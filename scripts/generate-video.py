from pathlib import Path
import math
import subprocess

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
SOURCE_CANDIDATES = [
    Path(r"C:\Users\Miguel\AppData\Local\Temp\codex-clipboard-bd483857-205f-4d0c-af07-d253b0cb1de2.png"),
    ROOT / "n8n-workflow-imported.png",
]
OUT_DIR = ROOT / "dist" / "video"
FRAMES_DIR = OUT_DIR / "frames"
OUTPUT = OUT_DIR / "eyepik-workflow-run-16x9.mp4"
POST_COPY = OUT_DIR / "post-copy.txt"

W, H = 1920, 1080
FPS = 30


def font(size, bold=False):
    names = [
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]
    for name in names:
        if Path(name).exists():
            return ImageFont.truetype(name, size)
    return ImageFont.load_default()


FONT_28 = font(28)
FONT_34 = font(34, True)
FONT_42 = font(42, True)


def find_source():
    for path in SOURCE_CANDIDATES:
        if path.exists():
            return path
    raise FileNotFoundError("No workflow canvas image found.")


def cover_canvas(source):
    img = Image.open(source).convert("RGB")
    scale = max(W / img.width, H / img.height)
    resized = img.resize((round(img.width * scale), round(img.height * scale)), Image.Resampling.LANCZOS)
    x = (resized.width - W) // 2
    y = (resized.height - H) // 2
    return resized.crop((x, y, x + W, y + H))


def rounded_rect(draw, box, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def text_size(draw, text, fnt):
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0], box[3] - box[1]


def label(draw, xy, title, body=None):
    x, y = xy
    pad_x, pad_y = 26, 20
    tw, th = text_size(draw, title, FONT_42)
    bw, bh = (0, 0)
    if body:
        bw, bh = text_size(draw, body, FONT_28)
    width = max(tw, bw) + pad_x * 2
    height = th + pad_y * 2 + (bh + 10 if body else 0)
    rounded_rect(draw, (x, y, x + width, y + height), 14, (9, 12, 18, 232), (53, 214, 135), 2)
    draw.text((x + pad_x, y + pad_y - 3), title, font=FONT_42, fill=(255, 255, 255))
    if body:
        draw.text((x + pad_x, y + pad_y + th + 10), body, font=FONT_28, fill=(206, 218, 226))


def status_panel(draw, lines):
    x, y, width = 1080, 146, 650
    line_h = 42
    height = 78 + len(lines) * line_h
    rounded_rect(draw, (x, y, x + width, y + height), 18, (12, 15, 21, 238), (255, 106, 0), 2)
    draw.ellipse((x + 28, y + 28, x + 50, y + 50), fill=(29, 185, 84))
    draw.text((x + 66, y + 19), "Workflow run verified", font=FONT_34, fill=(255, 255, 255))
    for i, line in enumerate(lines):
        draw.text((x + 34, y + 76 + i * line_h), line, font=FONT_28, fill=(221, 231, 238))


def highlight(draw, box, color=(255, 106, 0), label_text=None):
    x1, y1, x2, y2 = box
    for expand, alpha in [(24, 55), (14, 90), (4, 255)]:
        draw.rounded_rectangle(
            (x1 - expand, y1 - expand, x2 + expand, y2 + expand),
            radius=18,
            outline=color + (alpha,),
            width=5,
        )
    if label_text:
        draw.text((x1 - 20, y1 - 70), label_text, font=FONT_34, fill=(255, 255, 255))


def dim_and_highlight(base, boxes, title, body, status_lines=None):
    frame = base.convert("RGBA")
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 108))
    frame = Image.alpha_composite(frame, overlay)
    draw = ImageDraw.Draw(frame, "RGBA")
    for box in boxes:
        highlight(draw, box)
    label(draw, (96, 96), title, body)
    if status_lines:
        status_panel(draw, status_lines)
    return frame.convert("RGB")


def full_frame(base, title, body, status_lines=None):
    frame = base.convert("RGBA")
    draw = ImageDraw.Draw(frame, "RGBA")
    label(draw, (96, 96), title, body)
    if status_lines:
        status_panel(draw, status_lines)
    return frame.convert("RGB")


