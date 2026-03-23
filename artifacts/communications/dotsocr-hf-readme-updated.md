---
license: mit
base_model: rednote-hilab/dots.ocr
tags:
  - gguf
  - ocr
  - llama-cpp
  - vision
  - image-to-text
language:
  - en
  - zh
  - multilingual
---

# dots.ocr GGUF

GGUF conversions of [rednote-hilab/dots.ocr](https://huggingface.co/rednote-hilab/dots.ocr) for use with [llama.cpp](https://github.com/ggml-org/llama.cpp).

## Files

| File | Size | Description |
|---|---|---|
| Dots.Ocr-1.8B-Q8_0.gguf | 1.8 GB | Text model, 8-bit quantized |
| Dots.Ocr-1.8B-F16.gguf | 3.4 GB | Text model, float16 |
| mmproj-Dots.Ocr-F16.gguf | 2.4 GB | Vision encoder (mmproj), float16 |

## Update

On March 23, 2026, `mmproj-Dots.Ocr-F16.gguf` was regenerated from a corrected DotsOCR converter. The text GGUF files did not change. If you downloaded the `mmproj` earlier, refresh that file.

Current llama.cpp fork with DotsOCR support and the compatibility fix:

- [anthony-maio/llama.cpp](https://github.com/anthony-maio/llama.cpp)

## Architecture

dots.ocr = Qwen2 text backbone (1.7B params, 28 layers) + modified Qwen2-VL vision encoder (1.2B params, 42 layers).

Key differences from Qwen2-VL:
- Text model is standard Qwen2 with 1D RoPE (not M-RoPE)
- Vision uses RMSNorm, SiLU gated MLP, Conv2D patches, no attention bias
- 2D M-RoPE internal to vision encoder only

## Usage with llama.cpp

Requires a llama.cpp build with DotsOCR support. At the moment, use:

- [anthony-maio/llama.cpp](https://github.com/anthony-maio/llama.cpp)

Single-image example on Windows:

```powershell
llama-mtmd-cli.exe `
  -m .\Dots.Ocr-1.8B-Q8_0.gguf `
  --mmproj .\mmproj-Dots.Ocr-F16.gguf `
  --image .\page.png `
  -p "Extract all text from this image and preserve structure in markdown." `
  --ctx-size 131072 `
  -n 4096 `
  --temp 0 `
  --jinja
```

Equivalent server launch:

```powershell
llama-server.exe `
  -m .\Dots.Ocr-1.8B-Q8_0.gguf `
  --mmproj .\mmproj-Dots.Ocr-F16.gguf `
  --port 8111 `
  --host 0.0.0.0 `
  --ctx-size 131072 `
  -n 4096 `
  --temp 0 `
  --jinja
```
