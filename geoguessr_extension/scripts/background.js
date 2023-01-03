async function uploadImage(dataUri, direction, isFinal, tabUrl, cookie) {
	const token = tabUrl.split("/").pop();
	fetch("http://localhost:3000/images", {
		method: "POST",
		headers: { Accept: "application/json", "Content-Type": "application/json" },
		body: JSON.stringify({ image: dataUri, direction, isFinal }),
	})
		.then((response) => response.json())
		.then((data) => {
			console.log("Success:", data);
			if (data.result) {
				// Model has evaluated the image
				chrome.runtime.sendMessage({ msg: "image_evaluated", result: data.result, token: token, cookie: cookie });
			}
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

		// Take a screenshot of the current tab
		const screenshotUri = await chrome.tabs.captureVisibleTab();
		await uploadImage(screenshotUri, request.direction, request.nextDirection === "end", tab.url, request.cookie);

		// Download the screenshot and URL
		chrome.downloads.download({
			url: screenshotUri,
			filename: `screenshot-${tab.url.replace(/[^a-zA-Z0-9]/g, "_")}.png`,
			conflictAction: "uniquify",
		});

		// If this is the last screenshot, don't take another one
		if (request.nextDirection === "end") return;

		chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
			const currentTabId = tabs[0].id;
			chrome.tabs.sendMessage(currentTabId, { msg: `screenshot_content_${request.nextDirection}`, tab: tabs[0] });
		});
	}
});
