from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path
from typing import Iterable

import numpy as np
from PIL import Image
from skimage import measure
from skimage.filters import threshold_otsu
import svgwrite
import vtracer


VALID_EXTENSIONS = {".jpg", ".jpeg", ".png"}
QUALITY_LEVELS = {
    "bassa": {"max_colors": 6, "min_area": 80},
    "media": {"max_colors": 12, "min_area": 45},
    "alta": {"max_colors": 20, "min_area": 20},
}

VTRACER_QUALITY_LEVELS = {
    "bassa": {
        "filter_speckle": 10,
        "color_precision": 8,
        "layer_difference": 24,
        "corner_threshold": 85,
        "length_threshold": 10,
        "max_iterations": 6,
        "splice_threshold": 45,
        "path_precision": 1,
    },
    "media": {
        "filter_speckle": 6,
        "color_precision": 6,
        "layer_difference": 16,
        "corner_threshold": 70,
        "length_threshold": 6,
        "max_iterations": 10,
        "splice_threshold": 30,
        "path_precision": 2,
    },
    "alta": {
        "filter_speckle": 3,
        "color_precision": 4,
        "layer_difference": 10,
        "corner_threshold": 55,
        "length_threshold": 4,
        "max_iterations": 14,
        "splice_threshold": 20,
        "path_precision": 3,
    },
}


def _clean_input_path(value: str) -> str:
    return value.strip().strip('"').strip("'")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Converte un'immagine JPG/PNG in SVG vettoriale (modalità colore o bianco/nero)."
    )
    parser.add_argument("--input", "-i", help="Percorso immagine di input (.jpg/.jpeg/.png)")
    parser.add_argument("--output", "-o", help="Percorso file output (.svg)")
    parser.add_argument(
        "--mode",
        "-m",
        choices=["color", "bw"],
        help="Modalità vettorizzazione: color (colori) o bw (bianco/nero)",
    )
    parser.add_argument(
        "--quality",
        "-q",
        choices=list(QUALITY_LEVELS.keys()),
        help="Qualità dettaglio: bassa, media, alta",
    )
    parser.add_argument(
        "--invert-bw",
        action="store_true",
        help="In modalità bw inverte il soggetto (utile se il soggetto è chiaro su fondo scuro)",
    )
    parser.add_argument(
        "--engine",
        choices=["vtracer", "legacy"],
        help="Motore vettorizzazione: vtracer (qualità migliore) o legacy (algoritmo interno)",
    )
    return parser.parse_args()


def prompt_if_missing(args: argparse.Namespace) -> argparse.Namespace:
    if not args.input:
        args.input = _clean_input_path(input("Percorso immagine input (.jpg/.jpeg/.png): "))

    if not args.mode:
        args.mode = input("Modalità [color/bw] (default: color): ").strip().lower() or "color"

    if args.mode not in {"color", "bw"}:
        raise ValueError("Modalità non valida. Usa 'color' o 'bw'.")

    if not args.quality:
        args.quality = (
            input("Qualità [bassa/media/alta] (default: media): ").strip().lower() or "media"
        )

    if args.quality not in QUALITY_LEVELS:
        raise ValueError("Qualità non valida. Usa 'bassa', 'media' o 'alta'.")

    if not args.output:
        input_path = Path(args.input)
        args.output = str(input_path.with_suffix(".svg"))
    else:
        args.output = _clean_input_path(args.output)

    if not args.engine:
        args.engine = (
            input("Engine [vtracer/legacy] (default: vtracer): ").strip().lower() or "vtracer"
        )

    if args.engine not in {"vtracer", "legacy"}:
        raise ValueError("Engine non valido. Usa 'vtracer' o 'legacy'.")

    return args


def validate_paths(input_path: Path, output_path: Path) -> None:
    if not input_path.exists():
        raise FileNotFoundError(f"File input non trovato: {input_path}")

    if input_path.suffix.lower() not in VALID_EXTENSIONS:
        raise ValueError("Formato input non supportato. Usa .jpg, .jpeg o .png")

    if output_path.suffix.lower() != ".svg":
        raise ValueError("Output supportato al momento: solo .svg")

    output_path.parent.mkdir(parents=True, exist_ok=True)


def _contours_to_paths(
    contours: Iterable[np.ndarray],
    min_area: float,
) -> list[str]:
    paths: list[str] = []
    for contour in contours:
        if contour.shape[0] < 3:
            continue

        points = [(float(c[1]), float(c[0])) for c in contour]
        area = polygon_area(points)
        if abs(area) < min_area:
            continue

        start_x, start_y = points[0]
        commands = [f"M {start_x:.2f},{start_y:.2f}"]
        commands.extend(f"L {x:.2f},{y:.2f}" for x, y in points[1:])
        commands.append("Z")
        paths.append(" ".join(commands))
    return paths


def polygon_area(points: list[tuple[float, float]]) -> float:
    x = np.array([p[0] for p in points])
    y = np.array([p[1] for p in points])
    return 0.5 * float(np.sum(x * np.roll(y, -1) - y * np.roll(x, -1)))


