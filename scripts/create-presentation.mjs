import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const workspaceDir = "D:/dev/Automations";
const SKILL_DIR =
  "C:/Users/Miguel/.codex/plugins/cache/openai-primary-runtime/presentations/26.1007.11041/skills/presentations";
const RUNTIME_PYTHON =
  "C:/Users/Miguel/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe";

const TMP_DIR = path.join(workspaceDir, ".presentation-build");
const OUT_DIR = path.join(workspaceDir, "dist", "presentation");
const FINAL_PPTX = path.join(OUT_DIR, "luma-thread-interested-buyer-automation.pptx");
const ASSET_DIR = path.join(OUT_DIR, "assets");

const W = 1280;
const H = 720;
const FONT = "Aptos";

async function readBytes(file) {
  const bytes = await fs.readFile(file);
  return bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
}

function addText(slide, text, position, style = {}) {
  const shape = slide.shapes.add({
    geometry: "textbox",
    position,
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  shape.text = text;
  shape.text.style = {
    fontFamily: FONT,
    fontSize: style.fontSize ?? 24,
    bold: style.bold ?? false,
    color: style.color ?? "1f2528",
    ...style,
  };
  return shape;
}

function addRule(slide, x, y, w, color = "2f6f73") {
  slide.shapes.add({
    geometry: "rect",
    position: { left: x, top: y, width: w, height: 4 },
    fill: color,
    line: { style: "solid", fill: color, width: 0 },
  });
}

function addFooter(slide, number) {
  addText(slide, `0${number}`, { left: 1120, top: 648, width: 80, height: 28 }, {
    fontSize: 15,
    bold: true,
    color: "687176",
  });
}

function addProcess(slide, x, y, labels, activeIndex = -1) {
  const stepW = 130;
  const gap = 18;
  labels.forEach((label, i) => {
    const left = x + i * (stepW + gap);
    const fill = i <= activeIndex ? "eef4f1" : "ffffff";
    const line = i <= activeIndex ? "2f6f73" : "d8dedb";
    slide.shapes.add({
      geometry: "roundRect",
      position: { left, top: y, width: stepW, height: 82 },
      fill,
      line: { style: "solid", fill: line, width: 1.2 },
      borderRadius: "rounded-lg",
    });
    addText(slide, label, { left: left + 14, top: y + 18, width: stepW - 28, height: 42 }, {
      fontSize: 18,
      bold: true,
      color: "1f2528",
    });
  });
}

async function addImage(slide, file, position, fit = "cover") {
  slide.images.add({
    blob: await readBytes(file),
    contentType: "image/png",
    fit,
    position,
    geometry: "roundRect",
    borderRadius: "rounded-xl",
  });
}

async function build() {
  await fs.mkdir(TMP_DIR, { recursive: true });
  await fs.mkdir(OUT_DIR, { recursive: true });

  const presentation = Presentation.create({
    slideSize: { width: W, height: H },
  });

  const dark = "171918";
  const ink = "1f2528";
  const muted = "687176";
  const accent = "2f6f73";
  const rust = "9c4f36";
  const paper = "fbfaf7";

  {
    const slide = presentation.slides.add();
    slide.background.fill = dark;
    addText(slide, "Luma & Thread", { left: 70, top: 58, width: 280, height: 34 }, {
      fontSize: 22,
      bold: true,
      color: "e8efe9",
    });
    addText(slide, "Interested Buyer Automation", { left: 70, top: 168, width: 640, height: 120 }, {
      fontSize: 56,
      bold: true,
      color: "ffffff",
    });
    addText(
      slide,
      "A working buyer intake flow for fashion and lifestyle sales teams.",
      { left: 72, top: 318, width: 560, height: 70 },
      { fontSize: 24, color: "cbd6d0" },
    );
    addRule(slide, 74, 422, 210, accent);
    addProcess(slide, 74, 500, ["Form", "n8n", "Sheets", "Gmail", "Follow-up"], 4);
    addFooter(slide, 1);
  }

  {
    const slide = presentation.slides.add();
    slide.background.fill = paper;
    addText(slide, "Sales intake problem", { left: 66, top: 58, width: 520, height: 50 }, {
      fontSize: 38,
      bold: true,
      color: ink,
    });
    addText(
      slide,
      "Fashion inquiries arrive through messages, comments, product links, and quick forms. The sales team needs the buyer context before the buyer cools off.",
      { left: 68, top: 128, width: 520, height: 120 },
      { fontSize: 24, color: muted },
    );
    addText(slide, "The workflow keeps four things visible:", { left: 68, top: 306, width: 480, height: 36 }, {
      fontSize: 26,
      bold: true,
      color: ink,
    });
    const points = ["Product interest", "Budget and size", "Intent level", "Recommended next action"];
    points.forEach((point, i) => {
      addText(slide, point, { left: 100, top: 366 + i * 48, width: 420, height: 32 }, {
        fontSize: 24,
        color: ink,
      });
      slide.shapes.add({
        geometry: "ellipse",
        position: { left: 70, top: 374 + i * 48, width: 14, height: 14 },
        fill: accent,
        line: { style: "solid", fill: accent, width: 0 },
      });
    });
    addProcess(slide, 650, 204, ["Capture", "Segment", "Save", "Alert"], 3);
    addText(slide, "Outcome", { left: 650, top: 380, width: 380, height: 42 }, {
      fontSize: 30,
      bold: true,
      color: rust,
    });
    addText(
      slide,
      "A shopper record, sales alert, and follow-up path appear from one submission.",
      { left: 650, top: 428, width: 430, height: 92 },
      { fontSize: 24, color: ink },
    );
    addFooter(slide, 2);
  }

  {
    const slide = presentation.slides.add();
    slide.background.fill = "ffffff";
    addText(slide, "Buyer desk", { left: 62, top: 48, width: 520, height: 46 }, {
      fontSize: 38,
      bold: true,
      color: ink,
    });
    addText(
      slide,
      "The form captures product, budget, size, style preference, urgency, and source.",
      { left: 64, top: 104, width: 560, height: 44 },
      { fontSize: 22, color: muted },
    );
    await addImage(slide, path.join(ASSET_DIR, "buyer-desk.png"), {
      left: 64,
      top: 170,
      width: 1120,
      height: 420,
    });
    addText(slide, "Local desk forwards to the published n8n webhook.", {
      left: 72,
      top: 616,
      width: 760,
      height: 32,
    }, { fontSize: 22, bold: true, color: accent });
    addFooter(slide, 3);
  }

  {
    const slide = presentation.slides.add();
    slide.background.fill = dark;
    addText(slide, "n8n workflow backbone", { left: 58, top: 48, width: 600, height: 48 }, {
      fontSize: 38,
      bold: true,
      color: "ffffff",
    });
    addText(
      slide,
      "The workflow records the buyer first, sends the confirmation and sales alert, then routes high-intent shoppers to the personal shopping path.",
      { left: 60, top: 106, width: 760, height: 62 },
      { fontSize: 22, color: "cbd6d0" },
    );
    await addImage(slide, path.join(workspaceDir, "dist", "video", "dom-canvas.png"), {
      left: 54,
      top: 184,
      width: 1172,
      height: 430,
    });
    addFooter(slide, 4);
  }

  {
    const slide = presentation.slides.add();
    slide.background.fill = paper;
    addText(slide, "Run evidence", { left: 66, top: 58, width: 420, height: 48 }, {
      fontSize: 38,
      bold: true,
      color: ink,
    });
    addText(
      slide,
      "The published webhook accepted the buyer submission and returned a started workflow response.",
      { left: 68, top: 122, width: 610, height: 78 },
      { fontSize: 24, color: muted },
    );
    const code = 'POST /webhook/buyer-interest\n{"message":"Workflow was started"}';
    slide.shapes.add({
      geometry: "roundRect",
      position: { left: 70, top: 246, width: 570, height: 150 },
      fill: "171918",
      line: { style: "solid", fill: "171918", width: 0 },
      borderRadius: "rounded-xl",
    });
    addText(slide, code, { left: 104, top: 284, width: 510, height: 82 }, {
      fontSize: 25,
      color: "e9f2ed",
      fontFamily: "Consolas",
    });
    addProcess(slide, 70, 478, ["Buyer", "Tracker", "Email", "Offer"], 3);
    await addImage(slide, path.join(workspaceDir, "dist", "video", "frames", "frame-0252.png"), {
      left: 724,
      top: 128,
      width: 430,
      height: 360,
    });
    addText(slide, "Video asset shows the node path with executed checks.", {
      left: 724,
      top: 526,
      width: 420,
      height: 52,
    }, { fontSize: 22, color: ink });
    addFooter(slide, 5);
  }

  {
    const slide = presentation.slides.add();
    slide.background.fill = "ffffff";
    addText(slide, "Presentation links", { left: 70, top: 60, width: 520, height: 52 }, {
      fontSize: 40,
      bold: true,
      color: ink,
    });
    addText(slide, "Open the live page, play the workflow video, or download this deck from the repository.", {
      left: 72,
      top: 126,
      width: 700,
      height: 68,
    }, { fontSize: 24, color: muted });
    const items = [
      ["Live page", "https://calina-miguel.github.io/fashion-buyer-automation/"],
      ["Repository", "https://github.com/calina-miguel/fashion-buyer-automation"],
      ["Workflow", "https://devtones.app.n8n.cloud/workflow/anSd0GnuD9zYGiLD"],
    ];
    items.forEach(([title, url], i) => {
      const top = 250 + i * 94;
      addText(slide, title, { left: 92, top, width: 240, height: 32 }, {
        fontSize: 27,
        bold: true,
        color: rust,
      });
      addText(slide, url, { left: 92, top: top + 38, width: 920, height: 34 }, {
        fontSize: 21,
        color: ink,
      });
      addRule(slide, 92, top + 82, 760, "d8dedb");
    });
    addFooter(slide, 6);
  }

  for (const [index, slide] of presentation.slides.items.entries()) {
    const png = await presentation.export({ slide, format: "png", scale: 1 });
    await fs.writeFile(
      path.join(TMP_DIR, `slide-${String(index + 1).padStart(2, "0")}.png`),
      new Uint8Array(await png.arrayBuffer()),
    );
  }

  const { finalizePresentation } = await import(
    pathToFileURL(path.join(SKILL_DIR, "container_tools/artifact_tool_utils.mjs")).href
  );
  const stagingDir = path.join(workspaceDir, ".codex-finalizer");
  await fs.mkdir(stagingDir, { recursive: true });
  const candidatePath = path.join(stagingDir, "presentation-candidate.pptx");
  await (await PresentationFile.exportPptx(presentation)).save(candidatePath);

  await finalizePresentation({
    explicitTotalSlideCount: 6,
    requiredNativeTableOwnerSlides: [],
    requiredNativeChartOwnerSlides: [],
    workspaceDir,
    candidatePath,
    finalPath: FINAL_PPTX,
    pythonExecutable: RUNTIME_PYTHON,
    integrityValidatorPath: path.join(SKILL_DIR, "container_tools/inspect_presentation_package_integrity.py"),
    layoutValidatorPath: path.join(SKILL_DIR, "container_tools/inspect_presentation_layout_geometry.py"),
    layoutArgs: [
      "--expected-slide-size-emu",
      "12192000,6858000",
      "--validate-heading-fit",
    ],
    fontPolicy: { basis: "design", families: [FONT, "Consolas"] },
    verifyArtifactToolImport: true,
    receiptPath: path.join(stagingDir, "luma-thread-presentation.validation.json"),
  });

  console.log(FINAL_PPTX);
}

build().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
