#!/usr/bin/env python3
"""Render docs/social-preview.png from the SVG layout (Pillow)."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "social-preview.png"

W, H = 1280, 640


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def blend(c1: tuple[int, int, int], c2: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return tuple(int(lerp(c1[i], c2[i], t)) for i in range(3))


def load_fonts() -> dict[str, ImageFont.FreeTypeFont | ImageFont.ImageFont]:
    candidates = {
        "title": ("C:/Windows/Fonts/segoeuib.ttf", 40),
        "sub": ("C:/Windows/Fonts/segoeui.ttf", 20),
        "box": ("C:/Windows/Fonts/segoeuib.ttf", 18),
        "box_sub": ("C:/Windows/Fonts/segoeui.ttf", 13),
        "center": ("C:/Windows/Fonts/segoeuib.ttf", 22),
        "chips": ("C:/Windows/Fonts/segoeui.ttf", 14),
        "footer": ("C:/Windows/Fonts/segoeui.ttf", 15),
    }
    fonts: dict[str, ImageFont.FreeTypeFont | ImageFont.ImageFont] = {}
    default = ImageFont.load_default()
    for key, (path, size) in candidates.items():
        try:
            fonts[key] = ImageFont.truetype(path, size)
        except OSError:
            fonts[key] = default
    return fonts


def draw_arrow(draw: ImageDraw.ImageDraw, x: int, y1: int, y2: int) -> None:
    draw.line([(x, y1), (x, y2)], fill=(139, 92, 246), width=3)
    draw.polygon([(x, y2 + 10), (x - 8, y2 - 6), (x + 8, y2 - 6)], fill=(139, 92, 246))


def main() -> None:
    img = Image.new("RGB", (W, H))
    px = img.load()
    c0, c1 = (11, 6, 24), (18, 10, 42)
    for y in range(H):
        for x in range(W):
            t = (x / W) * 0.35 + (y / H) * 0.65
            px[x, y] = blend(c0, c1, t)

    draw = ImageDraw.Draw(img)
    fonts = load_fonts()

    draw.text((W // 2, 48), "KIMSS CONTROL PLANE", font=fonts["title"], fill=(238, 240, 250), anchor="mm")
    draw.text(
        (W // 2, 92),
        "Secure Enterprise Agent Gateway  ·  OpenAPI  ·  MCP RBAC  ·  A2A",
        font=fonts["sub"],
        fill=(165, 173, 200),
        anchor="mm",
    )

    # Left: agents
    lx0, ly0, lw, lh = 80, 150, 220, 280
    draw.rounded_rectangle((lx0, ly0, lx0 + lw, ly0 + lh), radius=16, fill=(28, 17, 64), outline=(75, 85, 111))
    draw.text((lx0 + 20, ly0 + 28), "AGENTS & SDKs", font=fonts["box_sub"], fill=(196, 181, 253))
    for i, label in enumerate(["OpenAI SDK", "Anthropic SDK", "Python / Java SDK", "MCP clients"]):
        y = ly0 + 70 + i * 52
        draw.rounded_rectangle((lx0 + 16, y, lx0 + lw - 16, y + 40), radius=10, fill=(26, 10, 51), outline=(75, 85, 111))
        draw.text((lx0 + lw // 2, y + 20), label, font=fonts["box"], fill=(238, 240, 250), anchor="mm")

    draw_arrow(draw, 310, 290, 350)

    # Center: control plane
    cx0, cy0, cw, ch = 330, 130, 620, 320
    draw.rounded_rectangle((cx0, cy0, cx0 + cw, cy0 + ch), radius=20, fill=(42, 31, 94), outline=(99, 102, 241), width=2)
    draw.text((W // 2, cy0 + 36), "Control Plane", font=fonts["center"], fill=(238, 240, 250), anchor="mm")
    draw.text(
        (W // 2, cy0 + 72),
        "Identity  ·  Policy  ·  Audit  ·  Metering  ·  Kill Switch",
        font=fonts["chips"],
        fill=(196, 181, 253),
        anchor="mm",
    )
    chips = ["OpenAPI spec", "MCP RBAC grants", "Governed requests", "Article 12 audit"]
    for i, chip in enumerate(chips):
        row, col = divmod(i, 2)
        bx = cx0 + 40 + col * 280
        by = cy0 + 110 + row * 56
        draw.rounded_rectangle((bx, by, bx + 260, by + 44), radius=12, fill=(26, 10, 51), outline=(139, 92, 246))
        draw.text((bx + 130, by + 22), chip, font=fonts["box"], fill=(238, 240, 250), anchor="mm")

    draw.text(
        (W // 2, cy0 + ch - 36),
        "Agent-to-agent integration without rewriting your data plane",
        font=fonts["box_sub"],
        fill=(165, 173, 200),
        anchor="mm",
    )

    draw_arrow(draw, 960, 290, 350)

    # Right: providers
    rx0, ry0, rw, rh = 980, 150, 220, 280
    draw.rounded_rectangle((rx0, ry0, rx0 + rw, ry0 + rh), radius=16, fill=(28, 17, 64), outline=(75, 85, 111))
    draw.text((rx0 + 20, ry0 + 28), "YOUR INFRA", font=fonts["box_sub"], fill=(196, 181, 253))
    for i, label in enumerate(["OpenAI", "Anthropic", "Azure / Foundry", "Custom models"]):
        y = ry0 + 70 + i * 52
        draw.rounded_rectangle((rx0 + 16, y, rx0 + rw - 16, y + 40), radius=10, fill=(26, 10, 51), outline=(75, 85, 111))
        draw.text((rx0 + rw // 2, y + 20), label, font=fonts["box"], fill=(238, 240, 250), anchor="mm")

    draw.text(
        (W // 2, 558),
        "github.com/kimss-ai/kimss-control-plane",
        font=fonts["footer"],
        fill=(107, 114, 128),
        anchor="mm",
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, "PNG", optimize=True)
    print(f"Wrote {OUT} ({OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
