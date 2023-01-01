async function upload(file) {
	// const blob = await (await fetch(file)).blob();
	// console.log(typeof blob);

	fetch("http://localhost:3000/images", {
		// Your POST endpoint
		method: "POST",
		body: file, // This is your file object
	})
		.then(
			(response) => response.json() // if the response is a JSON object
		)
		.then(
			(success) => console.log(success) // Handle the success response object
		)
		.catch(
			(error) => console.log(error) // Handle the error response object
		);
}

chrome.runtime.onMessage.addListener(async (request) => {
	if (request.msg == "screenshot") {
		// Get the current tab
		const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
		const tab = tabs[0];

		console.log(tab);

		if (tab?.url?.startsWith("chrome://")) return undefined;
		if (tab?.url?.startsWith("devtools://")) return undefined;

		// fetch("http://localhost:3000/", { body: JSON.stringify({ image: "test" }) });
		// fetch("http://localhost:3000/home", { method: "POST", headers: { Accept: "application/json", "Content-Type": "application/json" }, body: JSON.stringify({ image: "test" }) });

		chrome.tabs.captureVisibleTab(null, { format: "png" }, (dataUrl) => {
			console.log(dataUrl);
			// console.log(dataUrl);
			// let formData = new FormData();
			// formData.append("file", dataUrl);
			// console.log(formData);
			// Send the data URL to the server using fetch()
			fetch("http://localhost:3000/images", {
				method: "POST",
				headers: { Accept: "application/json", "Content-Type": "application/json" },
				// body: formData,
				body: JSON.stringify({ image: dataUrl }),
			})
				.then((response) => response.json())
				.then((data) => {
					console.log("Success:", data);
				})
				.catch((error) => {
					console.log("Error:", error);
				});
		});
		return;

		// // Take a screenshot of the current tab
		const screenshot = await chrome.tabs.captureVisibleTab();
		console.log("SCREEN", typeof screenshot);
		await upload(screenshot);

		// Download the screenshot and URL
		chrome.downloads.download({
			url: screenshot,
			filename: `screenshot-${tab.url.replace(/[^a-zA-Z0-9]/g, "_")}.png`,
			conflictAction: "uniquify",
		});

		// send message to content script
		chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
			const currentTabId = tabs[0].id;
			chrome.tabs.sendMessage(currentTabId, { msg: `screenshot_content_${request.direction}`, tab: tabs[0] });
		});
	}
});
