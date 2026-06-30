const apiBase = "http://127.0.0.1:8000/api/v1";
const uploadForm = document.querySelector("#uploadForm");
const imageInput = document.querySelector("#imageInput");
const preview = document.querySelector("#preview");
const result = document.querySelector("#result");
const statusPill = document.querySelector("#statusPill");
const historyBody = document.querySelector("#historyBody");
const refreshHistory = document.querySelector("#refreshHistory");
const sampleGrid = document.querySelector("#sampleGrid");
const runAllSamples = document.querySelector("#runAllSamples");

const demoSamples = [
  {
    slug: "clear-front",
    title: "Clear front plate",
    expectedPlate: "TXABC1234",
    body: "#58798b",
    backdrop: "#dbe9ef",
    plate: "TXABC1234",
    plateAngle: 0,
    plateX: 440,
    plateY: 470,
    mode: "normal",
  },
  {
    slug: "slight-angle",
    title: "Slight angle",
    expectedPlate: "CA8ZP219",
    body: "#745b93",
    backdrop: "#e5e4da",
    plate: "CA8ZP219",
    plateAngle: -4,
    plateX: 455,
    plateY: 468,
    mode: "normal",
  },
  {
    slug: "low-light",
    title: "Low light",
    expectedPlate: "NYC2048",
    body: "#40515f",
    backdrop: "#1f2a33",
    plate: "NYC2048",
    plateAngle: 0,
    plateX: 444,
    plateY: 470,
    mode: "night",
  },
  {
    slug: "noisy-plate",
    title: "Noisy plate",
    expectedPlate: "FLM5R812",
    body: "#7c6d54",
    backdrop: "#d8dde0",
    plate: "FLM5R812",
    plateAngle: 2,
    plateX: 442,
    plateY: 470,
    mode: "noisy",
  },
  {
    slug: "no-visible-plate",
    title: "No visible plate",
    expectedPlate: "None",
    body: "#637074",
    backdrop: "#d7e3e7",
    plate: "",
    plateAngle: 0,
    plateX: 0,
    plateY: 0,
    mode: "normal",
  },
];

imageInput.addEventListener("change", () => {
  const file = imageInput.files[0];
  if (!file) return;
  preview.src = URL.createObjectURL(file);
  preview.hidden = false;
});

uploadForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const file = imageInput.files[0];
  if (!file) {
    setStatus("Choose an image", false);
    return;
  }

  await recognizeFile(file);
});

refreshHistory.addEventListener("click", loadHistory);
runAllSamples.addEventListener("click", runAllDemoSamples);

async function recognizeFile(file, sample = null) {
  const data = new FormData();
  data.append("file", file);
  setStatus("Processing", false);
  result.className = "result-empty";
  result.textContent = "Running detection and OCR...";
  preview.src = URL.createObjectURL(file);
  preview.hidden = false;

  try {
    const response = await fetch(`${apiBase}/recognize/image`, {
      method: "POST",
      body: data,
    });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.detail || "Recognition failed");
    renderResult(payload);
    if (sample) renderSampleResult(sample, payload);
    await loadHistory();
  } catch (error) {
    setStatus("Failed", false);
    result.className = "result-empty";
    result.textContent = error.message;
    if (sample) renderSampleError(sample, error);
  }
}

async function loadDemoSamples() {
  for (const sample of demoSamples) {
    sample.image = await createSampleDataUrl(sample);
  }
  sampleGrid.innerHTML = demoSamples.map(renderSampleCard).join("");
  sampleGrid.querySelectorAll("[data-sample]").forEach((button) => {
    button.addEventListener("click", () => runDemoSample(button.dataset.sample));
  });
}

function renderSampleCard(sample) {
  return `
    <article class="sample-card">
      <img src="${sample.image}" alt="${escapeHtml(sample.title)} demo image">
      <div class="sample-body">
        <div>
          <h3>${escapeHtml(sample.title)}</h3>
          <span>Expected: ${escapeHtml(sample.expectedPlate)}</span>
        </div>
        <button class="sample-action" type="button" data-sample="${escapeHtml(sample.slug)}">Try</button>
      </div>
      <div id="sample-result-${escapeHtml(sample.slug)}" class="sample-result">Not run yet</div>
    </article>
  `;
}

async function runDemoSample(slug) {
  const sample = demoSamples.find((item) => item.slug === slug);
  if (!sample) return;

  const blob = await createSampleBlob(sample);
  const file = new File([blob], `${sample.slug}.png`, { type: "image/png" });
  await recognizeFile(file, sample);
}

async function runAllDemoSamples() {
  runAllSamples.disabled = true;
  for (const sample of demoSamples) {
    await runDemoSample(sample.slug);
  }
  runAllSamples.disabled = false;
}

