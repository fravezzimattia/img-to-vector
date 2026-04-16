# img-to-svg

A Python script to convert **JPG/PNG** images into **vector SVG** files using `uv`.

It supports two modes:
- `color`: color vectorization (with quantization)
- `bw`: black-and-white vectorization (logo/silhouette style)

It also supports two engines:
- `vtracer` (**default, recommended**): better quality and smoother curves
- `legacy`: previous internal algorithm

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/)

## Setup

```bash
uv sync
```

## Usage

### 1) Interactive mode

```bash
uv run python img_to_vector.py
```

The script will prompt you for:
- input file (`.jpg`, `.jpeg`, `.png`)
- mode (`color` or `bw`)
- quality (`bassa`, `media`, `alta`)

### 2) CLI mode (non-interactive)

```bash
uv run python img_to_vector.py \
  --input /path/to/image.png \
  --output /path/to/output.svg \
  --mode color \
  --quality alta \
  --engine vtracer
```

Black-and-white example with inversion:

```bash
uv run python img_to_vector.py \
  --input /path/to/logo.jpg \
  --mode bw \
  --quality media \
  --engine vtracer \
  --invert-bw
```

Example using the legacy engine:

```bash
uv run python img_to_vector.py \
  --input /path/to/image.png \
  --mode color \
  --quality alta \
  --engine legacy
```

## Available options

```bash
uv run python img_to_vector.py --help
```

## Notes

- Supported vector output format in this script: **SVG**.
- If `--output` is not specified, a `.svg` file is created automatically using the same name as the input image.
- PNG images with **transparency** are handled by preserving transparent areas in the SVG (no solid background).
- For better results on complex images/photos, use `--engine vtracer --quality alta`.

> Note: quality options are in Italian because they match the CLI choices:
> - `bassa` = low
> - `media` = medium
> - `alta` = high
