"""Render the full demo film: motion-graphics teaser (~35 s) -> app walkthrough -> closing.

Structure mirrors a start-up teaser: a brand moment, the problem told through
pictures (stock photos plus two drawn problem mocks), an RBI scale bridge, then
the working prototype screens, then a closing card. ~2:12 at 1920x1080/24 fps.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / ".video-deps"))

from PIL import Image, ImageDraw, ImageFilter, ImageFont
import imageio_ffmpeg


ROOT = Path(__file__).parent
ASSETS = ROOT / "assets"
WORK = ROOT / ".render" / "final-cut"
OUT = ROOT / "Bank-Raasta-demo-final.mp4"
REUSE_SCENES = "--reuse-scenes" in sys.argv
VIDEO = ASSETS / "market-video.mp4"
MARKET_STILL = ASSETS / "market-frame.png"
QR_STILL = ASSETS / "qr-payment-closeup.jpg"
SHOP_STILL = ASSETS / "shop-counter.jpg"
PERSON_PHONE = ASSETS / "person-phone-1.jpg"   # man looking at his phone, over the shoulder
PERSON_WAIT = ASSETS / "person-phone-3.jpg"    # elderly man holding his phone, waiting
OVERVIEW = ASSETS / "app-overview.png"
DETAILS = ASSETS / "app-details.png"
SUMMARY = ASSETS / "app-summary.png"
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 1920, 1080, 24
FONT = r"C:\Windows\Fonts\segoeui.ttf"
FONT_BOLD = r"C:\Windows\Fonts\segoeuib.ttf"

NAVY = (14, 28, 47)
BLUE = (73, 142, 226)
MINT = (119, 205, 163)
RED = (233, 87, 86)
WHITE = (250, 252, 255)
MUTED = (180, 198, 219)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_BOLD if bold else FONT, size)


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def cover(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    image = image.convert("RGB")
    target_w, target_h = size
    scale = max(target_w / image.width, target_h / image.height)
    rw, rh = round(image.width * scale), round(image.height * scale)
    image = image.resize((rw, rh), Image.Resampling.LANCZOS)
    left = (rw - target_w) // 2
    top = (rh - target_h) // 2
    return image.crop((left, top, left + target_w, top + target_h))


def wrap(draw: ImageDraw.ImageDraw, text: str, face: ImageFont.FreeTypeFont, width: int) -> list[str]:
    lines: list[str] = []
    line = ""
    for word in text.split():
        candidate = word if not line else line + " " + word
        if draw.textbbox((0, 0), candidate, font=face)[2] <= width:
            line = candidate
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def paragraph(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str,
              face: ImageFont.FreeTypeFont, fill, width: int, gap: int = 8) -> int:
    x, y = xy
    for line in wrap(draw, text, face, width):
        draw.text((x, y), line, font=face, fill=fill)
        y += face.size + gap
    return y


def rounded_panel(img: Image.Image, box: tuple[int, int, int, int], fill=(8, 20, 37, 208), radius=24) -> None:
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).rounded_rectangle(box, radius=radius, fill=fill)
    img.alpha_composite(layer)


def rounded_image(source: Image.Image, size: tuple[int, int], radius: int = 14) -> Image.Image:
    image = source.convert("RGB").resize(size, Image.Resampling.LANCZOS).convert("RGBA")
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius=radius, fill=255)
    image.putalpha(mask)
    return image


def shadow(img: Image.Image, box: tuple[int, int, int, int], radius=26, blur=24, alpha=115) -> None:
    layer = Image.new("RGBA", img.size, (0, 0, 0, alpha))
    img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(blur)))


def photo_background(path: Path, dark=0.30, band: tuple[int, int, int, int] | None = None) -> Image.Image:
    src = Image.open(path)
    if band:
        src = src.crop(band)
    img = cover(src, (W, H)).convert("RGBA")
    shade = Image.new("RGBA", img.size, (8, 18, 30, int(dark * 255)))
    img.alpha_composite(shade)
    return img


def numbered(prefix: str) -> Path:
    return WORK / f"{prefix}-{len(list(WORK.glob(f'{prefix}-*.png'))):02d}.png"


def subtitle_pill(img: Image.Image, text: str) -> None:
    """Black centered subtitle pill, teaser style."""
    d = ImageDraw.Draw(img)
    face = font(36, True)
    tw = d.textbbox((0, 0), text, font=face)[2]
    box = ((W - tw) // 2 - 46, 962, (W + tw) // 2 + 46, 1042)
    d.rounded_rectangle(box, radius=40, fill=(16, 16, 18, 245))
    d.text(((W - tw) // 2, 976), text, font=face, fill=WHITE)


def route_glyph(img: Image.Image, cx: int, cy: int, scale: float = 1.0) -> None:
    """Bank Raasta mark: a curved route that ends at a destination pin."""
    d = ImageDraw.Draw(img)
    s = scale
    pts = [(cx - 92 * s, cy + 78 * s), (cx - 54 * s, cy + 24 * s), (cx + 10 * s, cy - 4 * s),
           (cx + 60 * s, cy - 38 * s)]
    d.line([tuple(p) for p in pts], fill=BLUE, width=max(2, int(14 * s)), joint="curve")
    r = int(11 * s)
    d.ellipse((cx - 92 * s - r, cy + 78 * s - r, cx - 92 * s + r, cy + 78 * s + r), fill=BLUE)
    pr = int(34 * s)
    d.ellipse((cx + 26 * s, cy - 110 * s, cx + 26 * s + pr * 2, cy - 110 * s + pr * 2), fill=MINT)
    dr = int(12 * s)
    d.ellipse((cx + 26 * s + pr - dr, cy - 110 * s + pr - dr - 2, cx + 26 * s + pr + dr,
               cy - 110 * s + pr + dr - 2), fill=(10, 30, 50))
    d.polygon([(cx + 26 * s, cy - 55 * s), (cx + 26 * s - 24 * s, cy - 6 * s),
               (cx + 26 * s + 24 * s, cy - 6 * s)], fill=MINT)


def vignette(img: Image.Image, strength: float = 0.5) -> Image.Image:
    """Darken the edges so the centre of a frame reads like a spotlight."""
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).ellipse((-260, -160, W + 260, H + 160), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(190))
    dark = Image.new("RGBA", (W, H), (2, 10, 20, int(strength * 255)))
    return Image.composite(img.convert("RGB"), dark.convert("RGB"), mask).convert("RGBA")


def make_logo_scene() -> Path:
    """Opening frame: dark, cinematic — the brand mark glows over a QR-payment
    photograph, like a chapter title card."""
    img = photo_background(QR_STILL, 0.66)
    img = vignette(img, 0.45)
    glyph = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    route_glyph(glyph, W // 2 + 26, 316, scale=1.55)
    halo = glyph.filter(ImageFilter.GaussianBlur(30))
    r, g, b, a = halo.split()
    halo = Image.merge("RGBA", (r, g, b, a.point(lambda v: int(v * 0.55))))
    img.alpha_composite(halo)
    img.alpha_composite(glyph)
    d = ImageDraw.Draw(img)
    word = "Bank Raasta"
    face = font(126, True)
    tw = d.textbbox((0, 0), word, font=face)[2]
    d.text(((W - tw) // 2, 500), word, font=face, fill=WHITE)
    d.rounded_rectangle(((W - 300) // 2, 656, (W + 300) // 2, 666), radius=5, fill=MINT)
    line = "A voice-first guide to the next step in a bank complaint"
    lface = font(31)
    lw = d.textbbox((0, 0), line, font=lface)[2]
    d.text(((W - lw) // 2, 710), line, font=lface, fill=MUTED)
    subtitle_pill(img, "For the moment a payment goes wrong.")
    out = numbered("logo")
    img.save(out)
    return out


def make_problem_phone() -> Path:
    """A man and his phone: the real phone anchors a zoom callout that shows
    the drawn failed-payment screen — what he only sees in miniature."""
    img = photo_background(PERSON_PHONE, 0.38)
    # zoom ring around the real phone's screen (anchor measured on the photo)
    d = ImageDraw.Draw(img)
    d.ellipse((552, 262, 662, 416), outline=(255, 255, 255, 165), width=2)
    # pulsing red alert rings around the same anchor — payment failure energy
    d.ellipse((542, 252, 672, 426), outline=(233, 87, 86, 150), width=3)
    d.ellipse((532, 242, 682, 436), outline=(233, 87, 86, 70), width=2)
    # drawn mock phone (the "view zoomed in")
    pw, ph, px, py = 430, 860, 40, 84
    body = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    bd = ImageDraw.Draw(body)
    bd.rounded_rectangle((0, 0, pw - 1, ph - 1), radius=50, fill=(12, 24, 40, 250),
                         outline=(255, 255, 255, 80), width=3)
    bd.rounded_rectangle((pw // 2 - 66, 26, pw // 2 + 66, 52), radius=12, fill=(30, 46, 64, 255))
    shadow(img, (px + 20, py + 28, px + pw + 20, py + ph + 28), blur=30, alpha=140)
    img.alpha_composite(body, (px, py))
    d = ImageDraw.Draw(img)
    d.text((px + 38, 116), "9:41", font=font(26, True), fill=WHITE)
    d.text((px + pw - 172, 120), "CASH APP", font=font(21, True), fill=MUTED)
    d.text((px + 38, 186), "Scan & Pay", font=font(40, True), fill=WHITE)
    d.text((px + 38, 246), "To: Sharma General Store", font=font(25), fill=MUTED)
    d.text((px + 38, 372), "₹ 2,450", font=font(80, True), fill=WHITE)
    y = 545
    d.rounded_rectangle((px + 32, y, px + pw - 32, y + 90), radius=19, fill=(66, 22, 26, 255),
                        outline=(233, 87, 86, 220), width=3)
    d.text((px + 52, y + 16), "PAYMENT FAILED", font=font(32, True), fill=RED)
    d.text((px + 52, y + 54), "Amount debited from account", font=font(21), fill=(240, 210, 212))
    d.text((px + 38, y + 142), "UPI Ref 4128 9067 2210", font=font(23, True), fill=MUTED)
    d.text((px + 38, y + 182), "Merchant: no confirmation", font=font(23), fill=MUTED)
    d.text((px + 38, y + 222), "You complained to the bank", font=font(23), fill=MUTED)
    d.rounded_rectangle((px + 32, 896, px + pw - 32, 938), radius=16, fill=(23, 49, 78, 255))
    d.text((px + 230, 902), "Sample screen", font=font(19), fill=(150, 175, 200))
    # connector: his phone screen -> the zoomed view
    d.rounded_rectangle((552, 262, 662, 416), radius=16, outline=(255, 255, 255, 120), width=2)
    d.line([(612, 336), (536, 452), (478, 520)], fill=MINT, width=7, joint="curve")
    d.ellipse((604, 328, 620, 344), fill=MINT)
    d.polygon([(492, 498), (474, 530), (506, 532)], fill=MINT)
    # headline card sits low-right so the man's face stays visible above it
    d = ImageDraw.Draw(img)
    box = (790, 430, 1780, 944)
    rounded_panel(img, box, (8, 20, 37, 224), 30)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((838, 492, 854, 534), radius=7, fill=BLUE)
    d.text((880, 490), "THE PAYMENT FAILS", font=font(25, True), fill=(161, 202, 250))
    d.text((838, 556), "Money debited.", font=font(66, True), fill=WHITE)
    d.text((838, 648), "No confirmation.", font=font(66, True), fill=WHITE)
    d.rounded_rectangle((838, 730, 1128, 744), radius=7, fill=RED)
    paragraph(d, (840, 772), "Both sides are left unsure: the customer paid, the shop received nothing, and the complaint sits unanswered.", font(25), (222, 232, 244), 900, gap=7)
    subtitle_pill(img, "The payment fails. Your money is debited.")
    stamp(img)
    out = numbered("mock")
    img.save(out)
    return out


def make_problem_shop() -> Path:
    """Split-screen diptych: what the customer's phone saw versus what reached
    the shop's screen — the money lives on one screen and nowhere on the other."""
    img = photo_background(SHOP_STILL, 0.50)

    def phone(px: int, py: int = 190, pw: int = 400, ph: int = 700) -> None:
        body = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
        bd = ImageDraw.Draw(body)
        bd.rounded_rectangle((0, 0, pw - 1, ph - 1), radius=46, fill=(12, 24, 40, 252),
                             outline=(255, 255, 255, 75), width=3)
        bd.rounded_rectangle((pw // 2 - 60, 22, pw // 2 + 60, 46), radius=11, fill=(30, 46, 64, 255))
        shadow(img, (px + 16, py + 26, px + pw + 16, py + ph + 26), blur=30, alpha=150)
        img.alpha_composite(body, (px, py))

    d = ImageDraw.Draw(img)
    # top kicker
    text = "TWO SCREENS · ONE PAYMENT · NO TRUTH"
    kface = font(27, True)
    kw = d.textbbox((0, 0), text, font=kface)[2]
    d.rounded_rectangle(((W - kw) // 2 - 40, 52, (W + kw) // 2 + 40, 114), radius=30,
                        fill=(8, 20, 37, 235), outline=(233, 87, 86, 120), width=2)
    d.text(((W - kw) // 2, 69), text, font=kface, fill=WHITE)

    # ---- the customer's phone (left)
    px, py, pw = 170, 190, 400
    phone(px)
    d = ImageDraw.Draw(img)
    d.text((px + 36, py + 70), "9:41", font=font(24, True), fill=WHITE)
    d.text((px + pw - 178, py + 72), "CASH APP", font=font(19, True), fill=MUTED)
    d.text((px + 36, py + 126), "Scan & Pay", font=font(36, True), fill=WHITE)
    d.text((px + 36, py + 184), "To: Sharma General Store", font=font(21), fill=MUTED)
    d.text((px + 36, py + 292), "₹ 2,450", font=font(64, True), fill=WHITE)
    d.rounded_rectangle((px + 30, py + 420, px + pw - 30, py + 504), radius=17,
                        fill=(66, 22, 26, 255), outline=(233, 87, 86, 220), width=3)
    d.text((px + 52, py + 434), "PAYMENT FAILED", font=font(26, True), fill=RED)
    d.text((px + 52, py + 470), "Amount debited", font=font(18), fill=(240, 210, 212))
    d.rounded_rectangle((px + 30, py + 556, px + pw - 30, py + 644), radius=16, fill=(23, 49, 78, 255))
    d.text((px + 52, py + 572), "SMS · 7:12 PM", font=font(17, True), fill=MINT)
    d.text((px + 52, py + 600), "₹2,450 debited from a/c", font=font(19), fill=(214, 230, 246))
    d.text((px + 56, py + 680), "The money left the account.", font=font(19, True), fill=MINT)

    # ---- the shop's phone (right)
    qx = 1350
    phone(qx)
    d = ImageDraw.Draw(img)
    d.text((qx + 36, py + 70), "7:12 PM", font=font(24, True), fill=WHITE)
    d.text((qx + pw - 190, py + 72), "MERCHANT", font=font(19, True), fill=MUTED)
    d.text((qx + 36, py + 126), "Today's collections", font=font(32, True), fill=WHITE)
    d.text((qx + 36, py + 184), "Sharma General Store", font=font(21), fill=MUTED)
    d.text((qx + 36, py + 284), "₹ 0", font=font(96, True), fill=RED)
    d.text((qx + 218, py + 344), "received", font=font(24), fill=MUTED)
    d.rounded_rectangle((qx + 30, py + 444, qx + pw - 30, py + 528), radius=17, fill=(66, 22, 26, 255))
    d.text((qx + 52, py + 462), "NO RECORD OF", font=font(26, True), fill=RED)
    d.text((qx + 52, py + 494), "THIS PAYMENT", font=font(26, True), fill=RED)
    d.text((qx + 56, py + 680), "The shop received nothing.", font=font(19, True), fill=MUTED)

    # ---- the red void between the two screens
    fb = d.textbbox((0, 0), "×", font=font(170, True))
    d.text(((W - fb[2]) // 2, py + 210), "×", font=font(170, True), fill=(233, 87, 86, 235))
    link = "NO CONFIRMATION · EITHER SIDE"
    lface = font(26, True)
    lw = d.textbbox((0, 0), link, font=lface)[2]
    d.rounded_rectangle(((W - lw) // 2 - 30, py + 448, (W + lw) // 2 + 30, py + 504), radius=28,
                        fill=(8, 20, 37, 240), outline=(233, 87, 86, 160), width=2)
    d.text(((W - lw) // 2, py + 462), link, font=lface, fill=(245, 190, 190))

    # ---- caption chips under each phone
    for cx, label in ((px + pw // 2, "WHAT THE CUSTOMER SAW"),
                      (qx + pw // 2, "WHAT THE SHOP SAW")):
        lwd = d.textbbox((0, 0), label, font=font(19, True))[2]
        d.rounded_rectangle((cx - lwd // 2 - 28, 904, cx + lwd // 2 + 28, 946), radius=20,
                            fill=(10, 22, 38, 235))
        d.text((cx - lwd // 2, 914), label, font=font(19, True), fill=(198, 214, 232))

    subtitle_pill(img, "The shop has no confirmation.")
    stamp(img)
    out = numbered("mock")
    img.save(out)
    return out


def make_problem_wait() -> Path:
    """An elderly man waits with his phone; the drawn complaint timeline tells
    the story at his side, leaving his face in frame."""
    # crop a 16:9 band around the face/phone region of the portrait
    img = photo_background(PERSON_WAIT, 0.5, band=(0, 260, 1600, 1150))
    # giant ghost numeral across the man's side of the frame — the wait, visualised
    gd = ImageDraw.Draw(img)
    gd.text((34, 400), "12", font=font(430, True), fill=(233, 87, 86, 52))
    gd.text((96, 892), "DAYS · NOT ONE REPLY", font=font(30, True), fill=(245, 190, 190))
    px, py, pw, ph = 1090, 150, 760, 830
    card = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    cd = ImageDraw.Draw(card)
    cd.rounded_rectangle((0, 0, pw - 1, ph - 1), radius=32, fill=(11, 25, 42, 246),
                         outline=(255, 255, 255, 55), width=3)
    shadow(img, (px + 16, py + 24, px + pw + 16, py + ph + 24), blur=28, alpha=150)
    img.alpha_composite(card, (px, py))
    d = ImageDraw.Draw(img)
    # small kicker chip over the photograph, clear of the right card
    d.rounded_rectangle((60, 74, 470, 140), radius=32, fill=(10, 22, 38, 225))
    d.text((92, 92), "THE WAIT · DAY 12", font=font(26, True), fill=(245, 190, 190))
    d.text((px + 50, py + 40), "COMPLAINT TIMELINE", font=font(25, True), fill=(161, 202, 250))
    rows = [
        ("Day 0", "Filed the complaint with the bank", MINT),
        ("Day 5", "No acknowledgement received", MUTED),
        ("Day 12", "Still no reply, no resolution", RED),
        ("Today", "The next step is unclear", WHITE),
    ]
    y = py + 118
    for i, (day, text, col) in enumerate(rows):
        d.ellipse((px + 54, y + 8, px + 74, y + 28), fill=col)
        if i < len(rows) - 1:
            d.line((px + 64, y + 30, px + 64, y + 132), fill=(60, 82, 106), width=3)
        d.text((px + 106, y), day, font=font(26, True), fill=WHITE)
        d.text((px + 106, y + 40), text, font=font(22), fill=MUTED)
        y += 174
    subtitle_pill(img, "You complained. The bank did not reply.")
    stamp(img)
    out = numbered("mock")
    img.save(out)
    return out


def make_stat_scene() -> Path:
    """The RBI statistic as a giant numeral — poster typography, not a text box."""
    img = photo_background(MARKET_STILL, 0.58)
    img = vignette(img, 0.40)
    d = ImageDraw.Draw(img)
    text = "THE SCALE OF THE PROBLEM"
    kface = font(22, True)
    kw = d.textbbox((0, 0), text, font=kface)[2]
    d.rounded_rectangle(((W - kw) // 2 - 40, 96, (W + kw) // 2 + 40, 152), radius=28,
                        fill=(8, 20, 37, 238))
    d.rounded_rectangle(((W - kw) // 2 - 8, 112, (W - kw) // 2 + 6, 136), radius=6, fill=BLUE)
    d.text(((W - kw) // 2 + 32, 112), text, font=kface, fill=(161, 202, 250))
    num = "13,34,244"
    nface = font(218, True)
    nw = d.textbbox((0, 0), num, font=nface)[2]
    d.text(((W - nw) // 2, 250), num, font=nface, fill=WHITE,
           stroke_width=1, stroke_fill=(4, 10, 20))
    label = "COMPLAINTS RECEIVED BY RBI"
    lface = font(44, True)
    lw = d.textbbox((0, 0), label, font=lface)[2]
    d.text(((W - lw) // 2, 524), label, font=lface, fill=(245, 190, 190))
    d.rounded_rectangle(((W - 220) // 2, 616, (W + 220) // 2, 624), radius=4, fill=MINT)
    sub = "under the Reserve Bank's Integrated Ombudsman Scheme · FY 2024-25"
    sface = font(30)
    sw = d.textbbox((0, 0), sub, font=sface)[2]
    d.text(((W - sw) // 2, 656), sub, font=sface, fill=(210, 224, 240))
    src = "Source: RBI · Annual Report of the Ombudsman Scheme, 2024-25"
    scface = font(17, True)
    scw = d.textbbox((0, 0), src, font=scface)[2]
    d.text(((W - scw) // 2, 764), src, font=scface, fill=(160, 182, 208))
    subtitle_pill(img, "13.34 lakh complaints in one year.")
    stamp(img)
    out = numbered("mock")
    img.save(out)
    return out


def make_bridge_scene() -> Path:
    """A flat brand-color statement card — the 'so we built it' beat, a strip of
    stillness between the problem photos and the product tour."""
    img = Image.new("RGBA", (W, H), NAVY + (255,))
    glyph = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    route_glyph(glyph, 1530, 520, scale=3.0)
    glyph.putalpha(glyph.split()[3].point(lambda v: int(v * 0.09)))
    img.alpha_composite(glyph)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((262, 172, 278, 232), radius=8, fill=BLUE)
    d.text((312, 178), "SO WE BUILT", font=font(42, True), fill=(161, 202, 250))
    d.text((250, 276), "Bank Raasta.", font=font(146, True), fill=WHITE)
    d.rounded_rectangle((258, 478, 1036, 488), radius=5, fill=MINT)
    paragraph(d, (258, 528), "A guide that organizes the case and shows the possible next official step — the official one, not a guess.", font(31), (216, 228, 242), 1180, gap=11)
    for cx, label, color in ((560, "NO BANK LOGIN", MINT),
                             (1080, "NEVER FILES FOR YOU", (245, 190, 190))):
        cface = font(23, True)
        cw = d.textbbox((0, 0), label, font=cface)[2]
        d.rounded_rectangle((cx - cw // 2 - 30, 726, cx + cw // 2 + 30, 782), radius=28,
                            outline=color, width=3)
        d.text((cx - cw // 2, 739), label, font=cface, fill=color)
    subtitle_pill(img, "So we built Bank Raasta.")
    out = numbered("mock")
    img.save(out)
    return out


def stamp(img: Image.Image, text: str = "ILLUSTRATIVE SCENARIO · STOCK PHOTO") -> None:
    d = ImageDraw.Draw(img)
    d.text((W - 570, 36), text, font=font(15, True), fill=(245, 247, 250, 220))


def caption_overlay(kicker: str, title: str, detail: str, *, stamp_text="ILLUSTRATIVE SCENARIO · STOCK FOOTAGE") -> Path:
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    box = (82, 620, 1330, 984)
    d.rounded_rectangle(box, radius=28, fill=(9, 23, 41, 222), outline=(255, 255, 255, 40), width=2)
    d.rounded_rectangle((118, 660, 132, 694), radius=6, fill=BLUE)
    d.text((156, 657), kicker.upper(), font=font(21, True), fill=(158, 199, 247, 255))
    y = paragraph(d, (118, 718), title, font(44, True), WHITE, 1130, gap=7)
    y += 11
    paragraph(d, (120, y), detail, font(25), (221, 231, 243, 255), 1110, gap=5)
    d.text((W - 570, H - 45), stamp_text, font=font(15, True), fill=(245, 247, 250, 220))
    out = numbered("overlay")
    img.save(out)
    return out


def encode_footage(start: float, duration: float, overlay: Path, out: Path) -> None:
    if REUSE_SCENES and out.exists():
        return
    vf = (
        "[0:v]trim=duration={dur},setpts=PTS-STARTPTS,"
        "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,"
        "fps=24,setsar=1[bg];[1:v]format=rgba[fg];"
        "[bg][fg]overlay=0:0:format=auto,format=yuv420p[v]"
    ).format(dur=duration)
    run([FFMPEG, "-hide_banner", "-loglevel", "error", "-y", "-ss", str(start), "-i", str(VIDEO),
         "-loop", "1", "-i", str(overlay), "-filter_complex", vf, "-map", "[v]", "-t", str(duration),
         "-an", "-r", str(FPS), "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", str(out)])


def encode_still(image: Path, duration: float, out: Path, zoom: bool = True) -> None:
    if REUSE_SCENES and out.exists():
        return
    filters = ("scale=1920:1080,zoompan=z='min(zoom+0.00010,1.008)':d=1:s=1920x1080:fps=24,"
               "format=yuv420p") if zoom else "scale=1920:1080,format=yuv420p"
    run([FFMPEG, "-hide_banner", "-loglevel", "error", "-y", "-threads", "1",
         "-loop", "1", "-i", str(image), "-t", str(duration),
         "-vf", filters, "-an", "-r", str(FPS), "-c:v", "libx264", "-preset", "ultrafast",
         "-crf", "18", "-pix_fmt", "yuv420p", str(out)])


def brand_rail(img: Image.Image) -> None:
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((36, 24, 190, 60), radius=18, fill=(35, 77, 126, 255))
    d.text((58, 31), "BANK RAASTA", font=font(17, True), fill=WHITE)


def make_full_ui(path: Path, chapter: str, caption: str) -> Path:
    img = Image.new("RGBA", (W, H), NAVY + (255,))
    brand_rail(img)
    d = ImageDraw.Draw(img)
    d.text((220, 30), chapter.upper(), font=font(18, True), fill=(177, 201, 230))
    screen = rounded_image(Image.open(path).convert("RGB"), (1840, 890), 12)
    shadow(img, (37, 83, 1883, 981), radius=15, blur=17, alpha=118)
    img.alpha_composite(screen, (40, 78))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((38, 988, 1882, 1060), radius=18, fill=(20, 42, 68, 255))
    d.rounded_rectangle((60, 1006, 69, 1042), radius=5, fill=BLUE)
    paragraph(d, (90, 1005), caption, font(24, True), WHITE, 1735, gap=2)
    out = numbered("ui")
    img.save(out)
    return out


def make_focus_ui(path: Path, crop_box: tuple[int, int, int, int], chapter: str,
                  title: str, bullets: list[str], *, image_left=True, crop_height=775) -> Path:
    img = Image.new("RGBA", (W, H), NAVY + (255,))
    brand_rail(img)
    d = ImageDraw.Draw(img)
    d.text((225, 33), chapter.upper(), font=font(18, True), fill=(177, 201, 230))
    source = Image.open(path).convert("RGB").crop(crop_box)
    card_x = 56 if image_left else 1138
    card_y = 126
    card_w = 1070
    card_h = crop_height
    screen = rounded_image(source, (card_w, card_h), 15)
    shadow(img, (card_x - 3, card_y - 2, card_x + card_w + 4, card_y + card_h + 4), radius=18, blur=24, alpha=135)
    img.alpha_composite(screen, (card_x, card_y))
    text_x = 1190 if image_left else 62
    text_w = 665
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((text_x, 150, text_x + 12, 192), radius=6, fill=BLUE)
    d.text((text_x + 32, 151), chapter.upper(), font=font(18, True), fill=(151, 194, 244))
    y = paragraph(d, (text_x, 220), title, font(38, True), WHITE, text_w, gap=8)
    y += 28
    for item in bullets:
        d.ellipse((text_x + 1, y + 9, text_x + 13, y + 21), fill=MINT)
        y2 = paragraph(d, (text_x + 32, y), item, font(24), (219, 231, 244), text_w - 40, gap=7)
        y = y2 + 24
    d.text((62, 1036), "Illustrative sample case · Confirm the applicable process with your bank or RBI", font=font(16), fill=(151, 174, 202))
    out = numbered("focus")
    img.save(out)
    return out


def make_api_highlight(path: Path, chapter: str, caption: str, highlight: tuple[int, int, int, int] | None = None) -> Path:
    img = Image.new("RGBA", (W, H), NAVY + (255,))
    brand_rail(img)
    d = ImageDraw.Draw(img)
    d.text((220, 30), chapter.upper(), font=font(18, True), fill=(177, 201, 230))
    screen = rounded_image(Image.open(path).convert("RGB"), (1840, 890), 12)
    shadow(img, (37, 83, 1883, 981), radius=15, blur=17, alpha=118)
    img.alpha_composite(screen, (40, 78))
    if highlight:
        x1, y1, x2, y2 = highlight
        sx, sy = 1840 / 1862, 890 / 900
        box = (40 + int(x1 * sx), 78 + int(y1 * sy), 40 + int(x2 * sx), 78 + int(y2 * sy))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle(box, radius=12, outline=(87, 174, 255, 255), width=7)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((38, 988, 1882, 1060), radius=18, fill=(20, 42, 68, 255))
    d.rounded_rectangle((60, 1006, 69, 1042), radius=5, fill=BLUE)
    paragraph(d, (90, 1005), caption, font(24, True), WHITE, 1735, gap=2)
    out = numbered("api")
    img.save(out)
    return out


def make_closing_scene() -> Path:
    img = photo_background(MARKET_STILL, 0.35)
    route_glyph(img, 292, 300, scale=1.0)
    d = ImageDraw.Draw(img)
    d.text((150, 400), "A clearer route through a bank complaint.", font=font(58, True), fill=WHITE)
    paragraph(d, (152, 500), "Organize the facts. Understand the official next step. Keep control of what you send.", font(28), (224, 234, 245), 860, gap=9)
    stamp(img, "ILLUSTRATIVE SCENARIO · PEXELS FOOTAGE · SAMPLE CASE DATA")
    out = numbered("mock")
    img.save(out)
    return out


SCENES_BUILDERS = [
    # (image/scene builder or footage tuple, duration, zoom?)
    ("logo", 4.0, False),
    ("phone", 6.0, True),
    ("shop", 5.0, True),
    ("wait", 6.0, True),
    ("stat", 7.5, True),
    ("bridge", 5.0, True),
    ("ui1", 12.0, True),
    ("ui2", 10.0, True),
    ("ui3", 12.0, True),
    ("ui4", 11.0, True),
    ("ui5", 13.0, True),
    ("ui6", 9.0, True),
    ("ui7", 12.0, True),
    ("ui8", 9.0, True),
    ("ui9", 11.0, True),
    ("closing", 9.0, True),
]


def main() -> None:
    WORK.mkdir(parents=True, exist_ok=True)
    for needed in [VIDEO, MARKET_STILL, QR_STILL, SHOP_STILL, PERSON_PHONE, PERSON_WAIT,
                   OVERVIEW, DETAILS, SUMMARY]:
        if not needed.exists():
            raise FileNotFoundError(needed)

    clips: list[tuple[Path, float]] = []

    def add(builder, dur: float, zoom=True):
        out = WORK / f"clip-{len(clips) + 1:02d}.mp4"
        img = builder()
        encode_still(img, dur, out, zoom=zoom)
        clips.append((out, dur))

    add(make_logo_scene, 4.0)
    add(make_problem_phone, 6.0)
    add(make_problem_shop, 5.0)
    add(make_problem_wait, 6.0)
    add(make_stat_scene, 7.5)
    add(make_bridge_scene, 5.0)
    add(lambda: make_full_ui(OVERVIEW, "01 · Start with what happened",
        "One place to describe the issue, record dates and see the route suggested by the information you entered."), 12.0)
    add(lambda: make_focus_ui(OVERVIEW, (226, 320, 960, 775), "02 · Issue & language", "Choose the case that fits.", [
        "UPI or digital payment, card charge, loan or EMI, and bank-service issues.",
        "Speech input supports ten listed Indian languages. Guidance is currently Hindi or English.",
    ], crop_height=740), 10.0)
    add(lambda: make_full_ui(DETAILS, "03 · Build a clear case",
        "Record the event, amount, provider, desired outcome, and whether you have already complained."), 12.0)
    add(lambda: make_focus_ui(DETAILS, (266, 118, 965, 494), "04 · Speak, then review", "Gnani Prisma speech input", [
        "Transcribed words appear in an editable field so the user can correct them before use.",
        "The API is wired in the prototype. This recording uses sample mode; no key is configured.",
    ], crop_height=760), 11.0)
    add(lambda: make_focus_ui(OVERVIEW, (975, 325, 1630, 828), "05 · See a dated next step", "A case path from dates and status", [
        "The guide follows a deterministic rule path using the complaint timeline and reply status.",
        "It links to the official RBI route. It does not decide the outcome or submit a complaint.",
    ], crop_height=760), 13.0)
    add(lambda: make_focus_ui(OVERVIEW, (982, 525, 1630, 888), "06 · Know what to keep", "Be ready before you follow up.", [
        "Keep the complaint number, the bank's reply, and transaction proof together.",
        "Open RBI's Complaint Management System from the guide when you are ready.",
    ], crop_height=700), 9.0)
    add(lambda: make_full_ui(SUMMARY, "07 · Make the story easy to share",
        "Create a summary in the selected guidance language, then copy it or download a text file to review."), 12.0)
    add(lambda: make_focus_ui(SUMMARY, (995, 685, 1627, 896), "08 · Save safely", "Keep your notes on this device.", [
        "Saved case notes use this browser's local storage.",
        "No bank login, PIN, OTP, password or full account number is needed. The app never files the complaint for you.",
    ], crop_height=620), 9.0)
    add(lambda: make_api_highlight(SUMMARY, "09 · Optional read-aloud",
        "Gnani Timbre is wired for Hindi/English read-aloud; live speech activates when the API key is added privately.",
        highlight=(1018, 0, 1324, 39)), 11.0)
    add(make_closing_scene, 9.0)

    # Staged join: large multi-input xfade chains over-allocate decoder memory, so
    # clips are cross-faded pairwise — never more than two inputs per ffmpeg call.
    xfade = 0.55
    groups = [clips[0:6], clips[6:12], clips[12:16]]

    def join(items: list[tuple[Path, float]], name: str) -> float:
        current = items
        step = 0
        while len(current) > 1:
            merged: list[tuple[Path, float]] = []
            for i in range(0, len(current) - 1, 2):
                a, da = current[i]
                b, db = current[i + 1]
                out = WORK / f"{name}.x{step:02d}-of-{i:02d}.mp4"
                step += 1
                run([FFMPEG, "-hide_banner", "-loglevel", "error", "-y", "-threads", "1",
                     "-i", str(a), "-i", str(b), "-filter_complex",
                     f"[0:v][1:v]xfade=transition=fade:duration={xfade}:offset={da - xfade:.3f},"
                     "format=yuv420p[v]",
                     "-map", "[v]", "-c:v", "libx264", "-preset", "ultrafast", "-crf", "14",
                     "-pix_fmt", "yuv420p", str(out)])
                merged.append((out, da + db - xfade))
            if len(current) % 2 == 1:
                merged.append(current[-1])
            current = merged
        # one final fast pass to a clean crf-18 intermediate for this group
        head, dur = current[0]
        out = WORK / f"{name}.mp4"
        run([FFMPEG, "-hide_banner", "-loglevel", "error", "-y", "-threads", "1",
             "-i", str(head),
             "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18",
             "-pix_fmt", "yuv420p", str(out)])
        return dur

    group_files = []
    for g, items in enumerate(groups):
        dur = join(items, f"stage-{chr(97 + g)}")
        group_files.append((WORK / f"stage-{chr(97 + g)}.mp4", dur))

    # fold the three groups together, again two inputs at a time
    ab, ab_len = group_files[0]
    run([FFMPEG, "-hide_banner", "-loglevel", "error", "-y", "-threads", "1",
         "-i", str(group_files[0][0]), "-i", str(group_files[1][0]), "-filter_complex",
         f"[0:v][1:v]xfade=transition=fade:duration={xfade}:offset={group_files[0][1] - xfade:.3f},"
         "format=yuv420p[v]",
         "-map", "[v]", "-c:v", "libx264", "-preset", "ultrafast", "-crf", "14",
         "-pix_fmt", "yuv420p", str(WORK / "stage-ab.mp4")])
    da = group_files[0][1] + group_files[1][1] - xfade
    off2 = da - xfade
    # quiet market ambience preview bed (final narration mix replaces the track)
    audio_chain = (
        "[2:a]atrim=0:24,asetpts=PTS-STARTPTS,volume=0.16,"
        "afade=t=in:st=0:d=1.2,afade=t=out:st=17:d=5,apad,atrim=duration=180[aout]"
    )
    run([FFMPEG, "-hide_banner", "-loglevel", "error", "-y", "-threads", "1",
         "-i", str(WORK / "stage-ab.mp4"), "-i", str(group_files[2][0]), "-i", str(VIDEO),
         "-filter_complex",
         f"[0:v][1:v]xfade=transition=fade:duration={xfade}:offset={off2:.3f},format=yuv420p[vout];"
         + audio_chain,
         "-map", "[vout]", "-map", "[aout]", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
         "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", "-shortest", str(OUT)])
    total = da + group_files[2][1] - xfade
    print(f"Created {OUT}")
    print(f"Scenes: {len(clips)}; duration about {total:.1f}s")


if __name__ == "__main__":
    main()
