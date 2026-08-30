#!/usr/bin/env python3
"""Render docs/hero-control-plane.png — GitHub-reliable README hero (matches the SVG layout)."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "hero-control-plane.png"

W, H = 1280, 560


def load_font(path: str, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def rr(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    radius: int,
    fill: tuple[int, int, int],
    outline: tuple[int, int, int] | None = None,
    width: int = 1,
) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def arrow(draw: ImageDraw.ImageDraw, x0: int, x1: int, y: int, color: tuple[int, int, int]) -> None:
    draw.line([(x0, y), (x1 - 12, y)], fill=color, width=3)
    draw.polygon([(x1, y), (x1 - 12, y - 8), (x1 - 12, y + 8)], fill=color)


def main() -> None:
    img = Image.new("RGB", (W, H), (12, 18, 32))
    draw = ImageDraw.Draw(img)

    # Soft center wash
    for y in range(140, 480):
        for x in range(300, 980):
            dx = (x - 640) / 420
            dy = (y - 300) / 180
            if dx * dx + dy * dy < 1.0:
                img.putpixel((x, y), (19, 32, 56))

    f_eyebrow = load_font("C:/Windows/Fonts/segoeuib.ttf", 13)
    f_title = load_font("C:/Windows/Fonts/segoeuib.ttf", 28)
    f_sub = load_font("C:/Windows/Fonts/segoeui.ttf", 15)
    f_col = load_font("C:/Windows/Fonts/segoeuib.ttf", 12)
    f_box = load_font("C:/Windows/Fonts/segoeuib.ttf", 15)
    f_chip = load_font("C:/Windows/Fonts/segoeuib.ttf", 13)
    f_small = load_font("C:/Windows/Fonts/segoeui.ttf", 12)
    f_mid = load_font("C:/Windows/Fonts/segoeuib.ttf", 20)
    f_listen = load_font("C:/Windows/Fonts/segoeuib.ttf", 14)
    f_foot = load_font("C:/Windows/Fonts/segoeui.ttf", 13)

    cyan = (56, 189, 248)
    text = (241, 245, 249)
    muted = (148, 163, 184)
    dim = (100, 116, 139)
    panel = (17, 24, 39)
    card = (11, 18, 32)
    stroke = (51, 65, 85)
    gate = (8, 47, 73)
    kill = (69, 10, 10)

    draw.rounded_rectangle((1, 1, W - 2, H - 2), radius=19, outline=(30, 42, 63), width=2)

    draw.text((W // 2, 48), "KIMSS CONTROL PLANE", font=f_eyebrow, fill=cyan, anchor="mm")
    draw.text((W // 2, 82), "Govern any agent before it reaches your models", font=f_title, fill=text, anchor="mm")
    draw.text(
        (W // 2, 112),
        "Dual-listener gateway  ·  OpenAPI contract  ·  A2A onboarding  ·  Article 12 audit",
        font=f_sub,
        fill=muted,
        anchor="mm",
    )

    # Left column
    rr(draw, (48, 148, 328, 488), 16, panel, stroke, 2)
    draw.text((188, 180), "AGENTS & SDKs", font=f_col, fill=cyan, anchor="mm")
    left_labels = ["OpenAI SDK", "Anthropic SDK", "Cascade / Cursor / A2A", "Python & Java clients"]
    for i, label in enumerate(left_labels):
        y = 200 + i * 60
        rr(draw, (72, y, 304, y + 48), 10, card, (71, 85, 105), 1)
        draw.text((188, y + 24), label, font=f_box, fill=(226, 232, 240), anchor="mm")
    draw.text((188, 462), "base_url → api.kimss.ai", font=f_small, fill=dim, anchor="mm")

    arrow(draw, 338, 404, 318, cyan)

    # Center
    rr(draw, (416, 148, 864, 488), 16, (15, 27, 45), cyan, 2)
    draw.text((640, 180), "GATEWAY SURFACE", font=f_col, fill=cyan, anchor="mm")
    draw.text((640, 208), "Identity · Policy · Audit", font=f_mid, fill=(248, 250, 252), anchor="mm")

    chips_top = [("Identity", 444, 562), ("Policy", 574, 692), ("Audit trail", 704, 840)]
    for label, x0, x1 in chips_top:
        rr(draw, (x0, 232, x1, 276), 8, gate, (14, 165, 233), 1)
        draw.text(((x0 + x1) // 2, 254), label, font=f_chip, fill=(224, 242, 254), anchor="mm")

    rr(draw, (444, 292, 626, 336), 8, gate, (14, 165, 233), 1)
    draw.text((535, 314), "Metering", font=f_chip, fill=(224, 242, 254), anchor="mm")
    rr(draw, (642, 292, 840, 336), 8, kill, (248, 113, 113), 1)
    draw.text((741, 314), "Kill switch", font=f_chip, fill=(254, 202, 202), anchor="mm")

    rr(draw, (444, 360, 836, 456), 12, card, stroke, 1)
    draw.text((640, 390), "DUAL LISTENERS", font=f_small, fill=muted, anchor="mm")
    draw.text((640, 418), "POST /v1/chat/completions", font=f_listen, fill=text, anchor="mm")
    draw.text((640, 440), "POST /v1/messages", font=f_listen, fill=text, anchor="mm")

    arrow(draw, 874, 940, 318, cyan)

    # Right column
    rr(draw, (952, 148, 1232, 488), 16, panel, stroke, 2)
    draw.text((1092, 180), "YOUR INFRASTRUCTURE", font=f_col, fill=cyan, anchor="mm")
    right_labels = ["Vaulted OpenAI", "Vaulted Anthropic", "Azure / custom models", "MCP tool servers"]
    for i, label in enumerate(right_labels):
        y = 200 + i * 60
        rr(draw, (976, y, 1208, y + 48), 10, card, (71, 85, 105), 1)
        draw.text((1092, y + 24), label, font=f_box, fill=(226, 232, 240), anchor="mm")
    draw.text((1092, 462), "BYOI — you hold the keys", font=f_small, fill=dim, anchor="mm")

    draw.text(
        (W // 2, 530),
        "Live API: api.kimss.ai  ·  Spec: openapi/control-plane.yaml  ·  A2A: AI_INTEGRATION.md",
        font=f_foot,
        fill=dim,
        anchor="mm",
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, "PNG", optimize=True)
    print(f"Wrote {OUT} ({OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
