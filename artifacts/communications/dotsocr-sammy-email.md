Subject: DotsOCR test steps and the correct command

Hi Sammy,

I found the remaining runtime issue.

The `mmproj` file was already correct. The remaining bug was in the DotsOCR runtime graph in `llama.cpp`.

I fixed it here:
https://github.com/anthony-maio/llama.cpp

Latest fix commit:
https://github.com/anthony-maio/llama.cpp/commit/7d6933756

The problem was that DotsOCR patch embeddings were being handled with the wrong layout before the first norm/projection step. That caused the `ggml_can_repeat` assertion during projector warmup.

Please rebuild again from the latest `master` and test with the same command.

For reference, this is what I verified locally after the fix:

- projector warmup passed
- model entered chat mode successfully

Your command format was already basically correct after switching to `llama-mtmd-cli.exe`.

There are still two practical points to keep:

1. The executable for single-image OCR should be `llama-mtmd-cli.exe`, not `llama-cli.exe`.
2. The `mmproj-Dots.Ocr-F16.gguf` file in your AppData path may still be the older file.

I also refreshed the corrected `mmproj` file here:
https://huggingface.co/anthonym21/dots.ocr-GGUF

For a quick test, please do this:

1. Re-download `mmproj-Dots.Ocr-F16.gguf` from:
https://huggingface.co/anthonym21/dots.ocr-GGUF

2. Use `llama-mtmd-cli.exe`

3. Use a normal prompt. Do not manually add `<|im_start|>` / `<|vision_start|>` tokens.

Example command:

```cmd
llama-mtmd-cli.exe ^
  -m C:\L\python-3.13.5-embed-amd64\dotsocr-master1\weights\DotsOCR\dots.ocr-1.8B-Q8_0.gguf ^
  --mmproj C:\Users\Administrator\AppData\Roaming\club.aimt.dotsocr.runner\models\mmproj-Dots.Ocr-F16.gguf ^
  --image C:\L\100-1-840x840.jpg ^
  --ctx-size 4096 ^
  -n 2048 ^
  --temp 0 ^
  --jinja ^
  -p "Extract all text from this image and preserve structure in markdown."
```

If you want the simplest possible test, this also works because it downloads the model and `mmproj` from Hugging Face automatically:

```cmd
llama-mtmd-cli.exe ^
  -hf anthonym21/dots.ocr-GGUF:q8_0 ^
  --image C:\L\100-1-840x840.jpg ^
  --ctx-size 4096 ^
  -n 2048 ^
  --temp 0 ^
  --jinja ^
  -p "Extract all text from this image and preserve structure in markdown."
```

If it still fails, please send me:

- the exact command you ran
- the first 30 lines of output
- the SHA256 of the `mmproj` file

You can get the SHA256 with:

```cmd
certutil -hashfile C:\Users\Administrator\AppData\Roaming\club.aimt.dotsocr.runner\models\mmproj-Dots.Ocr-F16.gguf SHA256
```

The corrected `mmproj` SHA256 should be:

`B65A1DB58DB75F6D1AE900A4CB80772C4C0FABFAF261439E4C4AB965F6970DE8`

For `dots.mocr`, it should use the same DotsOCR code path, but it needs its own new text GGUF and its own new `mmproj`.

Best,
Anthony
