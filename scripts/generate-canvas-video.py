from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path(r"C:\Users\Miguel\AppData\Local\Temp\codex-clipboard-bd483857-205f-4d0c-af07-d253b0cb1de2.png")
OUT = ROOT / "dist" / "linkedin"
FRAMES = OUT / "canvas-frames"
VIDEO = OUT / "eyepik-canvas-walkthrough-16x9.mp4"

W, H = 1920, 1080
FPS = 30


def font(size, bold=False):
    candidates = [
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
    ]
    for item in candidates:
        if Path(item).exists():
            return ImageFont.truetype(item, size)
    return ImageFont.load_default()


TITLE = font(46, True)
BODY = font(30)
SMALL = font(24, True)


def cover_canvas(src, zoom=1.0, pan_x=0.5, pan_y=0.5):
    sw, sh = src.size
    target_ratio = W / H
    src_ratio = sw / sh
    if src_ratio > target_ratio:
        crop_h = sh / zoom
        crop_w = crop_h * target_ratio
    else:
        crop_w = sw / zoom
        crop_h = crop_w / target_ratio
    left = max(0, min(sw - crop_w, (sw - crop_w) * pan_x))
    top = max(0, min(sh - crop_h, (sh - crop_h) * pan_y))
    crop = src.crop((left, top, left + crop_w, top + crop_h))
    return crop.resize((W, H), Image.Resampling.LANCZOS)


def draw_caption(img, title, body):
    draw = ImageDraw.Draw(img, "RGBA")
    draw.rounded_rectangle((64, 760, 710, 995), radius=28, fill=(16, 18, 18, 220), outline=(74, 86, 82, 180), width=2)
    draw.text((96, 798), title, font=TITLE, fill=(255, 255, 255, 255))
    y = 860
    words = body.split()
    line = ""
    for word in words:
        test = f"{line} {word}".strip()
        if draw.textbbox((0, 0), test, font=BODY)[2] > 550:
            draw.text((96, y), line, font=BODY, fill=(210, 221, 216, 255))
            y += 42
            line = word
        else:
            line = test
    if line:
        draw.text((96, y), line, font=BODY, fill=(210, 221, 216, 255))


def draw_tag(img, text):
    draw = ImageDraw.Draw(img, "RGBA")
    draw.rounded_rectangle((1470, 880, 1845, 950), radius=22, fill=(26, 32, 30, 225), outline=(68, 81, 76, 180), width=2)
    draw.ellipse((1500, 902, 1522, 924), fill=(0, 145, 134, 255))
    draw.text((1540, 897), text, font=SMALL, fill=(238, 244, 241, 255))


SCENES = [
    (0.96, 0.50, 0.50, "Buyer intake", "A shopper submits interest and the workflow starts from the webhook."),
    (1.35, 0.28, 0.52, "Normalize details", "The flow cleans buyer fields and scores purchase intent."),
    (1.35, 0.42, 0.52, "Save the buyer", "The record lands in Google Sheets before messages go out."),
    (1.38, 0.55, 0.45, "Sales gets context", "Confirmation and sales alert paths run in parallel."),
    (1.35, 0.67, 0.47, "Route intent", "Ready-to-buy shoppers move into the follow-up branch."),
    (1.28, 0.82, 0.43, "Personal shopping", "The offer is sent and the tracker is updated."),
    (0.96, 0.50, 0.50, "Published workflow", "Production submissions start the live automation."),
]


def main():
    if not SOURCE.exists():
        raise SystemExit(f"Missing source image: {SOURCE}")
    OUT.mkdir(parents=True, exist_ok=True)
    FRAMES.mkdir(parents=True, exist_ok=True)
    for old in FRAMES.glob("*.png"):
        old.unlink()

    src = Image.open(SOURCE).convert("RGB")
    idx = 0
    frames_per_scene = FPS * 5
    for zoom, pan_x, pan_y, title, body in SCENES:
        for frame in range(frames_per_scene):
            t = frame / max(1, frames_per_scene - 1)
            z = zoom * (1 + 0.035 * t)
            img = cover_canvas(src, z, pan_x, pan_y)
            vignette = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            vdraw = ImageDraw.Draw(vignette)
            vdraw.rectangle((0, 0, W, H), outline=(0, 0, 0, 120), width=28)
            img = Image.alpha_composite(img.convert("RGBA"), vignette)
            draw_caption(img, title, body)
            draw_tag(img, "EyePik Inc. Interested Buyer Automation")
            img.convert("RGB").save(FRAMES / f"frame-{idx:04d}.png")
            idx += 1

    subprocess.run([
        "ffmpeg",
        "-y",
        "-framerate",
        str(FPS),
        "-i",
        str(FRAMES / "frame-%04d.png"),
        "-vf",
        "format=yuv420p",
        "-movflags",
        "+faststart",
        str(VIDEO),
    ], check=True)
    print(VIDEO)


if __name__ == "__main__":
    main()
