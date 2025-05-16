chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === "NEW_REEL") {
    handleNewReel(request);
  }
});

async function handleNewReel(reelData) {
  try {
    // Get additional metadata
    const response = await fetch(`http://localhost:8000/api/factcheck`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        reel_url: reelData.reelUrl,
        reel_id: reelData.reelId,
        timestamp: reelData.timestamp,
      }),
    });

    const result = await response.json();

    // Send result back to content script
    chrome.tabs.sendMessage(sender.tab.id, {
      type: "FACTCHECK_RESULT",
      data: result,
    });
  } catch (error) {
    console.error("Factcheck failed:", error);
  }
}
