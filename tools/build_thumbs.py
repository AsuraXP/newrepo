"""Build final thumbnails from the generated base art.

Style lock: one big cartoon character + ONE huge hand-lettered electric-yellow
headline (matching the reference channel's shouty single headline), thick black
ink outline, warm cream paper. Text is composited with PIL (never AI-generated)
so the spelling is exact: "WHY WE COOK".

Outputs:
  thumbnail.jpg        1280x720  (16:9 YouTube thumbnail)
  thumb_portrait.png   1080x1920 (9:16 portrait / Shorts thumbnail)
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THUMBS = os.path.join(HERE, "thumbs")
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
YELLOW = (255, 214, 0)     # electric yellow #FFD700
INK = (26, 26, 26)         # ink black
PAPER = (247, 240, 221)    # warm cream


def _fit_font(draw, text, max_w, max_h, start=260):
    """Largest bold font size so `text` fits inside max_w x max_h."""
    size = start
    while size > 8:
        f = ImageFont.truetype(FONT, size)
        bb = draw.textbbox((0, 0), text, font=f, stroke_width=0)
        w, h = bb[2] - bb[0], bb[3] - bb[1]
        if w <= max_w and h <= max_h:
            return f, w, h
        size -= 4
    f = ImageFont.truetype(FONT, size)
    bb = draw.textbbox((0, 0), text, font=f)
    return f, bb[2] - bb[0], bb[3] - bb[1]


def _headline_layer(lines, out_w, band_h, stroke):
    """Render one or more centered yellow lines with a thick black ink outline
    onto a transparent layer of width out_w and height band_h, slightly rotated
    for a hand-drawn feel. Returns an RGBA image."""
    pad = 80
    layer = Image.new("RGBA", (out_w + 2 * pad, band_h + 2 * pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    max_w = out_w - 40
    # pick a common size that fits the longest line
    probe = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    size = 300
    per_line_h = band_h / len(lines)
    common = None
    while size > 8:
        f = ImageFont.truetype(FONT, size)
        fits = True
        for ln in lines:
            bb = probe.textbbox((0, 0), ln, font=f)
            if (bb[2] - bb[0]) > max_w or (bb[3] - bb[1]) > per_line_h * 0.98:
                fits = False
                break
        if fits:
            common = f
            break
        size -= 4
    if common is None:
        common = ImageFont.truetype(FONT, 8)

    total_h = 0
    mets = []
    for ln in lines:
        bb = d.textbbox((0, 0), ln, font=common)
        w, h = bb[2] - bb[0], bb[3] - bb[1]
        mets.append((ln, w, h, bb))
        total_h += h
    gap = 6
    total_h += gap * (len(lines) - 1)
    y = (layer.height - total_h) / 2
    for ln, w, h, bb in mets:
        x = (layer.width - w) / 2 - bb[0]
        d.text((x, y - bb[1]), ln, font=common, fill=YELLOW + (255,),
               stroke_width=stroke, stroke_fill=INK + (255,))
        y += h + gap
    # gentle rotation, hand-lettered look
    rot = layer.rotate(2.2, resample=Image.BICUBIC, expand=False)
    return rot


def build_landscape():
    base = Image.open(os.path.join(THUMBS, "thumb_base_landscape.png")).convert("RGB")
    W, H = 1280, 720
    # base is 1376x768 (~16:9). Resize to fill WxH (negligible crop-free letterbox).
    canvas = Image.new("RGB", (W, H), PAPER)
    r = max(W / base.width, H / base.height)
    nw, nh = round(base.width * r), round(base.height * r)
    base = base.resize((nw, nh), Image.LANCZOS)
    canvas.paste(base, ((W - nw) // 2, (H - nh) // 2))

    band_h = 190  # top empty band
    layer = _headline_layer(["WHY WE COOK"], W, band_h, stroke=9)
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    # center the headline layer horizontally, place in the top band
    lx = (W - layer.width) // 2
    ly = -60
    L.alpha_composite(layer, (lx, ly))
    out = Image.alpha_composite(canvas.convert("RGBA"), L).convert("RGB")
    out.save(os.path.join(THUMBS, "thumbnail.jpg"), "JPEG", quality=92, subsampling=0)
    return out.size


def build_portrait():
    base = Image.open(os.path.join(THUMBS, "thumb_base_portrait.png")).convert("RGB")
    W, H = 1080, 1920  # 9:16
    canvas = Image.new("RGB", (W, H), PAPER)
    r = max(W / base.width, H / base.height)
    nw, nh = round(base.width * r), round(base.height * r)
    base = base.resize((nw, nh), Image.LANCZOS)
    canvas.paste(base, ((W - nw) // 2, (H - nh) // 2))

    # two-line stacked headline in the top empty area
    band_h = 520
    layer = _headline_layer(["WHY WE", "COOK"], W, band_h, stroke=11)
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    lx = (W - layer.width) // 2
    ly = -40
    L.alpha_composite(layer, (lx, ly))
    out = Image.alpha_composite(canvas.convert("RGBA"), L).convert("RGB")
    # Flat cartoon art is visually lossless at 32 colours; keeps PNG well under
    # YouTube's 2 MB thumbnail limit.
    out.quantize(colors=32, method=Image.Quantize.MEDIANCUT,
                 dither=Image.Dither.NONE).save(
        os.path.join(THUMBS, "thumb_portrait.png"), "PNG", optimize=True)
    return out.size


if __name__ == "__main__":
    print("thumbnail.jpg", build_landscape())
    print("thumb_portrait.png", build_portrait())
