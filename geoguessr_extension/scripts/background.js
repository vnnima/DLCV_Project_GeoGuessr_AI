async function upload(file, direction, isFinal) {
	fetch("http://localhost:3000/images", {
		method: "POST",
		headers: { Accept: "application/json", "Content-Type": "application/json" },
		// body: formData,
		body: JSON.stringify({ image: dataUrl, direction, isFinal }),
	})
		.then((response) => response.json())
		.then((data) => {
			console.log("Success:", data);
		})
		.catch((error) => {
			console.log("Error:", error);
		});
}

chrome.runtime.onMessage.addListener(async (request) => {
	if (request.msg == "screenshot") {
		// Get the current tab
		const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
		const tab = tabs[0];

		if (tab?.url?.startsWith("chrome://")) return undefined;
		if (tab?.url?.startsWith("devtools://")) return undefined;

		chrome.tabs.captureVisibleTab(null, { format: "png" }, (dataUrl) => {
			console.log(dataUrl);
		});

		// // Take a screenshot of the current tab
		const screenshotUri = await chrome.tabs.captureVisibleTab();
		await upload(screenshotUri, request.direction, request.nextDirection === "end");

		// Download the screenshot and URL
		chrome.downloads.download({
			url: screenshotUri,
			filename: `screenshot-${tab.url.replace(/[^a-zA-Z0-9]/g, "_")}.png`,
			conflictAction: "uniquify",
		});

		// send message to content script
		chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
			const currentTabId = tabs[0].id;
			chrome.tabs.sendMessage(currentTabId, { msg: `screenshot_content_${request.nextDirection}`, tab: tabs[0] });
		});
	}
});
