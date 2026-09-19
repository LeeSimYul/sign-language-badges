#!/usr/bin/env python3
"""Export the SVG badge masters in assets/svg/ to PNG and WebP raster badges.

빌드 산출물 생성기 / Raster badge exporter.

The SVG files are the single source of truth. Every raster badge in this
repository is produced from them by this script, so the exports never drift
from the vector masters.

For each badge the exporter can produce:

* two themes  - ``light`` renders the master as authored; ``dark`` inverts the
  achromatic parts (black ink becomes light, white faces become dark) so the
  badge stays legible on dark backgrounds (GitHub dark mode, Discord, VRChat
  night worlds) while the national flag colours are preserved untouched.
* two shapes  - ``wide`` keeps the master's aspect ratio, ``square`` centres
  the badge on a square canvas for Discord role icons and emoji.
* four sizes  - ``xs`` 160px, ``sm`` 320px, ``md`` 640px, ``lg`` 1280px wide.
  Any custom pixel width may be passed instead of a preset name.
* two formats - ``png`` and ``webp`` (lossless by default).

Usage
-----
    pip install cairosvg Pillow

    python scripts/generate_badges.py                       # full default matrix
    python scripts/generate_badges.py --only KSL,ASL        # just two badges
    python scripts/generate_badges.py --themes dark --sizes 512
    python scripts/generate_badges.py --shapes square --sizes sm --formats png
    python scripts/generate_badges.py --dry-run             # print, write nothing

Outputs land in ``assets/export/<theme>/<shape>/<size>/<NAME>.<ext>`` next to a
``manifest.json`` describing the run.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

try:
    import cairosvg
except ImportError:  # pragma: no cover - dependency hint
    sys.exit(
        "cairosvg is required.\n"
        "  pip install cairosvg Pillow\n"
        "cairosvg also needs the native Cairo library "
        "(apt: libcairo2, brew: cairo)."
    )

try:
    from PIL import Image, ImageColor
except ImportError:  # pragma: no cover - dependency hint
    sys.exit("Pillow is required.\n  pip install cairosvg Pillow")


REPO_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_SVG_DIR = REPO_ROOT / "assets" / "svg"
DEFAULT_OUT_DIR = REPO_ROOT / "assets" / "export"

#: Named width presets, in pixels.
SIZE_PRESETS: dict[str, int] = {"xs": 160, "sm": 320, "md": 640, "lg": 1280}

THEMES = ("light", "dark")
SHAPES = ("wide", "square")
FORMATS = ("png", "webp")

DEFAULT_SIZES = ("xs", "sm", "md", "lg")
DEFAULT_THEMES = THEMES
DEFAULT_SHAPES = ("wide",)
DEFAULT_FORMATS = FORMATS

#: Dark-theme replacement for the badge's near-black ink (keylines, letters).
DEFAULT_DARK_INK = "#f5f5f5"

#: Dark-theme replacement for near-white "paper" areas (letter faces, inner
#: keylines). Matches GitHub's dark canvas so the badge sits flush in a README.
DEFAULT_DARK_PAPER = "#12151c"

#: Relative luminance at or below which an achromatic colour counts as ink.
DEFAULT_INK_THRESHOLD = 0.08

#: Relative luminance at or above which an achromatic colour counts as paper.
DEFAULT_PAPER_THRESHOLD = 0.90

#: Chroma above which a colour is treated as a national/brand colour and is
#: never recoloured. The reds, blues and yellows of the flags sit far above it;
#: blacks, whites and neutral greys sit at or near zero.
DEFAULT_CHROMA_THRESHOLD = 0.12

#: Colour-bearing SVG attributes. ``fill="none"`` and ``fill="url(#id)"`` are
#: skipped by :func:`classify`, so gradients and flag fills survive untouched.
COLOUR_ATTRS = ("fill", "stroke", "stop-color", "flood-color", "color")

_ATTR_RE = re.compile(
    r'\b(' + "|".join(COLOUR_ATTRS) + r')\s*=\s*"([^"]*)"',
    re.IGNORECASE,
)
_STYLE_RE = re.compile(
    r'\b(' + "|".join(COLOUR_ATTRS) + r')\s*:\s*([^;"\'}]+)',
    re.IGNORECASE,
)
_SVG_OPEN_RE = re.compile(r"<svg\b[^>]*>", re.IGNORECASE)

NAMED_COLOURS = {"black": "#000000", "white": "#ffffff"}


# --------------------------------------------------------------------------- #
# colour helpers
# --------------------------------------------------------------------------- #
def _parse_hex(value: str) -> tuple[int, int, int] | None:
    """Return the RGB triple for a hex or simple named colour, else ``None``."""
    token = value.strip().lower()
    token = NAMED_COLOURS.get(token, token)
    if not token.startswith("#"):
        return None
    digits = token[1:]
    if len(digits) == 3:
        digits = "".join(c * 2 for c in digits)
    if len(digits) != 6 or any(c not in "0123456789abcdef" for c in digits):
        return None
    return tuple(int(digits[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def _luminance(rgb: tuple[int, int, int]) -> float:
    """Perceived relative luminance in the 0.0 - 1.0 range."""
    r, g, b = (channel / 255 for channel in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _chroma(rgb: tuple[int, int, int]) -> float:
    """Colourfulness in the 0.0 - 1.0 range; 0.0 for any shade of grey."""
    return (max(rgb) - min(rgb)) / 255


@dataclass(frozen=True)
class DarkPalette:
    """How the dark theme repaints the achromatic parts of a badge."""

    ink: str = DEFAULT_DARK_INK
    paper: str = DEFAULT_DARK_PAPER
    ink_threshold: float = DEFAULT_INK_THRESHOLD
    paper_threshold: float = DEFAULT_PAPER_THRESHOLD
    chroma_threshold: float = DEFAULT_CHROMA_THRESHOLD


def classify(value: str, palette: DarkPalette) -> str | None:
    """Return the dark-theme colour for ``value``, or ``None`` to keep it.

    Only greys are repainted. Anything colourful - the red and blue of the
    Korean flag, the navy and red of the French one, the red disc of the
    Japanese one - is left exactly as the designer drew it, as are
    ``fill="none"`` and ``url(#gradient)`` references, which do not parse as
    colours at all.
    """
    rgb = _parse_hex(value)
    if rgb is None or _chroma(rgb) > palette.chroma_threshold:
        return None
    luminance = _luminance(rgb)
    if luminance <= palette.ink_threshold:
        return palette.ink
    if luminance >= palette.paper_threshold:
        return palette.paper
    return None


# --------------------------------------------------------------------------- #
# SVG preparation
# --------------------------------------------------------------------------- #
def recolour_for_dark(svg: str, palette: DarkPalette) -> str:
    """Repaint the achromatic parts of ``svg`` for a dark background.

    Three things are needed for a faithful dark variant:

    1. every near-black ``fill``/``stroke``/``stop-color`` becomes the light
       ink, so the keylines stay visible,
    2. every near-white face becomes the dark paper colour, so letter faces do
       not melt into the keylines that just turned white, and
    3. the root ``<svg>`` gains ``fill="<ink>"``, because paths that declare no
       fill at all default to black and would otherwise disappear.
    """

    def swap_attr(match: re.Match[str]) -> str:
        name, value = match.group(1), match.group(2)
        replacement = classify(value, palette)
        return match.group(0) if replacement is None else f'{name}="{replacement}"'

    def swap_style(match: re.Match[str]) -> str:
        name, value = match.group(1), match.group(2)
        replacement = classify(value, palette)
        return match.group(0) if replacement is None else f"{name}:{replacement}"

    svg = _ATTR_RE.sub(swap_attr, svg)
    svg = _STYLE_RE.sub(swap_style, svg)

    open_tag = _SVG_OPEN_RE.search(svg)
    if open_tag and not re.search(r'\bfill\s*=', open_tag.group(0), re.IGNORECASE):
        patched = open_tag.group(0)[:-1].rstrip() + f' fill="{palette.ink}">'
        svg = svg[: open_tag.start()] + patched + svg[open_tag.end() :]
    return svg


def prepare_svg(source: Path, theme: str, palette: DarkPalette) -> bytes:
    """Read ``source`` and return the SVG bytes to rasterise for ``theme``."""
    svg = source.read_text(encoding="utf-8")
    if theme == "dark":
        svg = recolour_for_dark(svg, palette)
    return svg.encode("utf-8")


# --------------------------------------------------------------------------- #
# rasterising
# --------------------------------------------------------------------------- #
def rasterise(svg_bytes: bytes, width: int, source_dir: Path) -> Image.Image:
    """Render ``svg_bytes`` to an RGBA image ``width`` pixels wide."""
    png_bytes = cairosvg.svg2png(
        bytestring=svg_bytes,
        output_width=width,
        url=source_dir.as_uri() + "/",
    )
    return Image.open(BytesIO(png_bytes)).convert("RGBA")


def to_square(image: Image.Image) -> Image.Image:
    """Centre ``image`` on a transparent square canvas of its longest side."""
    side = max(image.size)
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    canvas.paste(
        image,
        ((side - image.width) // 2, (side - image.height) // 2),
        image,
    )
    return canvas


def flatten(image: Image.Image, background: str) -> Image.Image:
    """Composite ``image`` over a solid ``background`` colour."""
    rgba = ImageColor.getcolor(background, "RGBA")
    canvas = Image.new("RGBA", image.size, rgba)
    canvas.alpha_composite(image)
    return canvas


def save(image: Image.Image, target: Path, fmt: str, webp_quality: int | None) -> None:
    """Write ``image`` to ``target`` in ``fmt``."""
    target.parent.mkdir(parents=True, exist_ok=True)
    if fmt == "png":
        image.save(target, format="PNG", optimize=True)
    elif fmt == "webp":
        if webp_quality is None:
            image.save(target, format="WEBP", lossless=True, method=6)
        else:
            image.save(target, format="WEBP", quality=webp_quality, method=6)
    else:  # pragma: no cover - guarded by argparse choices
        raise ValueError(f"unsupported format: {fmt}")


# --------------------------------------------------------------------------- #
# CLI plumbing
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class SizeSpec:
    """A named output width, e.g. ``md`` -> 640px."""

    label: str
    width: int


def display_path(path: Path) -> str:
    """Repo-relative path for anything inside the repo, absolute otherwise."""
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path.resolve())


def parse_list(raw: str) -> list[str]:
    """Split a comma separated CLI value into clean tokens."""
    return [item.strip() for item in raw.split(",") if item.strip()]


def resolve_sizes(tokens: list[str]) -> list[SizeSpec]:
    """Turn ``['md', '512']`` into size specs, preserving order."""
    sizes: list[SizeSpec] = []
    for token in tokens:
        key = token.lower()
        if key in SIZE_PRESETS:
            sizes.append(SizeSpec(key, SIZE_PRESETS[key]))
            continue
        if not key.isdigit() or int(key) <= 0:
            raise SystemExit(
                f"unknown size {token!r}; use a preset "
                f"({', '.join(SIZE_PRESETS)}) or a positive pixel width"
            )
        sizes.append(SizeSpec(f"{key}px", int(key)))
    return sizes


def validate_choices(values: list[str], allowed: tuple[str, ...], flag: str) -> list[str]:
    """Reject unknown ``--themes``/``--shapes``/``--formats`` values."""
    lowered = [value.lower() for value in values]
    unknown = [value for value in lowered if value not in allowed]
    if unknown:
        raise SystemExit(
            f"unknown {flag} value(s) {', '.join(unknown)}; "
            f"choose from {', '.join(allowed)}"
        )
    return lowered


def discover_sources(svg_dir: Path, only: list[str]) -> list[Path]:
    """Return the SVG masters to export, honouring ``--only``."""
    if not svg_dir.is_dir():
        raise SystemExit(f"SVG directory not found: {svg_dir}")
    sources = sorted(svg_dir.glob("*.svg"), key=lambda p: p.stem.lower())
    if not sources:
        raise SystemExit(f"no .svg files in {svg_dir}")
    if not only:
        return sources
    wanted = {name.lower() for name in only}
    selected = [path for path in sources if path.stem.lower() in wanted]
    missing = wanted - {path.stem.lower() for path in selected}
    if missing:
        available = ", ".join(path.stem for path in sources)
        raise SystemExit(
            f"no SVG master for {', '.join(sorted(missing))}; available: {available}"
        )
    return selected


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Export assets/svg/*.svg to PNG and WebP badges.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--svg-dir", type=Path, default=DEFAULT_SVG_DIR,
                        help="directory holding the SVG masters")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR,
                        help="directory the exports are written to")
    parser.add_argument("--only", default="",
                        help="comma separated badge names, e.g. KSL,ASL")
    parser.add_argument("--themes", default=",".join(DEFAULT_THEMES),
                        help=f"comma separated: {', '.join(THEMES)}")
    parser.add_argument("--shapes", default=",".join(DEFAULT_SHAPES),
                        help=f"comma separated: {', '.join(SHAPES)}")
    parser.add_argument("--sizes", default=",".join(DEFAULT_SIZES),
                        help="comma separated presets or pixel widths")
    parser.add_argument("--formats", default=",".join(DEFAULT_FORMATS),
                        help=f"comma separated: {', '.join(FORMATS)}")
    parser.add_argument("--background", default=None,
                        help="flatten onto this colour instead of transparency")
    parser.add_argument("--dark-ink", default=DEFAULT_DARK_INK,
                        help="colour the dark theme paints near-black ink in")
    parser.add_argument("--dark-paper", default=DEFAULT_DARK_PAPER,
                        help="colour the dark theme paints near-white faces in")
    parser.add_argument("--ink-threshold", type=float, default=DEFAULT_INK_THRESHOLD,
                        help="luminance at or below which a grey counts as ink")
    parser.add_argument("--paper-threshold", type=float, default=DEFAULT_PAPER_THRESHOLD,
                        help="luminance at or above which a grey counts as paper")
    parser.add_argument("--chroma-threshold", type=float, default=DEFAULT_CHROMA_THRESHOLD,
                        help="chroma above which a colour is kept as a flag colour")
    parser.add_argument("--webp-quality", type=int, default=None,
                        help="lossy WebP quality 1-100 (default: lossless)")
    parser.add_argument("--clean", action="store_true",
                        help="delete the output directory before exporting")
    parser.add_argument("--no-manifest", action="store_true",
                        help="skip writing manifest.json")
    parser.add_argument("--dry-run", action="store_true",
                        help="list the files that would be written")
    parser.add_argument("-q", "--quiet", action="store_true",
                        help="only report the summary line")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.webp_quality is not None and not 1 <= args.webp_quality <= 100:
        raise SystemExit("--webp-quality must be between 1 and 100")
    for flag, value in (
        ("--ink-threshold", args.ink_threshold),
        ("--paper-threshold", args.paper_threshold),
        ("--chroma-threshold", args.chroma_threshold),
    ):
        if not 0.0 <= value <= 1.0:
            raise SystemExit(f"{flag} must be between 0.0 and 1.0")
    if args.ink_threshold >= args.paper_threshold:
        raise SystemExit("--ink-threshold must be lower than --paper-threshold")

    palette = DarkPalette(
        ink=args.dark_ink,
        paper=args.dark_paper,
        ink_threshold=args.ink_threshold,
        paper_threshold=args.paper_threshold,
        chroma_threshold=args.chroma_threshold,
    )

    themes = validate_choices(parse_list(args.themes), THEMES, "--themes")
    shapes = validate_choices(parse_list(args.shapes), SHAPES, "--shapes")
    formats = validate_choices(parse_list(args.formats), FORMATS, "--formats")
    sizes = resolve_sizes(parse_list(args.sizes))
    if not (themes and shapes and formats and sizes):
        raise SystemExit("--themes, --shapes, --sizes and --formats must be non-empty")

    svg_dir = args.svg_dir.resolve()
    out_dir = args.out_dir.resolve()
    sources = discover_sources(svg_dir, parse_list(args.only))

    if args.clean and out_dir.exists() and not args.dry_run:
        shutil.rmtree(out_dir)

    records: list[dict[str, object]] = []
    for source in sources:
        for theme in themes:
            svg_bytes = prepare_svg(source, theme, palette)
            for size in sizes:
                base = rasterise(svg_bytes, size.width, svg_dir)
                for shape in shapes:
                    image = to_square(base) if shape == "square" else base
                    if args.background:
                        image = flatten(image, args.background)
                    for fmt in formats:
                        target = out_dir / theme / shape / size.label / f"{source.stem}.{fmt}"
                        if not args.dry_run:
                            save(image, target, fmt, args.webp_quality)
                        rel = display_path(target)
                        if not args.quiet:
                            prefix = "would write" if args.dry_run else "wrote"
                            print(f"{prefix} {rel} ({image.width}x{image.height})")
                        records.append(
                            {
                                "badge": source.stem,
                                "source": display_path(source),
                                "theme": theme,
                                "shape": shape,
                                "size": size.label,
                                "width": image.width,
                                "height": image.height,
                                "format": fmt,
                                "path": rel,
                            }
                        )

    if not args.no_manifest and not args.dry_run:
        manifest = out_dir / "manifest.json"
        manifest.parent.mkdir(parents=True, exist_ok=True)
        manifest.write_text(
            json.dumps(
                {
                    "generator": "scripts/generate_badges.py",
                    "source_dir": display_path(svg_dir),
                    "themes": themes,
                    "shapes": shapes,
                    "sizes": [{"label": s.label, "width": s.width} for s in sizes],
                    "formats": formats,
                    "dark_ink": palette.ink,
                    "dark_paper": palette.paper,
                    "badges": [source.stem for source in sources],
                    "files": records,
                },
                indent=2,
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )
        if not args.quiet:
            print(f"wrote {display_path(manifest)}")

    verb = "would export" if args.dry_run else "exported"
    print(
        f"{verb} {len(records)} file(s) from {len(sources)} badge(s) "
        f"-> {display_path(out_dir)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
