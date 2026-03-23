Subject: DotsOCR test steps and the correct command

Hi Sammy,

I think there are two separate issues in the test:

1. The executable for single-image OCR should be `llama-mtmd-cli.exe`, not `llama-cli.exe`.
2. The `mmproj-Dots.Ocr-F16.gguf` file in your AppData path may still be the older file.

I fixed the DotsOCR branch here:
https://github.com/anthony-maio/llama.cpp

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
