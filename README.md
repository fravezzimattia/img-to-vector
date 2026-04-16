# img-to-svg

Script Python per convertire immagini **JPG/PNG** in **SVG vettoriale** usando `uv`.

Supporta due modalità:
- `color`: vettorizzazione a colori (con quantizzazione)
- `bw`: vettorizzazione bianco/nero (stile logo/sagoma)

Supporta due engine:
- `vtracer` (**default, consigliato**): qualità migliore e curve più pulite
- `legacy`: algoritmo interno precedente

## Requisiti

- Python 3.11+
- [uv](https://docs.astral.sh/uv/)

## Setup

```bash
uv sync
```

## Utilizzo

### 1) Modalità interattiva

```bash
uv run python img_to_vector.py
```

Lo script ti chiederà:
- file input (`.jpg`, `.jpeg`, `.png`)
- modalità (`color` o `bw`)
- qualità (`bassa`, `media`, `alta`)

### 2) Modalità CLI (non interattiva)

```bash
uv run python img_to_vector.py \
  --input /percorso/immagine.png \
  --output /percorso/output.svg \
  --mode color \
  --quality alta \
  --engine vtracer
```

Esempio bianco/nero con inversione:

```bash
uv run python img_to_vector.py \
  --input /percorso/logo.jpg \
  --mode bw \
  --quality media \
  --engine vtracer \
  --invert-bw
```

Esempio con engine legacy:

```bash
uv run python img_to_vector.py \
  --input /percorso/immagine.png \
  --mode color \
  --quality alta \
  --engine legacy
```

## Opzioni disponibili

```bash
uv run python img_to_vector.py --help
```

## Note

- Formato vettoriale supportato nello script: **SVG**.
- Se `--output` non è specificato, viene creato automaticamente un file `.svg` con lo stesso nome dell'immagine input.
- Le immagini PNG con **trasparenza** vengono gestite mantenendo l'area trasparente nello SVG (senza sfondo pieno).
- Per risultati migliori su immagini complesse/foto, usa `--engine vtracer --quality alta`.
