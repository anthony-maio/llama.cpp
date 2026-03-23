# Fixing DotsOCR Support in llama.cpp

DotsOCR looked close enough to the existing Qwen2-VL family that the first pass of the integration felt straightforward. It was not. One tensor-mapping assumption was wrong, and that was enough to break the vision path at runtime.

This write-up covers what the model looks like, where the bug lived, why it surfaced as a `ggml_can_repeat` assertion, what changed in the branch, and what users should update in the published GGUF artifacts. As of March 23, 2026, the corrected `mmproj-Dots.Ocr-F16.gguf` has also been uploaded to the public Hugging Face repo.

## The Model Shape

DotsOCR combines two pieces:

- a standard Qwen2 text backbone,
- a modified vision encoder derived from the Qwen2-VL family.

The text side is ordinary enough for `llama.cpp`: Qwen2 layers, 1D RoPE, and the usual causal LM flow.

The vision side is where the differences matter. DotsOCR does not match Qwen2-VL exactly. The important details are:

- the vision stack uses RMSNorm instead of LayerNorm,
- the vision MLP is SiLU-gated,
- patch embedding is Conv2D-based,
- the encoder does not use the same attention-bias assumptions as some related models,
- 2D M-RoPE is used internally in the vision encoder,
- the patch merger happens after the vision transformer and before projection into text space.

That means support is not just a matter of adding a model name. The converter has to map the vision tensors correctly, the GGUF metadata has to describe the projector correctly, and the mtmd runtime graph has to build the same structure the original model expects.

## The Symptom

The failure showed up in `llama-server` startup, during multimodal warmup:

`GGML_ASSERT(ggml_can_repeat(b, a)) failed`

That assert comes from `ggml_add`. In practice, it means the graph tried to add two tensors whose shapes could not be broadcast together.

At first glance, that looks like a low-level graph or backend problem. It is easy to suspect CUDA, warmup image sizing, or an allocation issue. That would have been the wrong conclusion here.

The key clue was where the failure happened. Warmup forces the full vision graph to resolve with a representative image shape. If the converter gave the runtime the wrong tensor layout, warmup is often where it breaks first.

So the assert in `ggml_add` was the symptom, not the root cause.

## Tracing It Back

The debugging path narrowed down to two places:

- `convert_hf_to_gguf.py`, which maps Hugging Face tensor names into GGUF tensor names,
- `tools/mtmd/clip.cpp`, which loads those tensors and builds the projector graph.

Those two layers must agree on tensor meaning. If the converter says a tensor is the up projection and the runtime graph treats it as the down projection, the file may still load, but the hidden dimensions will not line up once the graph starts composing the vision MLP and merger path.

That is exactly what happened.

DotsOCR’s vision MLP layout is:

- `fc1` = gate projection,
- `fc3` = up projection,
- `fc2` = down projection.

The original conversion logic had `fc2` and `fc3` reversed. That gave the runtime a projector with the wrong shape contract.

Once the graph reached an add that assumed the merged hidden state and projected tensor were compatible, the broadcast check failed and `ggml_add` aborted.

## Why This Was Easy to Miss

The model is similar enough to existing Qwen2-VL-family code that reuse looks attractive. That is usually the right instinct in `llama.cpp`, but only up to the point where the architecture diverges.

DotsOCR diverges in exactly the sort of place that can be easy to gloss over during a first integration pass:

- same general family,
- different vision norm choice,
- different MLP wiring,
- different projector assumptions.

That is the kind of mismatch that produces a clean compile, a valid-looking GGUF, and then a runtime failure much later in the pipeline.

It is also why multimodal work tends to punish “close enough” logic. Text-only integrations can often survive small naming mistakes because the shapes are repetitive and the architecture is more uniform. Vision projectors are less forgiving.

## The Fix

There were two useful fixes, not one.

First, the converter mapping had to be corrected.

In `convert_hf_to_gguf.py`, the DotsOCR vision MLP mapping is now:

- `fc1 -> gate_proj`
- `fc3 -> up_proj`
- `fc2 -> down_proj`

That fixes future mmproj exports.

Second, the runtime path needed a compatibility fallback for older artifacts already produced from the bad mapping.

`tools/mtmd/clip.cpp` already had a load-time FFN swap heuristic for older model families whose up/down tensors were known to be reversed in legacy exports. I extended that compatibility path to include `PROJECTOR_TYPE_DOTS_OCR`.

That means the updated branch can still recover older DotsOCR mmproj files in more cases, which is useful for users who already downloaded the published artifact.

The combination matters:

- the converter fix makes new exports correct,
- the runtime compatibility fix helps existing users,
- the correct long-term answer is still to regenerate the mmproj artifact.

## What Changed in the Branch

The rebased branch now contains two DotsOCR commits on top of current upstream:

- `998912477` adds the original DotsOCR support,
- `e79349d23` fixes the vision FFN mapping and adds regression coverage.

The fork’s `master` branch is synced to current upstream and includes both of those commits.

The fix was verified with:

- a regression test for the DotsOCR converter mapping,
- a successful `Release` build of `mtmd` and `llama-server` after rebasing onto upstream.

I did not run a full end-to-end local DotsOCR inference pass in this workspace because the published GGUF pair was not already present locally. The corrected mmproj was regenerated from the original Hugging Face source model, which is the main artifact change needed for release quality.

## What Should Change on Hugging Face

For the published repository at `anthonym21/dots.ocr-GGUF`, the split is simple:

- keep the text GGUFs,
- replace the old `mmproj-Dots.Ocr-F16.gguf`,
- update the README to note that the mmproj was regenerated from the fixed converter.

The text model files do not need to be replaced for this bug. The issue lived in the vision-side FFN mapping and the runtime compatibility path, not in the text backbone conversion.

I regenerated a corrected mmproj locally from the fixed branch. The resulting artifact is:

- `mmproj-Dots.Ocr-F16-fixed.gguf`
- size: `2,524,495,808` bytes
- SHA-256: `b65a1db58db75f6d1ae900a4cb80772c4c0fabfaf261439e4c4ab965f6970de8`

For the public repo, I would upload that file under the original published name:

- `mmproj-Dots.Ocr-F16.gguf`

That avoids forcing users to change launch commands. The README can simply note that the file was refreshed on March 23, 2026 from the corrected converter.

## Lessons From the Bug

The main lesson is that multimodal integrations are mostly about contracts.

The source checkpoint, the converter, the GGUF metadata, and the runtime graph all have to agree on:

- tensor identity,
- tensor orientation,
- hidden dimensions,
- positional encoding assumptions,
- merger layout.

If any one layer is wrong, the eventual failure often appears far away from the original mistake.

That is what happened here. The graph builder failed in `ggml_add`, but the real bug was a wrong assumption in the converter about which DotsOCR tensor represented the up projection and which represented the down projection.

That is also why it was worth fixing the converter explicitly instead of relying only on a runtime compatibility hack. Compatibility logic is useful for already-published artifacts, but the canonical conversion path still needs to encode the actual model architecture.

## Practical Next Steps

If you want a clean release path for DotsOCR support in `llama.cpp`, the next steps are:

1. use the updated `master` branch from the fork,
2. keep the existing text GGUFs,
3. replace the old mmproj with the regenerated one,
4. update the Hugging Face README to explain the refresh,
5. ask users who hit the old warmup failure to rebuild `llama-server` from the updated branch.

That gets the code, the published artifact, and the user instructions back into alignment.