def make_frames(base):
    # Coordinates are tuned to the supplied 16:9 n8n canvas screenshot after cover-scaling.
    webhook = (424, 510, 520, 604)
    normalize = (610, 510, 702, 604)
    sheet = (770, 510, 864, 604)
    confirm = (920, 450, 1010, 544)
    alert = (920, 608, 1010, 702)
    decision = (1090, 510, 1180, 604)
    delay = (1262, 452, 1352, 544)
    offer = (1425, 452, 1515, 544)
    mark_sent = (1588, 452, 1678, 544)

    scenes = [
        (
            full_frame(
                base,
                "EyePik Inc. Interested Buyer Automation",
                "Published workflow ready for live buyer intake.",
            ),
            3.0,
        ),
        (
            dim_and_highlight(
                base,
                [webhook],
                "Buyer interest submitted",
                "The intake form sends a POST request to the live n8n webhook.",
                ["POST /webhook/buyer-interest", "Response: {\"message\":\"Workflow was started\"}"],
            ),
            5.0,
        ),
        (
            dim_and_highlight(
                base,
                [normalize, sheet],
                "Buyer record prepared",
                "Field names are cleaned, intent is segmented, then the buyer is saved.",
                ["Segment: Ready-to-buy", "Priority: High", "Tracker update accepted"],
            ),
            5.0,
        ),
        (
            dim_and_highlight(
                base,
                [confirm, alert],
                "Confirmation and sales alert sent",
                "The shopper gets reassurance while the sales team receives the full context.",
                ["Shopper confirmation queued", "Sales alert queued", "Product, budget, size, urgency included"],
            ),
            5.0,
        ),
        (
            dim_and_highlight(
                base,
                [decision],
                "Ready-to-buy branch selected",
                "High-intent buyers continue into a personal shopping follow-up path.",
                ["Condition matched", "Buyer routed to follow-up"],
            ),
            4.0,
        ),
        (
            dim_and_highlight(
                base,
                [delay, offer, mark_sent],
                "Follow-up path completed",
                "The offer is sent after a natural delay and the tracker is updated.",
                ["Personal shopping offer queued", "Offer status marked sent", "Verified Oct 8, 2026"],
            ),
            6.0,
        ),
        (
            full_frame(
                base,
                "Live workflow verified",
                "Form -> n8n -> Google Sheets -> Gmail -> follow-up path.",
                ["Production webhook accepted the buyer submission", "Workflow run returned: started"],
            ),
            4.0,
        ),
    ]

    FRAMES_DIR.mkdir(parents=True, exist_ok=True)
    for old in FRAMES_DIR.glob("frame-*.png"):
        old.unlink()

    idx = 0
    total_frames = sum(round(scene[1] * FPS) for scene in scenes)
    for image, seconds in scenes:
        count = round(seconds * FPS)
        for i in range(count):
            # Subtle opacity pulse on highlighted scenes, with no camera shake.
            frame = image.copy().convert("RGBA")
            pulse = 0.5 + 0.5 * math.sin(i / FPS * math.pi * 2)
            draw = ImageDraw.Draw(frame, "RGBA")
            progress_w = round(W * (idx / max(1, total_frames)))
            draw.rectangle((0, H - 8, progress_w, H), fill=(255, 106, 0, 210))
            if pulse > 0.92:
                glow = Image.new("RGBA", (W, H), (255, 106, 0, 0))
                frame = Image.alpha_composite(frame, glow)
            frame.convert("RGB").save(FRAMES_DIR / f"frame-{idx:04d}.png", quality=95)
            idx += 1


def encode_video():
    cmd = [
        "ffmpeg",
        "-y",
        "-framerate",
        str(FPS),
        "-i",
        str(FRAMES_DIR / "frame-%04d.png"),
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        str(OUTPUT),
    ]
    subprocess.run(cmd, check=True)


def write_post_copy():
    POST_COPY.write_text(
        "\n".join(
            [
                "Interested buyers move fast. The sales workflow has to move with them.",
                "",
                "For EyePik Inc., this automation turns each fashion and lifestyle inquiry into a clean sales record:",
                "",
                "Buyer form -> n8n -> Google Sheets -> Gmail -> follow-up path",
                "",
                "It captures the shopper's product interest, budget, size, style preferences, and urgency; segments intent; flags missing details; alerts the sales team; and routes ready-to-buy buyers toward a personal shopping offer.",
                "",
                "Built with n8n, Google Sheets, and Gmail.",
                "",
                "#n8n #workflowautomation #businessautomation #retailautomation #fashiontech #nocode #salesautomation",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    source = find_source()
    base = cover_canvas(source)
    make_frames(base)
    encode_video()
    write_post_copy()
    print(f"source={source}")
    print(f"video={OUTPUT}")
    print(f"post_copy={POST_COPY}")


if __name__ == "__main__":
    main()
