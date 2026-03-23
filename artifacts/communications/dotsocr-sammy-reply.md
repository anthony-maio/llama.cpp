Hi Sammy,

I fixed the DotsOCR issue and pushed it here:
https://github.com/anthony-maio/llama.cpp

I also refreshed the public `mmproj` here:
https://huggingface.co/anthonym21/dots.ocr-GGUF

Single-image command with the updated build:

```powershell
llama-mtmd-cli.exe -hf anthonym21/dots.ocr-GGUF:q8_0 --image C:\path\to\image.png -p "Extract all text from this image and preserve structure in markdown." --ctx-size 131072 -n 4096 --temp 0 --jinja
```

If you already have the files locally, use:

```powershell
llama-mtmd-cli.exe -m C:\path\to\Dots.Ocr-1.8B-Q8_0.gguf --mmproj C:\path\to\mmproj-Dots.Ocr-F16.gguf --image C:\path\to\image.png -p "Extract all text from this image and preserve structure in markdown." --ctx-size 131072 -n 4096 --temp 0 --jinja
```

For `dots.mocr`, it looks compatible with the same DotsOCR code path, but yes, it needs its own new text GGUF and its own new `mmproj`.

Model:
https://huggingface.co/rednote-hilab/dots.mocr

Recommended conversion flow:

```powershell
git clone https://huggingface.co/rednote-hilab/dots.mocr
python convert_hf_to_gguf.py .\dots.mocr --outtype f16 --outfile .\Dots.Mocr-F16.gguf
python convert_hf_to_gguf.py .\dots.mocr --mmproj --outtype f16 --use-temp-file --outfile .\mmproj-Dots.Mocr-F16.gguf
```

If you rebuild and still hit an error, send me the new log.

Anthony
