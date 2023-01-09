async function uploadImage(dataUri, direction) {
	try {
		const response = await fetch("http://localhost:3000/save-image", {
			method: "POST",
			headers: { Accept: "application/json", "Content-Type": "application/json" },
			body: JSON.stringify({ image: dataUri, direction }),
		});
		const data = await response.json();
		console.log("Success:", data);
		return data;
	} catch (error) {
		console.log("Error:", error);
	}
}

chrome.runtime.onMessage.addListener(async (request) => {
	if (request.msg == "screenshot") {
		// Get the current tab
		const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
		const tab = tabs[0];
		const tabUrl = tab.url;
		const token = tabUrl.split("/").pop();
		const cookie = request.cookie;
		console.log(cookie);

		if (tab?.url?.startsWith("chrome://")) return undefined;
		if (tab?.url?.startsWith("devtools://")) return undefined;

		// Take a screenshot of the current tab
		const screenshotUri = await chrome.tabs.captureVisibleTab();
		const callModel = request.nextDirection === "end" && !request.createImage;
		const collectData = request.nextDirection === "end" && request.createImage;

		const data = await uploadImage(screenshotUri, request.direction, callModel, request.cookie, collectData);

		// Download the screenshot and URL
		if (request.download) {
			chrome.downloads.download({
				url: screenshotUri,
				filename: `screenshot-${tab.url.replace(/[^a-zA-Z0-9]/g, "_")}.png`,
				conflictAction: "uniquify",
			});
		}

		// If this is the last screenshot, don't take another one
		if (request.nextDirection !== "end") {
			chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
				const currentTabId = tabs[0].id;
				chrome.tabs.sendMessage(currentTabId, { msg: `screenshot_content_${request.nextDirection}`, tab: tabs[0], mode: request.mode });
			});
		}

		if (request.nextDirection !== "end") return;

		if (request.mode === "create-image") {
			// You have to add the cookie to the document for the API to work
			chrome.runtime.sendMessage({
				msg: "create_image",
				cookie: cookie,
				token: token,
			});
		} else if (request.mode === "evaluate-image") {
			const res = await fetch("http://localhost:3000/evaluate-image");
			const data = await res.json();

			chrome.runtime.sendMessage({
				msg: "image_evaluated",
				result: data.result,
				token: token,
				cookie: cookie,
			});
		}
	} else if (request.msg === "collect_images") {
		chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
			const currentTabId = tabs[0].id;
			chrome.tabs.sendMessage(currentTabId, { msg: "create_images" });
		});
	}
});
