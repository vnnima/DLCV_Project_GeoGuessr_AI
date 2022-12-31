// const playGeoGuessrButton = document.querySelector("#play-geoguessr");
const takeScreenshotButton = document.querySelector("#take-screenshot");

// playGeoGuessrButton.addEventListener("click", (e) => {
// 	console.log("playGeoGuessrButton clicked");
// 	chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
// 		const currentTabId = tabs[0].id;
// 		chrome.tabs.sendMessage(currentTabId, { command: "playGeoGuessr" }, (response) => {
// 			console.log(response);
// 		});
// 	});
// });

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

		// chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
		// 	const currentTabId = tabs[0].id;
		// 	chrome.tabs.sendMessage(currentTabId, { msg: "screenshot_content" });
		// });
	}
});
// (async () => {
// 	const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
// 	const response = await chrome.tabs.sendMessage(tab.id, { msg: "screenshot" });
// 	// do something with response here, not outside the function
// 	console.log(response);
// })();
// chrome.tabs.query(
// 	{
// 		active: true,
// 		currentWindow: true,
// 	},
// 	function (tabs) {
// 		chrome.scripting.executeScript({
// 			target: {
// 				tabId: tabs[0].id,
// 			},
// 			function: sendData,
// 		});
// 	}
// );

// const sendData = async () => {
// 	chrome.runtime.sendMessage(
// 		{
// 			msg: "screenshot",
// 		},
// 		function (response) {
// 			console.log(response.received);
// 		}
// 	);
// };
