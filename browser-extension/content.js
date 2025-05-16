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

  // popup.innerHTML = `
  //       <div class="dial-container">
  //           <div class="dial-background"><div class="dial-needle" style="transform: rotate(${needleRotation}deg);"></div></div>
  //       </div>
  //       <button id="close-alert">×</button>
  //   `;
  popup.innerHTML = `
    <div class="dial-container">
      <div class="dial-background">
        <div class="dial-needle" style="transform: rotate(${needleRotation}deg);"></div>
      </div>
      <span style="display: none;" id="percent-number" class=".score-percentage .${scoreColor}">${medicalScore}%</span>
    </div>
    
    <div class="dropdown-container">
      <div class="dropdown-header">
        <span id="arrow1" class="dropdown-arrow">↓</span>
        </div>
        <div class="dropdown-content">
        <ul>
          <li>Lorem ipsum dolor sit amet <button class="feedback-button" title="Agree with analysis">
            <svg viewBox="0 0 24 24" fill="green">
              <path d="M1 21h4V9H1v12zm22-11c0-1.1-.9-2-2-2h-6.31l.95-4.57.03-.32c0-.41-.17-.79-.44-1.06L14.17 1 7.59 7.59C7.22 7.95 7 8.45 7 9v10c0 1.1.9 2 2 2h9c.83 0 1.54-.5 1.84-1.22l3.02-7.05c.09-.23.14-.47.14-.73v-2z"/>
            </svg>
          </button></li>
          <li>Consectetur adipiscing elit <button class="feedback-button" title="Disagree with analysis">
            <svg viewBox="0 0 24 24" fill="red">
              <path d="M15 3H6c-.83 0-1.54.5-1.84 1.22l-3.02 7.05c-.09.23-.14.47-.14.73v2c0 1.1.9 2 2 2h6.31l-.95 4.57-.03.32c0 .41.17.79.44 1.06L9.83 23l6.58-6.59c.37-.36.59-.86.59-1.41V5c0-1.1-.9-2-2-2zm4 0v12h4V3h-4z"/>
            </svg>
          </button></li>
        </ul>
        <span id="arrow2" style="display: none;" class="dropdown-arrow">↑</span>
      </div>
      </div>
    </div>
    <button id="close-alert">×</button>
  `;

  // Add dropdown toggle functionality
  const dropdownHeader = popup.querySelector(".dropdown-header");
  const dropdownArrow = popup.querySelector("#arrow1");
  const goUpArrow = popup.querySelector("#arrow2");
  const percentNumber = popup.querySelector("#percent-number");
  const dropdownContent = popup.querySelector(".dropdown-content");

  dropdownHeader.addEventListener("click", () => {
    popup.classList.toggle("expanded");
    dropdownArrow.style.display = popup.classList.contains("expanded")
      ? "none"
      : "block";
    goUpArrow.style.display = popup.classList.contains("expanded")
      ? "block"
      : "none";

    percentNumber.style.display = popup.classList.contains("expanded")
      ? "block"
      : "none";
  });

  goUpArrow.addEventListener("click", () => {
    popup.classList.toggle("expanded");
    goUpArrow.style.display = popup.classList.contains("expanded")
      ? "block"
      : "none";

    dropdownArrow.style.display = popup.classList.contains("expanded")
      ? "none"
      : "block";

    percentNumber.style.display = popup.classList.contains("expanded")
      ? "block"
      : "none";
  });
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
