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
        <div class="dial-needle" style="transform: rotate(${needleRotation}deg);"></div>
      </div>
      <span style="display: none;" id="percent-number" class="score-percentage">${medicalScore}%</span>
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
            : `<button class="feedback-button" title="Undecided">
  <svg viewBox="0 0 24 24" fill="gray">
    <path d="M6 11h12v2H6z"/>
  </svg>
</button>`
        }
      ${statement.text}
      ${
        statement.evidence.length > 0
          ? `<a target="_blank" href=${statement.evidence[0].url}>📎</a>`
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
