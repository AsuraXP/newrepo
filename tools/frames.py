"""Shared frame utilities: normalise (resize+pad, never crop/stretch) and contact sheets."""
import glob
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1080
PAPER = (247, 240, 221)  # warm cream, matches the style block
FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
]


def _font(size):
    for p in FONT_PATHS:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def normalise(src, dst=None):
    """Resize to fit WxH preserving aspect, pad with paper colour. Never crop, never stretch."""
    dst = dst or src
    im = Image.open(src).convert("RGB")
    orig = im.size
    r = min(W / im.width, H / im.height)
    nw, nh = max(1, round(im.width * r)), max(1, round(im.height * r))
    im = im.resize((nw, nh), Image.LANCZOS)
    canvas = Image.new("RGB", (W, H), PAPER)
    canvas.paste(im, ((W - nw) // 2, (H - nh) // 2))
    # Flat cartoon art survives a 32-colour palette with no visible loss and
    # cuts frame size ~4x (2.4 MB -> 0.57 MB), which matters for 117 frames.
    canvas.quantize(colors=32, method=Image.Quantize.MEDIANCUT,
                    dither=Image.Dither.NONE).save(dst, optimize=True)
    return orig, canvas.size


def contact_sheet(paths, out_path, cols=5, thumb_w=380, title="", labels=None):
    """Build a labelled contact sheet and LOOK at it. 5 across, ~380px thumbs."""
    paths = list(paths)
    assert paths, "no frames for contact sheet"
    tw = thumb_w
    th = round(tw * H / W)
    label_h = 34
    head_h = 46 if title else 0
    rows = (len(paths) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw, head_h + rows * (th + label_h)), (28, 26, 24))
    d = ImageDraw.Draw(sheet)
    f_title = _font(22)
    f_lab = _font(17)
    if title:
        d.text((10, 10), title, fill=(255, 214, 64), font=f_title)
    for i, p in enumerate(paths):
        im = Image.open(p).convert("RGB")
        r = min(tw / im.width, th / im.height)
        im = im.resize((max(1, round(im.width * r)), max(1, round(im.height * r))), Image.LANCZOS)
        tile = Image.new("RGB", (tw, th), PAPER)
        tile.paste(im, ((tw - im.width) // 2, (th - im.height) // 2))
        x = (i % cols) * tw
        y = head_h + (i // cols) * (th + label_h)
        sheet.paste(tile, (x, y))
        lab = labels[i] if labels else os.path.basename(p)
        d.text((x + 6, y + th + 6), lab, fill=(240, 238, 232), font=f_lab)
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    sheet.save(out_path)
    return sheet.size


if __name__ == "__main__":
    import sys
    pattern, out, title = sys.argv[1], sys.argv[2], (sys.argv[3] if len(sys.argv) > 3 else "")
    ps = sorted(glob.glob(pattern))
    print(len(ps), "frames ->", contact_sheet(ps, out, title=title))
