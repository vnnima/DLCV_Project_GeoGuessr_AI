const takeScreenshotButton = document.querySelector("#play-geoguessr");
const dashboard = document.querySelector(".dashboard");

function addLoadingSpinner() {
	dashboard.innerHTML = "";
	const image = document.createElement("img");
	image.src = "../assets/loading.svg";
	image.classList.add("loading-spinner");
	dashboard.appendChild(image);
}

function addModelResult(result) {
	dashboard.innerHTML = "";
	const modelResult = document.createElement("p");
	modelResult.innerText = result.toString();
	dashboard.appendChild(modelResult);
}

function removeLoadingSpinner() {
	dashboard.innerHTML = "<p>Done!</p>";
}

takeScreenshotButton.addEventListener("click", (e) => {
	addLoadingSpinner();
	chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
		const currentTabId = tabs[0].id;
		chrome.tabs.sendMessage(currentTabId, { msg: "screenshot_content_top", tab: tabs[0] });
	});
});

chrome.runtime.onMessage.addListener(async (request) => {
	if (request.msg == "screenshot_end") {
		const tab = await chrome.tabs.query({ active: true, currentWindow: true });
		removeLoadingSpinner();
	} else if (request.msg == "image_evaluated") {
		console.log("Evaluated image:", request.result);
		addModelResult(request.result);
	}
});
