let currentPopup = null;

// Monitor URL changes
let lastUrl = location.href;
const observer = new MutationObserver(() => {
  if (location.href !== lastUrl) {
    lastUrl = location.href;
    console.log("URL change");
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
  return (
    window.location.pathname.includes("/reels/") ||
    window.location.pathname.includes("/reel/")
  );
}

function getScoreColor(score) {
  if (score <= 50) return "low-score";
  if (score <= 75) return "medium-score";
  return "high-score";
}

async function showPopup() {
  console.log("Started the showPopUp function!");
  if (currentPopup) return;

  var medicalScore = 0;
  // var scoreColor = getScoreColor(medicalScore);
  var needleRotation = medicalScore * 1.8 - 90; // Convert score to degrees (-90 to 90)

  console.log("medical score is " + medicalScore + " " + needleRotation);

  var popup = document.createElement("div");
  popup.className = "reel-alert";
  console.log("Made the div!");
  // popup.innerHTML = `
  //       <div class="dial-container">
  //           <div class="dial-background"><div class="dial-needle" style="transform: rotate(${needleRotation}deg);"></div></div>
  //       </div>
  //       <button id="close-alert">×</button>
  //   `;
  popup.innerHTML = `
    <div class="dial-container">
      <div class="dial-background">
        <div style="display:none;" class="dial-needle" style="transform: rotate(${needleRotation}deg);"></div>
      </div>
      <span style="display: none;" id="percent-number" class="score-percentage"></span>
    </div>
    
    <div class="dropdown-container">
      <div class="dropdown-content">
        <ul id="dropdown-list">
          Loading...
        </ul>
      </div>
      </div>
    </div>
    <button id="close-alert">×</button>
  `;

  document.body.appendChild(popup);
  // try {
  //   const medicalScore = await calculateMedicalAccuracy();
  //   const needleRotation = medicalScore * 1.8 - 90;

  //   // Update the needle rotation
  //   popup.querySelector(
  //     ".dial-needle"
  //   ).style.transform = `rotate(${needleRotation}deg)`;

  //   popup.querySelector("#percent-number").innerHTML = `${medicalScore}`;

  //   // TODO: Update statement content
  // } catch (error) {
  //   console.error("Failed to load medical data:", error);
  //   popup.querySelector(".dropdown-content").innerHTML =
  //     "<p>Could not load medical analysis at this time</p>";
  // }

  // Add dropdown toggle functionality
  const tacho = popup.querySelector(".dial-container");
  const needle = popup.querySelector(".dial-needle");
  const percentNumber = popup.querySelector("#percent-number");
  const dialContainer = popup.querySelector(".dial-container");

  tacho.addEventListener("click", () => {
    popup.classList.toggle("expanded");
    dialContainer.style.height = popup.classList.contains("expanded")
      ? "auto"
      : "40px";
    percentNumber.style.display = popup.classList.contains("expanded")
      ? "block"
      : "none";
  });

  popup.querySelector("#close-alert").addEventListener("click", () => {
    popup.remove();
    currentPopup = null;
  });

  try {
    console.log("Trying to make a  through the backend");
    // Send message to background script
    var data = await chrome.runtime.sendMessage({
      type: "getMedicalScore",
    });
    // if (error) throw new Error(error);

    var statements = data.statements;
    console.log("I got back " + statements[0].text);

    medicalScore = data["overall_truthiness"] * 100;

    needleRotation = medicalScore * 1.8 - 90;

    // Update the needle rotation
    popup.querySelector(".dial-needle").style.display = "block";
    popup.querySelector(
      ".dial-needle"
    ).style.transform = `rotate(${needleRotation}deg)`;

    popup.querySelector("#percent-number").innerHTML = `${medicalScore}%`;
    popup
      .querySelector("#percent-number")
      .classList.add(getScoreColor(medicalScore));

    console.log("Updating the GUI");

    var listContent = popup.querySelector("#dropdown-list");
    console.log("list content: ", listContent);
    listContent.innerHTML = "";

    // TODO: Update statement content
    for (var statement of statements) {
      console.log("statement: " + statement.text);
      let currentContent = listContent.innerHTML;
      listContent.innerHTML =
        currentContent +
        `<li> ${
          statement.verdict == "true"
            ? `<button class="feedback-button" title="Agree with analysis">
      <svg viewBox="0 0 24 24" fill="green">
        <path
          d="M1 21h4V9H1v12zm22-11c0-1.1-.9-2-2-2h-6.31l.95-4.57.03-.32c0-.41-.17-.79-.44-1.06L14.17 1 7.59 7.59C7.22 7.95 7 8.45 7 9v10c0 1.1.9 2 2 2h9c.83 0 1.54-.5 1.84-1.22l3.02-7.05c.09-.23.14-.47.14-.73v-2z"
        />
      </svg></button>`
            : statement.verdict == "false"
            ? `<button class="feedback-button" title="Disagree with analysis">
      <svg viewBox="0 0 24 24" fill="red">
        <path
          d="M15 3H6c-.83 0-1.54.5-1.84 1.22l-3.02 7.05c-.09.23-.14.47-.14.73v2c0 1.1.9 2 2 2h6.31l-.95 4.57-.03.32c0 .41.17.79.44 1.06L9.83 23l6.58-6.59c.37-.36.59-.86.59-1.41V5c0-1.1-.9-2-2-2zm4 0v12h4V3h-4z"
        />
      </svg></button>`
            : `<button class="feedback-button" title="Disagree with analysis">
      <svg viewBox="0 0 24 24" fill="orange" style="transform: rotate(0.25turn)">
        <path
          d="M15 3H6c-.83 0-1.54.5-1.84 1.22l-3.02 7.05c-.09.23-.14.47-.14.73v2c0 1.1.9 2 2 2h6.31l-.95 4.57-.03.32c0 .41.17.79.44 1.06L9.83 23l6.58-6.59c.37-.36.59-.86.59-1.41V5c0-1.1-.9-2-2-2zm4 0v12h4V3h-4z"
        />
      </svg></button>`
        }
      ${statement.text}
      ${
        statement.evidence.length > 0
          ? `<a id="link-icon" class="feedback-button" target="_blank" href=${statement.evidence[0].url}><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><!--!Font Awesome Free 6.7.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc.--><path d="M0 64C0 28.7 28.7 0 64 0L224 0l0 128c0 17.7 14.3 32 32 32l128 0 0 144-208 0c-35.3 0-64 28.7-64 64l0 144-48 0c-35.3 0-64-28.7-64-64L0 64zm384 64l-128 0L256 0 384 128zM176 352l32 0c30.9 0 56 25.1 56 56s-25.1 56-56 56l-16 0 0 32c0 8.8-7.2 16-16 16s-16-7.2-16-16l0-48 0-80c0-8.8 7.2-16 16-16zm32 80c13.3 0 24-10.7 24-24s-10.7-24-24-24l-16 0 0 48 16 0zm96-80l32 0c26.5 0 48 21.5 48 48l0 64c0 26.5-21.5 48-48 48l-32 0c-8.8 0-16-7.2-16-16l0-128c0-8.8 7.2-16 16-16zm32 128c8.8 0 16-7.2 16-16l0-64c0-8.8-7.2-16-16-16l-16 0 0 96 16 0zm80-112c0-8.8 7.2-16 16-16l48 0c8.8 0 16 7.2 16 16s-7.2 16-16 16l-32 0 0 32 32 0c8.8 0 16 7.2 16 16s-7.2 16-16 16l-32 0 0 48c0 8.8-7.2 16-16 16s-16-7.2-16-16l0-64 0-64z"/></svg></a>`
          : ""
      }
  </li>`;
    }
  } catch (error) {
    console.error("Error in content script" + error);
  }

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
