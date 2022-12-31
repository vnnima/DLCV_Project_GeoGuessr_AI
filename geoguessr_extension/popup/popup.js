const takeScreenshotButton = document.querySelector("#take-screenshot");

takeScreenshotButton.addEventListener("click", (e) => {
	console.log("Hi");

	chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
		const currentTabId = tabs[0].id;
		chrome.tabs.sendMessage(currentTabId, { msg: "screenshot_content_top", tab: tabs[0] });
	});
});

chrome.runtime.onMessage.addListener(async (request) => {
	if (request.msg == "screenshot_taken") {
		console.log("screenshot_taken");
		let tab = await chrome.tabs.query({ active: true, currentWindow: true });
		console.log(tab);
		chrome.tabs.sendMessage(tab[0].id, { msg: "screenshot_content" });
	}
});
