// scanner.js — Teachable Machine + webcam + Fetch API

const MODEL_URL = "/static/my_model/";
const PREDICT_ENDPOINT = "/scan/predict";

let model = null;

const video      = document.getElementById("webcam");
const canvas     = document.getElementById("snapshot");
const btnScan    = document.getElementById("btn-scan");
const fileUpload = document.getElementById("file-upload");
const camError   = document.getElementById("camera-error");
const camView    = document.getElementById("camera-viewport");

async function loadModel() {
  try {
    model = await tmImage.load(MODEL_URL + "model.json", MODEL_URL + "metadata.json");
    startCamera();
  } catch (err) {
    console.error("Model load failed:", err);
    showError("Could not load the ML model. Make sure model.json and metadata.json are in /static/my_model/");
  }
}

async function startCamera() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: "environment" }, audio: false,
    });
    video.srcObject = stream;
    video.addEventListener("loadeddata", () => { btnScan.disabled = false; });
  } catch (err) {
    camView.style.display = "none";
    camError.style.display = "flex";
    btnScan.disabled = true;
  }
}

async function runPrediction(imageSource) {
  if (!model) return;
  showLoading();
  let predictions;
  try {
    predictions = await model.predict(imageSource);
  } catch (err) {
    showError("Prediction failed — try again.");
    return;
  }
  const top = predictions.reduce((b, p) => (p.probability > b.probability ? p : b));
  try {
    const resp = await fetch(PREDICT_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ class_name: top.className, confidence: top.probability }),
    });
    renderResult(await resp.json());
  } catch (err) {
    showError("Server error — please try again.");
  }
}

btnScan.addEventListener("click", () => {
  const ctx = canvas.getContext("2d");
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  ctx.drawImage(video, 0, 0);
  runPrediction(canvas);
});

fileUpload.addEventListener("change", (e) => {
  const file = e.target.files[0];
  if (!file) return;
  const img = new Image();
  const url = URL.createObjectURL(file);
  img.onload = () => { URL.revokeObjectURL(url); runPrediction(img); };
  img.src = url;
});

function hideAll() {
  document.getElementById("result-empty").style.display = "none";
  document.getElementById("result-loading").style.display = "none";
  document.getElementById("result-card").style.display = "none";
  document.getElementById("result-error").style.display = "none";
}
function showLoading() { hideAll(); document.getElementById("result-loading").style.display = "flex"; }
function showError(msg) {
  hideAll();
  document.getElementById("result-error-msg").textContent = msg;
  document.getElementById("result-error").style.display = "block";
}
function renderResult(data) {
  hideAll();
  if (!data.success) { showError(data.message); return; }
  const c = data.card;
  document.getElementById("result-name").textContent = c.name;
  const meta = document.getElementById("result-meta");
  meta.innerHTML = "";
  if (c.card_type) meta.innerHTML += `<span class="meta-tag">${c.card_type}</span>`;
  if (c.rarity)    meta.innerHTML += `<span class="meta-tag">${c.rarity}</span>`;
  if (data.confidence) meta.innerHTML += `<span class="meta-tag">${Math.round(data.confidence*100)}% match</span>`;
  document.getElementById("result-desc").textContent = c.description || "";
  document.getElementById("result-owned-badge").style.display = data.already_owned ? "inline-flex" : "none";
  document.getElementById("result-card").style.display = "block";
}

loadModel();
