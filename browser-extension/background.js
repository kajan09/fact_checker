// chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
//   if (request.type === "NEW_REEL") {
//     handleNewReel(request);
//   }
// });

// async function handleNewReel(reelData) {
//   try {
//     // Get additional metadata
//     const response = await fetch(`http://localhost:8000/api/factcheck`, {
//       method: "POST",
//       headers: { "Content-Type": "application/json" },
//       body: JSON.stringify({
//         reel_url: reelData.reelUrl,
//         reel_id: reelData.reelId,
//         timestamp: reelData.timestamp,
//       }),
//     });

//     const result = await response.json();

//     // Send result back to content script
//     chrome.tabs.sendMessage(sender.tab.id, {
//       type: "FACTCHECK_RESULT",
//       data: result,
//     });
//   } catch (error) {
//     console.error("Factcheck failed:", error);
//   }
// }
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log("got a mesage!");
  if (request.type === "getMedicalScore") {
    // fetch("http://rcbe-srv-001:49064/number", {
    //   mode: "no-cors",
    // })
    //   .then((res) => res.json())
    //   .then((res) => {
    //     console.log("We have a JSON object: " + res + " " + res.number);
    //     sendResponse({ number: res.number });
    //   });

    fetch("http://rcbe-srv-001:49064/process", {
      method: "POST",
      // mode: "no-cors",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        url: "https://www.instagram.com/reels/DJDzRAgNHyv/",
        mock: "true",
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        console.log(data);
        sendResponse(data);
      })
      .catch((error) =>
        console.error("Error at API call in background: " + error)
      );
    // fetchMedicalScore()
    //   .then((score) => sendResponse({ score }))
    //   .catch((error) => sendResponse({ error: error.message }));
    return true; // Keep message channel open for async response
  }
});

async function fetchMedicalScore() {
  try {
    const response = await fetch("http://rcbe-srv-001:49064/number", {
      mode: "no-cors",
    });
    if (!response.ok) throw new Error("API request failed");
    const data = await response.json();
    console.log(data.number);
    return data.number;
  } catch (error) {
    console.error("Background error:", error);
    throw error;
  }
}
