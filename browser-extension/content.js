let currentPopup = null;

// Monitor URL changes
let lastUrl = location.href;
const observer = new MutationObserver(() => {
  if (location.href !== lastUrl) {
    lastUrl = location.href;
    checkForReel();
  }
});

observer.observe(document, { subtree: true, childList: true });

// Initial check
checkForReel();

function checkForReel() {
  if (isReelUrl()) {
    showPopup();
  } else {
    removePopup();
  }
}

function isReelUrl() {
  return window.location.pathname.includes("/reel/");
}

function calculateMedicalAccuracy() {
  // PLACEHOLDER: Replace this with actual medical fact-checking logic
  // For now, returns random number between 0-100 for demonstration
  return Math.floor(Math.random() * 100);
}

function getScoreColor(score) {
  if (score <= 50) return "low-score";
  if (score <= 75) return "medium-score";
  return "high-score";
}

function showPopup() {
  if (currentPopup) return;

  const medicalScore = calculateMedicalAccuracy();
  const scoreColor = getScoreColor(medicalScore);
  const needleRotation = medicalScore * 1.8 - 90; // Convert score to degrees (-90 to 90)

  const popup = document.createElement("div");
  popup.className = "reel-alert";

  popup.innerHTML = `
        <div class="dial-container">
            <div class="dial-background"><div class="dial-needle" style="transform: rotate(${needleRotation}deg);"></div></div>
        </div>
        <button id="close-alert">×</button>
    `;
  popup.querySelector("#close-alert").addEventListener("click", () => {
    popup.remove();
    currentPopup = null;
  });

  document.body.appendChild(popup);
  currentPopup = popup;

  // Auto-remove after 8 seconds
  // setTimeout(() => {
  //   popup.remove();
  //   currentPopup = null;
  // }, 8000);
}

function removePopup() {
  if (currentPopup) {
    currentPopup.remove();
    currentPopup = null;
  }
}
