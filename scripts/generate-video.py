from pathlib import Path
import json
import subprocess

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "dist" / "video"
FRAMES_DIR = OUT_DIR / "frames"
CANVAS = OUT_DIR / "dom-canvas.png"
RECTS = OUT_DIR / "dom-rects.json"
OUTPUT = OUT_DIR / "eyepik-workflow-run-16x9.mp4"
POST_COPY = OUT_DIR / "post-copy.txt"

W, H = 1920, 1080
FPS = 30
CROP_TOP = 54


def font(size, bold=False):
    fonts = [
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]
    for file in fonts:
        if Path(file).exists():
            return ImageFont.truetype(file, size)
    return ImageFont.load_default()


FONT_20 = font(20)
FONT_24 = font(24)
FONT_30 = font(30, True)
FONT_40 = font(40, True)


STEPS = [
    ("Buyer Interest Webhook", "Buyer interest received", "Live buyer submission hits the published webhook."),
    ("Normalize and Segment Buyer", "Fields normalized", "The intake is cleaned and intent is classified."),
    ("Save Buyer to Google Sheet", "Buyer saved", "The tracker receives a structured buyer record."),
    ("Immediate Buyer Confirmation", "Confirmation sent", "The shopper gets an immediate response."),
    ("Alert Sales Team", "Sales team alerted", "The sales team gets product, budget, size, and urgency."),
    ("Ready to Buy?", "Intent branch selected", "Ready-to-buy shoppers continue to the follow-up path."),
    ("Human-like Follow-up Delay", "Follow-up delay", "The next touchpoint waits before sending."),
    ("Send Personal Shopping Offer", "Offer sent", "The shopper receives the personal shopping next step."),
    ("Mark Offer Sent", "Tracker updated", "The record is marked after the follow-up is sent."),
]


def load_capture():
    if not CANVAS.exists() or not RECTS.exists():
        raise FileNotFoundError("Run DOM capture first: dist/video/dom-canvas.png and dom-rects.json are required.")
    source = Image.open(CANVAS).convert("RGB")
    data = json.loads(RECTS.read_text(encoding="utf-8"))
    return source, data


def fit_canvas(source):
    source = source.crop((0, CROP_TOP, source.width, source.height))
    scale = min(W / source.width, H / source.height)
    resized = source.resize((round(source.width * scale), round(source.height * scale)), Image.Resampling.LANCZOS)
    frame = Image.new("RGB", (W, H), (13, 13, 14))
    ox = (W - resized.width) // 2
    oy = (H - resized.height) // 2
    frame.paste(resized, (ox, oy))
    return frame, scale, ox, oy


def map_rect(rect, scale, ox, oy):
    x1 = round(rect["x"] * scale + ox)
    y1 = round((rect["y"] - CROP_TOP) * scale + oy)
    x2 = round((rect["x"] + rect["width"]) * scale + ox)
    y2 = round((rect["y"] + rect["height"] - CROP_TOP) * scale + oy)
    return x1, y1, x2, y2


def node_box(label_rect, scale):
    x1, y1, x2, y2 = label_rect
    cx = (x1 + x2) // 2
    # n8n node icons sit directly above their text labels. Size is derived from the live viewport scale.
    icon_w = round(84 * scale)
    icon_h = round(84 * scale)
    top = y1 - round(100 * scale)
    return cx - icon_w // 2, top, cx + icon_w // 2, top + icon_h


def round_rect(draw, rect, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(rect, radius=radius, fill=fill, outline=outline, width=width)


def check(draw, center, active):
    x, y = center
    r = 24 if active else 19
    fill = (31, 185, 84, 255) if active else (31, 185, 84, 205)
    outline = (214, 255, 229, 255) if active else (31, 185, 84, 240)
    draw.ellipse((x - r, y - r, x + r, y + r), fill=fill, outline=outline, width=3)
    draw.line((x - 10, y, x - 3, y + 8, x + 13, y - 11), fill=(255, 255, 255, 255), width=4)


def lower_third(draw, title, body):
    rect = (112, 860, 1808, 994)
    round_rect(draw, rect, 18, (8, 10, 14, 238), (31, 185, 84), 2)
    draw.text((148, 884), title, font=FONT_40, fill=(255, 255, 255))
    draw.text((148, 936), body, font=FONT_24, fill=(220, 228, 235))


def run_panel(draw, step, total):
    rect = (1232, 136, 1758, 320)
    round_rect(draw, rect, 18, (8, 10, 14, 238), (255, 106, 0), 2)
    draw.ellipse((1262, 166, 1288, 192), fill=(31, 185, 84))
    draw.text((1304, 157), "Published workflow accepted", font=FONT_30, fill=(255, 255, 255))
    lines = [
        "POST /webhook/buyer-interest",
        "Response: Workflow was started",
        f"Execution path: {step}/{total}",
    ]
    for i, line in enumerate(lines):
        draw.text((1266, 214 + i * 32), line, font=FONT_20, fill=(221, 229, 236))


def make_nodes(rect_data, scale, ox, oy):
    labels = rect_data["labels"]
    nodes = {}
    for label, _, _ in STEPS:
        label_rect = map_rect(labels[label], scale, ox, oy)
        icon = node_box(label_rect, scale)
        nodes[label] = {
            "label": label_rect,
            "icon": icon,
            "center": ((icon[0] + icon[2]) // 2, (icon[1] + icon[3]) // 2),
            "badge": (icon[2] - 2, icon[1] + 4),
        }
    return nodes


def scene(base, nodes, step_index):
    active_label, title, body = STEPS[step_index]
    frame = base.convert("RGBA")
    frame = Image.alpha_composite(frame, Image.new("RGBA", (W, H), (0, 0, 0, 18)))
    draw = ImageDraw.Draw(frame, "RGBA")

    for i, (label, _, _) in enumerate(STEPS):
        n = nodes[label]
        done = i < step_index
        active = i == step_index
        if done or active:
            check(draw, n["badge"], active)

    run_panel(draw, step_index + 1, len(STEPS))
    lower_third(draw, title, body)
    return frame.convert("RGB")


def write_frames():
    source, rect_data = load_capture()
    base, scale, ox, oy = fit_canvas(source)
    nodes = make_nodes(rect_data, scale, ox, oy)

    FRAMES_DIR.mkdir(parents=True, exist_ok=True)
    for old in FRAMES_DIR.glob("frame-*.png"):
        old.unlink()

    index = 0
    for step_index in range(len(STEPS)):
        frame = scene(base, nodes, step_index)
        for _ in range(round(2.8 * FPS)):
            frame.save(FRAMES_DIR / f"frame-{index:04d}.png", quality=95)
            index += 1


def encode():
    subprocess.run(
        [
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
        ],
        check=True,
    )


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
    write_frames()
    encode()
    write_post_copy()
    print(f"video={OUTPUT}")


if __name__ == "__main__":
    main()
