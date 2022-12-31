// chrome.browserAction.onClicked.addEventListener(async () => {
// 	// Take a screenshot of the current tab
// 	const screenshot = await chrome.tabs.captureVisibleTab();

// 	// Download the screenshot
// 	chrome.downloads.download({
// 		url: screenshot,
// 		filename: "screenshot.png",
// 	});
// });
/**
 *
 * @param {HTMLElement} elem
 * @param {number} x - number of pixels to move the mouse along the x axis of the element
 * @param {number} y - number of pixels to move the mouse along the y axis bottom
 * @returns
 */
function createMouseMoveEvent(elem, x, y) {
	return new MouseEvent("mousedown", {
		clientX: elem.getBoundingClientRect().left + x,
		clientY: elem.getBoundingClientRect().top + y,
		bubbles: true,
		cancelable: true,
	});
}

chrome.runtime.onMessage.addListener(async (request) => {
	const compassElem = document.querySelector(".compass__indicator");
	switch (request.msg) {
		case "screenshot_content_top":
			console.log("screenshot_content_top");
			// Move compass to the top
			compassElem.dispatchEvent(createMouseMoveEvent(compassElem, 0, -1000));
			// sleep for 1 second
			await new Promise((resolve) => setTimeout(resolve, 3000));
			chrome.runtime.sendMessage({ msg: "screenshot__", direction: "right" });
			break;
		case "screenshot_content_right":
			console.log("screenshot_content_right");
			// Move compass to the left
			compassElem.dispatchEvent(createMouseMoveEvent(compassElem, 1000, 0));
			await new Promise((resolve) => setTimeout(resolve, 3000));
			chrome.runtime.sendMessage({ msg: "screenshot__", direction: "bottom" });
			break;
		case "screenshot_content_bottom":
			console.log("screenshot_content_bottom");
			// Move compass to the top
			compassElem.dispatchEvent(createMouseMoveEvent(compassElem, 0, 1000));
			await new Promise((resolve) => setTimeout(resolve, 3000));
			chrome.runtime.sendMessage({ msg: "screenshot__", direction: "left" });
			break;
		case "screenshot_content_left":
			console.log("screenshot_content_left");
			// Move compass to the left
			compassElem.dispatchEvent(createMouseMoveEvent(compassElem, -1000, 0));
			await new Promise((resolve) => setTimeout(resolve, 3000));
			chrome.runtime.sendMessage({ msg: "screenshot__", direction: "end" });
			break;
		case "screenshot_content_end":
			console.log("screenshot_content_end");
			compassElem.dispatchEvent(new MouseEvent("mouseup", { bubbles: true, cancelable: true }));
	}

	// if (request.msg == "screenshot_content") {
	// 	console.log("screenshot_content");
	// 	const tab = request.tab;
	// 	const compassElem = document.querySelector(".compass__indicator");

	// 	// Move compass to the center
	// 	compassElem.dispatchEvent(createMouseMoveEvent(compassElem, 0, -1000));
	// 	// chrome.runtime.sendMessage({ msg: "screenshot" });
	// 	await takeScreenshot();

	// 	// sleep for 1 second
	// 	await new Promise((resolve) => setTimeout(resolve, 3000));

	// 	// Move compass to the right
	// 	compassElem.dispatchEvent(createMouseMoveEvent(compassElem, -1000, 0));
	// 	// chrome.runtime.sendMessage({ msg: "screenshot" });
	// 	await takeScreenshot();

	// 	await new Promise((resolve) => setTimeout(resolve, 3000));

	// 	// Move compass to the bottom
	// 	compassElem.dispatchEvent(createMouseMoveEvent(compassElem, 0, 1000));
	// 	// chrome.runtime.sendMessage({ msg: "screenshot" });
	// 	await takeScreenshot();

	// 	await new Promise((resolve) => setTimeout(resolve, 3000));

	// 	// Move compass to the left
	// 	compassElem.dispatchEvent(createMouseMoveEvent(compassElem, 1000, 0));
	// 	// chrome.runtime.sendMessage({ msg: "screenshot" });
	// 	await takeScreenshot();

	// 	compassElem.dispatchEvent(new MouseEvent("mouseup", { bubbles: true, cancelable: true }));
	// 	// chrome.runtime.sendMessage({ msg: "screenshot" });
	// } else
});
