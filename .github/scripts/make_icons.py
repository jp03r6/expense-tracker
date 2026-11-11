"""Generate PNG app icons matching icon.svg (dark bg, gradient $)."""
import glob
from PIL import Image, ImageDraw, ImageFont

TOP = (139, 92, 246)   # #8b5cf6
BOT = (217, 70, 239)   # #d946ef
BG = (18, 14, 34)      # #120e22
BASE = 512


def find_font():
    for pat in ("/usr/share/fonts/**/DejaVuSans-Bold.ttf",
                "/usr/share/fonts/**/*Bold*.ttf",
                "/usr/share/fonts/**/*.ttf"):
        hits = glob.glob(pat, recursive=True)
        if hits:
            return hits[0]
    return None


def gradient(size):
    img = Image.new("RGB", size)
    px = img.load()
    n = size[0] + size[1] - 2
    for y in range(size[1]):
        for x in range(size[0]):
            t = (x + y) / n
            px[x, y] = tuple(int(TOP[i] + (BOT[i] - TOP[i]) * t) for i in range(3))
    return img


def glyph_mask(size, font_size):
    m = Image.new("L", size, 0)
    d = ImageDraw.Draw(m)
    path = find_font()
    font = ImageFont.truetype(path, font_size) if path else ImageFont.load_default()
    bbox = d.textbbox((0, 0), "$", font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (size[0] - w) / 2 - bbox[0]
    y = (size[1] - h) / 2 - bbox[1]
    d.text((x, y), "$", font=font, fill=255)
    return m


def border_mask(size, inset, radius, width):
    m = Image.new("L", size, 0)
    d = ImageDraw.Draw(m)
    d.rounded_rectangle([inset, inset, size[0] - 1 - inset, size[1] - 1 - inset],
                        radius, outline=90, width=width)
    return m


def make_icon(size, full_bleed=False, glyph_ratio=0.60, border=True):
    s = size / BASE
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    grad = gradient((size, size)).convert("RGBA")

    if full_bleed:
        img.paste((BG[0], BG[1], BG[2], 255), (0, 0, size, size))
    else:
        bgm = Image.new("L", (size, size), 0)
        ImageDraw.Draw(bgm).rounded_rectangle([0, 0, size - 1, size - 1], int(116 * s), fill=255)
        img.paste((BG[0], BG[1], BG[2], 255), (0, 0), bgm)

    if border:
        bm = border_mask((size, size), int(40 * s), int(80 * s), max(2, int(12 * s)))
        img.paste(grad, (0, 0), bm)

    gm = glyph_mask((size, size), int(size * glyph_ratio))
    img.paste(grad, (0, 0), gm)
    return img


if __name__ == "__main__":
    make_icon(180, full_bleed=True, glyph_ratio=0.62).save("apple-touch-icon.png")
    make_icon(192).save("icon-192.png")
    make_icon(512).save("icon-512.png")
    make_icon(512, full_bleed=True, glyph_ratio=0.47).save("icon-512-maskable.png")
    print("icons written")
