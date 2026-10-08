from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import subprocess
import textwrap

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dist" / "linkedin"
FRAMES = OUT / "frames"
VIDEO = OUT / "eyepik-linkedin-walkthrough-16x9.mp4"
CAPTIONS = OUT / "caption.txt"

W, H = 1920, 1080
FPS = 30
SECONDS_PER_SCENE = 5

INK = "#f8faf7"
MUTED = "#cad4cf"
BG = "#111514"
PANEL = "#1f2523"
ACCENT = "#f47a20"
TEAL = "#42a5a4"
GREEN = "#46b36d"
RED = "#e45151"
LINE = "#3b4541"


def font(size, bold=False):
    names = [
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
    ]
    for name in names:
        if Path(name).exists():
            return ImageFont.truetype(name, size)
    return ImageFont.load_default()


F_TITLE = font(64, True)
F_H2 = font(46, True)
F_BODY = font(32)
F_SMALL = font(24)
F_TAG = font(24, True)
F_NODE = font(24, True)
F_NODE_SMALL = font(20)


def wrap(draw, text, x, y, width, fnt, fill=INK, spacing=12):
    lines = []
    for para in text.split("\n"):
        if not para.strip():
            lines.append("")
            continue
        words = para.split()
        current = ""
        for word in words:
            candidate = (current + " " + word).strip()
            if draw.textbbox((0, 0), candidate, font=fnt)[2] <= width:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += fnt.size + spacing
    return y


def rounded(draw, box, radius=28, fill=PANEL, outline=None, width=2):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def pill(draw, x, y, text, fill=ACCENT):
    pad_x, pad_y = 18, 8
    bbox = draw.textbbox((0, 0), text, font=F_TAG)
    w = bbox[2] - bbox[0] + pad_x * 2
    h = bbox[3] - bbox[1] + pad_y * 2
    rounded(draw, (x, y, x + w, y + h), radius=18, fill=fill)
    draw.text((x + pad_x, y + pad_y - 2), text, font=F_TAG, fill="#101312")


def base():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    for i in range(-H, W, 28):
        draw.line((i, H, i + H, 0), fill="#151b19", width=3)
    draw.rectangle((0, 0, W, H), outline="#202724", width=14)
    return img, draw


def header(draw, eyebrow="EYEPiK INC."):
    pill(draw, 88, 62, eyebrow, TEAL)


def node(draw, x, y, title, sub, color=TEAL):
    rounded(draw, (x, y, x + 225, y + 150), radius=22, fill="#202624", outline=LINE, width=3)
    draw.ellipse((x + 24, y + 24, x + 62, y + 62), fill=color)
    wrap(draw, title, x + 24, y + 72, 180, F_NODE, fill=INK, spacing=3)
    wrap(draw, sub, x + 24, y + 116, 180, F_NODE_SMALL, fill=MUTED, spacing=2)


def arrow(draw, x1, y1, x2, y2):
    draw.line((x1, y1, x2, y2), fill=ACCENT, width=5)
    draw.polygon([(x2, y2), (x2 - 18, y2 - 10), (x2 - 18, y2 + 10)], fill=ACCENT)


def scene(title, body, chips=None, diagram=False, metric=None):
    img, draw = base()
    header(draw)
    y = 145
    y = wrap(draw, title, 88, y, 900, F_TITLE, fill=INK, spacing=16)
    y += 22
    wrap(draw, body, 88, y, 820, F_BODY, fill=MUTED, spacing=12)
    if chips:
        cy = 830
        x = 88
        for chip, color in chips:
            pill(draw, x, cy, chip, color)
            x += draw.textbbox((0, 0), chip, font=F_TAG)[2] + 70
    if metric:
        rounded(draw, (1040, 190, 1790, 630), radius=32, fill="#171d1b", outline=LINE, width=3)
        wrap(draw, metric[0], 1090, 250, 640, F_H2, fill=INK, spacing=8)
        wrap(draw, metric[1], 1090, 335, 610, F_BODY, fill=MUTED, spacing=10)
    if diagram:
        y0 = 700
        xs = [88, 535, 982, 1429]
        data = [
            ("Buyer Form", "interest", ACCENT),
            ("n8n", "routing", TEAL),
            ("Sheets", "tracker", GREEN),
            ("Gmail", "follow-up", RED),
        ]
        for i, (t, s, c) in enumerate(data):
            node(draw, xs[i], y0, t, s, c)
            if i < len(xs) - 1:
                arrow(draw, xs[i] + 225, y0 + 75, xs[i + 1] - 16, y0 + 75)
    draw.text((88, 980), "Buyer form -> n8n -> Google Sheets -> Gmail", font=F_SMALL, fill="#8fa19a")
    return img


