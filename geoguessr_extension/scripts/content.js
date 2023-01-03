const SLEEP_DURATION = 1000;
function sleep(ms) {
	return new Promise((resolve) => setTimeout(resolve, ms));
}

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
			await sleep(SLEEP_DURATION);
			chrome.runtime.sendMessage({ msg: "screenshot", direction: "top", nextDirection: "right" });
			break;
		case "screenshot_content_right":
			console.log("screenshot_content_right");
			// Move compass to the left
			compassElem.dispatchEvent(createMouseMoveEvent(compassElem, 1000, 0));
			await sleep(SLEEP_DURATION);
			chrome.runtime.sendMessage({ msg: "screenshot", direction: "right", nextDirection: "bottom" });
			break;
		case "screenshot_content_bottom":
			console.log("screenshot_content_bottom");
			// Move compass to the top
			compassElem.dispatchEvent(createMouseMoveEvent(compassElem, 0, 1000));
			await sleep(SLEEP_DURATION);
			chrome.runtime.sendMessage({ msg: "screenshot", direction: "bottom", nextDirection: "left" });
			break;
		case "screenshot_content_left":
			console.log("screenshot_content_left");
			// Move compass to the left
			compassElem.dispatchEvent(createMouseMoveEvent(compassElem, -1000, 0));
			await sleep(SLEEP_DURATION);
			chrome.runtime.sendMessage({ msg: "screenshot", direction: "left", nextDirection: "end", cookie: document.cookie });
			break;
	}
});
