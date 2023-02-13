const SLEEP_DURATION = 1000;
function sleep(ms) {
	return new Promise((resolve) => setTimeout(resolve, ms));
}

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
			// Move compass to the top
			compassElem.dispatchEvent(createMouseMoveEvent(compassElem, 0, -1000));
			compassElem.dispatchEvent(new MouseEvent("mouseup", { bubbles: true, cancelable: true }));
			await sleep(SLEEP_DURATION);
			chrome.runtime.sendMessage({ msg: "screenshot", direction: "top", nextDirection: "top_right", mode: request.mode });
			break;
		case "screenshot_content_top_right":
			// Move compass to the left
			compassElem.dispatchEvent(createMouseMoveEvent(compassElem, 75, -5));
			compassElem.dispatchEvent(new MouseEvent("mouseup", { bubbles: true, cancelable: true }));
			await sleep(SLEEP_DURATION);
			chrome.runtime.sendMessage({ msg: "screenshot", direction: "top_right", nextDirection: "bottom_right", mode: request.mode });
			break;
		case "screenshot_content_bottom_right":
			// Move compass to the top
			compassElem.dispatchEvent(createMouseMoveEvent(compassElem, 55, 85));
			compassElem.dispatchEvent(new MouseEvent("mouseup", { bubbles: true, cancelable: true }));
			await sleep(SLEEP_DURATION);
			chrome.runtime.sendMessage({ msg: "screenshot", direction: "bottom_right", nextDirection: "bottom_left", mode: request.mode });
			break;
		case "screenshot_content_bottom_left":
			// Move compass to the left
			compassElem.dispatchEvent(createMouseMoveEvent(compassElem, -40, 100));
			compassElem.dispatchEvent(new MouseEvent("mouseup", { bubbles: true, cancelable: true }));
			await sleep(SLEEP_DURATION);
			chrome.runtime.sendMessage({ msg: "screenshot", direction: "bottom_left", nextDirection: "top_left", mode: request.mode });
			break;
		case "screenshot_content_top_left":
			// Move compass to the left
			compassElem.dispatchEvent(createMouseMoveEvent(compassElem, -80, -23));
			compassElem.dispatchEvent(new MouseEvent("mouseup", { bubbles: true, cancelable: true }));
			await sleep(SLEEP_DURATION);
			// This is the final screenshot. Send the message to the background script with the next direction as "end".
			// We also send the cookie to the background script so that it can be used to make the request to the API.
			chrome.runtime.sendMessage({ msg: "screenshot", direction: "top_left", nextDirection: "end", cookie: document.cookie, mode: request.mode });
			break;
		case "reload_page":
			location.reload();
			chrome.runtime.sendMessage({ msg: "collect_images" });
			break;
		case "start_new_game":
			const startButton = document.querySelector("[data-qa='start-game-button']");
			startButton.click();
			chrome.runtime.sendMessage({ msg: "collect_images" });
			break;
	}
});