def vectorize_bw(img: Image.Image, output_svg: Path, min_area: float, invert: bool) -> None:
    rgba = np.asarray(img.convert("RGBA"), dtype=np.uint8)
    gray = np.asarray(img.convert("L"), dtype=np.float32)
    alpha = rgba[:, :, 3]
    visible = alpha > 0
    if not np.any(visible):
        raise ValueError("L'immagine è completamente trasparente: nessun contenuto da vettorizzare.")

    t = threshold_otsu(gray[visible])
    mask = gray < t
    if invert:
        mask = ~mask
    mask &= visible

    contours = measure.find_contours(mask.astype(float), 0.5)
    paths = _contours_to_paths(contours, min_area=min_area)

    drawing = svgwrite.Drawing(str(output_svg), size=(f"{img.width}px", f"{img.height}px"))
    opacity = float(np.mean(alpha[mask])) / 255.0 if np.any(mask) else 1.0
    for d in paths:
        drawing.add(drawing.path(
            d=d,
            fill="black",
            fill_opacity=max(0.0, min(opacity, 1.0)),
            stroke="none",
            fill_rule="evenodd",
        ))
    drawing.save()


def vectorize_color(img: Image.Image, output_svg: Path, max_colors: int, min_area: float) -> None:
    rgba = np.asarray(img.convert("RGBA"), dtype=np.uint8)
    alpha = rgba[:, :, 3]
    visible = alpha > 0
    if not np.any(visible):
        raise ValueError("L'immagine è completamente trasparente: nessun contenuto da vettorizzare.")

    reduced = img.convert("RGB").quantize(colors=max_colors, method=Image.Quantize.MEDIANCUT)
    reduced_rgb = reduced.convert("RGB")
    arr = np.asarray(reduced_rgb)

    flat = arr.reshape(-1, 3)
    colors, counts = np.unique(flat, axis=0, return_counts=True)
    order = np.argsort(-counts)

    drawing = svgwrite.Drawing(str(output_svg), size=(f"{img.width}px", f"{img.height}px"))

    for idx in order:
        color = colors[idx]
        mask = np.all(arr == color, axis=2) & visible
        if np.count_nonzero(mask) < min_area:
            continue
        contours = measure.find_contours(mask.astype(float), 0.5)
        paths = _contours_to_paths(contours, min_area=min_area)
        if not paths:
            continue

        hex_color = f"#{int(color[0]):02x}{int(color[1]):02x}{int(color[2]):02x}"
        opacity = float(np.mean(alpha[mask])) / 255.0
        for d in paths:
            drawing.add(
                drawing.path(
                    d=d,
                    fill=hex_color,
                    fill_opacity=max(0.0, min(opacity, 1.0)),
                    stroke="none",
                    fill_rule="evenodd",
                )
            )

    drawing.save()


def _prepare_inverted_bw_png(source_path: Path) -> Path:
    with Image.open(source_path) as img:
        rgba = img.convert("RGBA")
        arr = np.asarray(rgba, dtype=np.uint8)
        rgb = arr[:, :, :3]
        alpha = arr[:, :, 3]
        visible = alpha > 0
        rgb[visible] = 255 - rgb[visible]

        out = np.dstack([rgb, alpha])
        tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        tmp_path = Path(tmp.name)
        tmp.close()
        Image.fromarray(out, mode="RGBA").save(tmp_path)
        return tmp_path


def vectorize_with_vtracer(
    input_path: Path,
    output_svg: Path,
    mode: str,
    quality: str,
    invert_bw: bool,
) -> None:
    cfg = VTRACER_QUALITY_LEVELS[quality]
    colormode = "binary" if mode == "bw" else "color"

    path_for_trace = input_path
    temp_file: Path | None = None
    try:
        if mode == "bw" and invert_bw:
            temp_file = _prepare_inverted_bw_png(input_path)
            path_for_trace = temp_file

        vtracer.convert_image_to_svg_py(
            str(path_for_trace),
            str(output_svg),
            colormode=colormode,
            hierarchical="stacked",
            mode="spline",
            **cfg,
        )
    finally:
        if temp_file and temp_file.exists():
            temp_file.unlink(missing_ok=True)


def main() -> int:
    try:
        args = prompt_if_missing(parse_args())
        input_path = Path(args.input).expanduser().resolve()
        output_path = Path(args.output).expanduser().resolve()
        validate_paths(input_path, output_path)

        if args.engine == "vtracer":
            vectorize_with_vtracer(
                input_path=input_path,
                output_svg=output_path,
                mode=args.mode,
                quality=args.quality,
                invert_bw=args.invert_bw,
            )
        else:
            cfg = QUALITY_LEVELS[args.quality]
            with Image.open(input_path) as img:
                if args.mode == "bw":
                    vectorize_bw(
                        img,
                        output_svg=output_path,
                        min_area=cfg["min_area"],
                        invert=args.invert_bw,
                    )
                else:
                    vectorize_color(
                        img,
                        output_svg=output_path,
                        max_colors=cfg["max_colors"],
                        min_area=cfg["min_area"],
                    )

        print(f"✅ SVG generato con successo: {output_path}")
        return 0
    except Exception as exc:
        print(f"❌ Errore: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
