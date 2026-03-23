I fixed the DotsOCR support in my `llama.cpp` branch.

The bug was in the vision-side FFN tensor mapping during conversion. DotsOCR does not use the same vision MLP layout as Qwen2-VL, and the `fc2` / `fc3` tensors were mapped in the wrong order. That led to a shape mismatch during warmup and surfaced as a `ggml_can_repeat` assertion.

The practical result:

- The DotsOCR vision mapping is corrected in the converter.
- Existing text GGUFs are still fine.
- The `mmproj` artifact has been refreshed on Hugging Face.
- If you want to use it now, rebuild `llama-server` from the updated branch.

Updated repo:
https://huggingface.co/anthonym21/dots.ocr-GGUF

If you are using the DotsOCR GGUFs, the clean path is:

1. update to the latest branch,
2. keep the text GGUFs,
3. pull the updated `mmproj` from Hugging Face.

Multimodal integrations are mostly about contracts between the source checkpoint, the converter, the GGUF metadata, and the runtime graph. If one tensor mapping is wrong, the failure often shows up far away from the actual mistake.