function renderResult(record) {
  const success = record.status === "success";
  setStatus(record.status.replaceAll("_", " "), success);
  result.className = "result-grid";
  result.innerHTML = `
    <div class="result-main">${escapeHtml(record.plate_number || "No plate")}</div>
    <div>${escapeHtml(record.message)}</div>
    ${record.plate_crop_path ? `<img class="crop-preview" src="${toUploadUrl(record.plate_crop_path)}" alt="Detected plate crop">` : ""}
    <div class="meta-grid">
      ${meta("Detection", percent(record.detection_confidence))}
      ${meta("OCR", percent(record.ocr_confidence))}
      ${meta("Processing", `${record.processing_time_ms} ms`)}
      ${meta("Model", record.model_version)}
    </div>
  `;
}

function renderSampleResult(sample, record) {
  const node = document.querySelector(`#sample-result-${sample.slug}`);
  if (!node) return;
  const expected = sample.expectedPlate === "None" ? "" : sample.expectedPlate;
  const recognized = record.plate_number || "";
  const matched = expected ? expected === recognized : record.status === "no_plate_detected";
  node.className = `sample-result ${matched ? "match" : "miss"}`;
  node.textContent = `Got ${recognized || record.status} (${matched ? "match" : "review"})`;
}

function renderSampleError(sample, error) {
  const node = document.querySelector(`#sample-result-${sample.slug}`);
  if (!node) return;
  node.className = "sample-result miss";
  node.textContent = error.message;
}

async function createSampleDataUrl(sample) {
  const canvas = drawSample(sample);
  return canvas.toDataURL("image/png");
}

async function createSampleBlob(sample) {
  const canvas = drawSample(sample);
  return new Promise((resolve) => canvas.toBlob(resolve, "image/png"));
}

function drawSample(sample) {
  const canvas = document.createElement("canvas");
  canvas.width = 1200;
  canvas.height = 760;
  const ctx = canvas.getContext("2d");
  const night = sample.mode === "night";

  ctx.fillStyle = sample.backdrop;
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = night ? "#11181e" : "#b8c2c8";
  ctx.fillRect(0, 548, canvas.width, 212);
  drawRoad(ctx, night);
  drawVehicle(ctx, sample, night);
  if (sample.mode === "noisy") drawNoise(ctx, 0.18);
  if (night) drawNightOverlay(ctx);
  drawSampleLabel(ctx, sample, night);
  return canvas;
}

function drawRoad(ctx, night) {
  ctx.beginPath();
  ctx.moveTo(0, 598);
  ctx.bezierCurveTo(230, 560, 390, 590, 574, 560);
  ctx.bezierCurveTo(760, 528, 920, 568, 1200, 532);
  ctx.lineTo(1200, 760);
  ctx.lineTo(0, 760);
  ctx.closePath();
  ctx.fillStyle = night ? "#151f27" : "#9faeb6";
  ctx.fill();
}

function drawVehicle(ctx, sample, night) {
  ctx.save();
  ctx.shadowColor = "rgba(18,32,42,0.26)";
  ctx.shadowBlur = 28;
  ctx.shadowOffsetY = 18;
  roundedPath(ctx, 214, 250, 830, 312, 28);
  ctx.fillStyle = sample.body;
  ctx.fill();
  ctx.restore();

  ctx.beginPath();
  ctx.moveTo(382, 306);
  ctx.bezierCurveTo(424, 270, 482, 264, 554, 264);
  ctx.lineTo(728, 264);
  ctx.bezierCurveTo(810, 266, 866, 286, 910, 346);
  ctx.lineTo(940, 406);
  ctx.lineTo(334, 406);
  ctx.closePath();
  ctx.fillStyle = night ? "#25323b" : "#c6d5dd";
  ctx.fill();

  ctx.beginPath();
  ctx.moveTo(335, 406);
  ctx.lineTo(934, 406);
  ctx.lineTo(978, 492);
  ctx.lineTo(290, 492);
  ctx.closePath();
  ctx.fillStyle = sample.body;
  ctx.globalAlpha = 0.92;
  ctx.fill();
  ctx.globalAlpha = 1;

  roundedRect(ctx, 308, 492, 640, 74, 22, "rgba(38,50,58,0.34)");
  drawWheel(ctx, 374, 560);
  drawWheel(ctx, 875, 560);
  roundedRect(ctx, 290, 430, 122, 42, 14, night ? "#ffe5a0" : "#fff4c3");
  roundedRect(ctx, 838, 430, 122, 42, 14, night ? "#ffe5a0" : "#fff4c3");

  if (sample.plate) {
    drawPlate(ctx, sample);
  }
}