SCENES = [
    (
        "Interested buyers should not get lost in messages.",
        "EyePik Inc. captures product interest, budget, size, style preferences, urgency, and contact details in one intake flow.",
        [("Fashion", TEAL), ("Sales", ACCENT), ("Lifestyle", GREEN)],
        False,
        None,
    ),
    (
        "One submission starts the whole workflow.",
        "A shopper sends what they want. The local buyer desk accepts the entry and forwards it to the published n8n workflow.",
        None,
        True,
        None,
    ),
    (
        "The buyer is saved before messages are sent.",
        "The workflow writes a structured row to Google Sheets, so the team has a source of truth before follow-up begins.",
        None,
        False,
        ("Tracker fields", "Name, email, phone, interest, category, budget, size, urgency, segment, priority, status, and next action."),
    ),
    (
        "Intent is segmented automatically.",
        "Ready-to-buy shoppers are marked high priority. Missing sizes or contact details are flagged for follow-up.",
        [("Ready-to-buy", GREEN), ("High priority", ACCENT), ("Missing details flagged", RED)],
        False,
        None,
    ),
    (
        "Sales gets the useful context.",
        "The sales alert includes the product interest, contact details, segment, budget, sizes, flags, and recommended action.",
        None,
        False,
        ("Sales alert", "A clean summary reaches the team without manually checking form entries or spreadsheets."),
    ),
    (
        "Ready-to-buy shoppers enter a personal shopping path.",
        "The workflow waits naturally, sends a personal shopping offer, then updates the tracker after the offer is sent.",
        None,
        True,
        None,
    ),
    (
        "Proof from the live workflow.",
        "The published endpoint accepts production submissions and returns: Workflow was started.",
        [("Published", GREEN), ("Production webhook", TEAL), ("Google Sheets", GREEN)],
        False,
        None,
    ),
    (
        "A cleaner handoff for fashion sales teams.",
        "Instead of chasing scattered buyer interest, EyePik Inc. gets a structured record, faster sales alerts, and a clear next step.",
        [("n8n", ACCENT), ("Google Sheets", GREEN), ("Gmail", RED)],
        False,
        None,
    ),
]

CAPTION_TEXT = """Managing interested buyers should not mean chasing scattered messages.

For EyePik Inc., this workflow turns buyer interest into a structured sales record:

Buyer form -> n8n -> Google Sheets -> Gmail -> follow-up path

It captures shopper details, segments intent, flags missing preferences, alerts the sales team, and routes ready-to-buy shoppers toward a personal shopping offer.

Built with n8n, Google Sheets, and Gmail.

#n8n #workflowautomation #businessautomation #retailautomation #fashiontech #nocode #salesautomation
"""


def main():
    FRAMES.mkdir(parents=True, exist_ok=True)
    for old in FRAMES.glob("*.png"):
        old.unlink()
    for idx, item in enumerate(SCENES, 1):
        img = scene(*item)
        img.save(FRAMES / f"scene-{idx:02d}.png")
    CAPTIONS.write_text(CAPTION_TEXT, encoding="utf-8")

    concat = OUT / "frames.txt"
    with concat.open("w", encoding="utf-8") as f:
        for idx in range(1, len(SCENES) + 1):
            f.write(f"file '{(FRAMES / f'scene-{idx:02d}.png').as_posix()}'\n")
            f.write(f"duration {SECONDS_PER_SCENE}\n")
        f.write(f"file '{(FRAMES / f'scene-{len(SCENES):02d}.png').as_posix()}'\n")

    subprocess.run([
        "ffmpeg",
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(concat),
        "-vf",
        f"fps={FPS},format=yuv420p",
        "-movflags",
        "+faststart",
        str(VIDEO),
    ], check=True)
    print(VIDEO)
    print(CAPTIONS)


if __name__ == "__main__":
    main()
