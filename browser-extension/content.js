// Detect Instagram Reel videos
console.log("content script loaded");
const observer = new MutationObserver(() => {
  const reel = document.querySelector('div[role="main"] video');
  console.log("Reel is there!");
  if (reel && !reel.dataset.factcheckAdded) {
    reel.dataset.factcheckAdded = true;
    handleNewReel(reel);
  }
});

observer.observe(document, { subtree: true, childList: true });

async function handleNewReel(videoElement) {
  // Get reel metadata
  const reelId = getReelId();
  const reelUrl = window.location.href;

  // Create overlay element
  const overlay = createOverlay();
  videoElement.parentElement.appendChild(overlay);

  // Send data to background script
  chrome.runtime.sendMessage({
    type: "NEW_REEL",
    reelId,
    reelUrl,
    timestamp: Date.now(),
  });
}

function getReelId() {
  const url = new URL(window.location.href);
  return url.pathname.split("/")[2];
}

function createOverlay() {
  const overlay = document.createElement("div");
  overlay.className = "factcheck-overlay";
  overlay.innerHTML = `
    <div class="loading-spinner"></div>
    <div class="result-content"></div>
  `;
  return overlay;
}

// Listen for results from background script
// chrome.runtime.onMessage.addListener((message) => {
//   if (message.type === 'FACTCHECK_RESULT') {
//     updateOverlay(message.data);
//   }
// });

// function updateOverlay(data) {
//   const overlay = document.querySelector('.factcheck-overlay');
//   overlay.querySelector('.loading-spinner').style.display = 'none';
//   overlay.querySelector('.result-content').innerHTML = `
//     <div class="verdict ${data.verdict.toLowerCase()}">${data.verdict}</div>
//     <div class="confidence">Confidence: ${data.confidence}%</div>
//     <div class="explanation">${data.explanation}</div>
//     ${data.sources ? `<div class="sources">Sources: ${data.sources.join(', ')}</div>` : ''}
//   `;
// }