function drawWheel(ctx, x, y) {
  ctx.fillStyle = "#20272d";
  ctx.beginPath();
  ctx.ellipse(x, y, 84, 84, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillStyle = "#6e7c83";
  ctx.beginPath();
  ctx.ellipse(x, y, 42, 42, 0, 0, Math.PI * 2);
  ctx.fill();
}

function drawPlate(ctx, sample) {
  ctx.save();
  ctx.translate(sample.plateX + 159, sample.plateY + 41);
  ctx.rotate((sample.plateAngle * Math.PI) / 180);
  ctx.translate(-159, -41);
  ctx.filter = sample.mode === "noisy" ? "blur(0.8px)" : "none";
  roundedRect(ctx, 0, 0, 318, 82, 10, "#f8faf7", "#14191c", 5);
  roundedRect(ctx, 12, 10, 42, 62, 5, "#176b87");
  ctx.fillStyle = "#ffffff";
  ctx.font = "700 22px Arial, Helvetica, sans-serif";
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillText("US", 33, 41);
  ctx.fillStyle = "#111619";
  ctx.font = "800 44px Arial, Helvetica, sans-serif";
  ctx.textAlign = "left";
  ctx.fillText(sample.plate, 68, 45);
  if (sample.mode === "noisy") drawNoise(ctx, 0.20, 0, 0, 318, 82);
  ctx.restore();
  ctx.filter = "none";
}

function drawNoise(ctx, alpha, x = 0, y = 0, width = 1200, height = 760) {
  ctx.save();
  ctx.globalAlpha = alpha;
  for (let row = y; row < y + height; row += 18) {
    for (let col = x; col < x + width; col += 18) {
      ctx.fillStyle = "#1b252b";
      ctx.fillRect(col + 3, row + 4, 2, 2);
      ctx.fillStyle = "#ffffff";
      ctx.fillRect(col + 12, row + 9, 2, 2);
    }
  }
  ctx.restore();
}

function drawNightOverlay(ctx) {
  ctx.fillStyle = "rgba(7,16,25,0.32)";
  ctx.fillRect(0, 0, 1200, 760);
  ctx.fillStyle = "rgba(255,228,154,0.13)";
  ctx.beginPath();
  ctx.arc(350, 450, 86, 0, Math.PI * 2);
  ctx.arc(900, 450, 86, 0, Math.PI * 2);
  ctx.fill();
}

function drawSampleLabel(ctx, sample, night) {
  ctx.fillStyle = night ? "#d7e4eb" : "#26323a";
  ctx.font = "700 28px Arial, Helvetica, sans-serif";
  ctx.fillText(sample.title, 38, 62);
  ctx.fillStyle = night ? "#9fb3bf" : "#5b6972";
  ctx.font = "20px Arial, Helvetica, sans-serif";
  ctx.fillText(`Expected: ${sample.expectedPlate}`, 38, 98);
}

function roundedRect(ctx, x, y, width, height, radius, fill, stroke = null, strokeWidth = 1) {
  roundedPath(ctx, x, y, width, height, radius);
  ctx.fillStyle = fill;
  ctx.fill();
  if (stroke) {
    ctx.lineWidth = strokeWidth;
    ctx.strokeStyle = stroke;
    ctx.stroke();
  }
}

function roundedPath(ctx, x, y, width, height, radius) {
  ctx.beginPath();
  ctx.moveTo(x + radius, y);
  ctx.lineTo(x + width - radius, y);
  ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
  ctx.lineTo(x + width, y + height - radius);
  ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
  ctx.lineTo(x + radius, y + height);
  ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
  ctx.lineTo(x, y + radius);
  ctx.quadraticCurveTo(x, y, x + radius, y);
  ctx.closePath();
}

async function loadHistory() {
  try {
    const response = await fetch(`${apiBase}/detections`);
    const records = await response.json();
    historyBody.innerHTML = records.length
      ? records.map(renderHistoryRow).join("")
      : `<tr><td colspan="5">No detections yet.</td></tr>`;
  } catch {
    historyBody.innerHTML = `<tr><td colspan="5">Backend is not reachable.</td></tr>`;
  }
}

function renderHistoryRow(record) {
  return `
    <tr>
      <td>${escapeHtml(record.plate_number || "-")}</td>
      <td>${escapeHtml(record.status)}</td>
      <td>${percent(record.detection_confidence)}</td>
      <td>${percent(record.ocr_confidence)}</td>
      <td>${new Date(record.created_at).toLocaleString()}</td>
    </tr>
  `;
}

function meta(label, value) {
  return `
    <div class="meta-item">
      <span class="meta-label">${escapeHtml(label)}</span>
      <span class="meta-value">${escapeHtml(value)}</span>
    </div>
  `;
}

function setStatus(text, success) {
  statusPill.textContent = text;
  statusPill.classList.toggle("success", success);
}

function percent(value) {
  return `${Math.round((Number(value) || 0) * 100)}%`;
}

function toUploadUrl(path) {
  const marker = "uploads/";
  const index = path.indexOf(marker);
  return index >= 0 ? `http://127.0.0.1:8000/${path.slice(index)}` : path;
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;",
  })[char]);
}

loadHistory();
loadDemoSamples();
