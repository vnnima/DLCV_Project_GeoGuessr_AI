chrome.runtime.onMessage.addListener(async (request) => {
	if (request.msg == "screenshot__") {
		// Get the current tab
		const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
		const tab = tabs[0];
		console.log(tab);

		// // Take a screenshot of the current tab
		const screenshot = await chrome.tabs.captureVisibleTab();

		// Download the screenshot and URL
		chrome.downloads.download({
			url: screenshot,
			filename: `screenshot-${tab.url.replace(/[^a-zA-Z0-9]/g, "_")}.png`,
			conflictAction: "uniquify",
		});

		console.log("I AM ABOUT TO SEND A MESSAGE IN THE BACKGROUND TO THE CONTENT SCRIPT");
		// send message to content script
		chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
			const currentTabId = tabs[0].id;
			chrome.tabs.sendMessage(currentTabId, { msg: `screenshot_content_${request.direction}`, tab: tabs[0] });
		});
	}
});
