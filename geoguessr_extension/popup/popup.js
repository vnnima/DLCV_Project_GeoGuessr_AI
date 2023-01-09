const takeScreenshotButton = document.querySelector("#play-geoguessr");
const collectDataButton = document.querySelector("#collect-data");
const dashboard = document.querySelector(".dashboard");
const buttons = document.querySelector(".buttons");

function addLoadingSpinner() {
	dashboard.innerHTML = "";
	const image = document.createElement("img");
	image.src = "../assets/loading.svg";
	image.classList.add("loading-spinner");
	dashboard.appendChild(image);
}

function addModelResult(result) {
	const { geohash, lat, lon } = JSON.parse(result);
	dashboard.innerHTML = `
	<div id="model-results">Model result:
		<p>Geohash: ${geohash}</p>
		<p>Lat: ${lat}</p>
		<p>Lon: ${lon}</p>
		<img style="width: 350px; height:100px;" src='../assets/prediction_plot/prediction.png' alt='Plot of top 5 predictions on world map'>
	</div>`;

	const modelResults = document.querySelector("#model-results");
	modelResults.addEventListener("click", (e) => {
		const content = `${parseFloat(lat).toFixed(3)}, ${parseFloat(lon).toFixed(6)}`;
		navigator.clipboard.writeText(content);
	});
}

function addSolutionData() {
	dashboard.innerHTML = "";
	const solutionElem = document.createElement("div");
	solutionElem.innerHTML = `
						<p>Solution: ${solutionLat}, ${solutionLng}</p>}
						<p>Round score: ${roundScore}</p>
						<p>Distance: ${distance}</p>
						`;
	dashboard.appendChild(solutionElem);
}

function addSubmitButton(token, cookie) {
	// We keep track of the round number in the dashboard element as a "data-"" attribute
	const roundNumber = dashboard.dataset.roundNumber;
	dashboard.dataset.roundNumber = parseInt(roundNumber) + 1;
	console.log(token);

	buttons.querySelector("#play-geoguessr").style.display = "none";
	const submitButton = document.createElement("button");
	submitButton.innerText = "Submit";
	submitButton.classList.add("btn");

	submitButton.addEventListener("click", (e) => {
		console.log(token);
		console.log(roundNumber);
		console.log(cookie);
		console.log(cookie);
		fetchSolutionData();
	});
	buttons.appendChild(submitButton);
}

takeScreenshotButton.addEventListener("click", (e) => {
	addLoadingSpinner();
	chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
		const currentTabId = tabs[0].id;
		chrome.tabs.sendMessage(currentTabId, { msg: "screenshot_content_top", tab: tabs[0], mode: "evaluate-image" });
	});
});

collectDataButton.addEventListener("click", (e) => {
	chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
		const currentTabId = tabs[0].id;
		chrome.tabs.sendMessage(currentTabId, { msg: "screenshot_content_top", tab: tabs[0], mode: "create-image" });
	});
});

async function fetchSolutionData(cookie, token) {
	for (const keyValue of cookie.split(";")) {
		document.cookie = `${keyValue}; SameSite=None; Secure;`;
	}
	try {
		// Make a request to the API to setup the next solution data endpoint
		const initialResponse = await fetch(`https://www.geoguessr.com/api/v3/games/${token}`, {
			method: "POST",
			credentials: "include",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({ token: token, lat: 50.12345, lng: 20.12345, timedOut: false }),
		});

		// Make a request to the API which now has the solution data
		const response = await fetch(`https://www.geoguessr.com/api/v3/games/${token}`);
		const data = await response.json();

		const roundNumber = data.round;
		const { lat, lng } = data.rounds[roundNumber - 1];
		const roundScore = data.player.guesses[roundNumber - 2].roundScore.amount;
		const distance = data.player.guesses[roundNumber - 2].distance.meters.amount;
		console.log({ lat, lng, roundScore, distance });
		return { lat, lng, roundScore, distance };
	} catch (err) {
		console.log(err);
	}
}

async function createImage(solutionLat, solutionLng) {
	try {
		await fetch("http://localhost:3000/create-image", {
			method: "POST",
			headers: { Accept: "application/json", "Content-Type": "application/json" },
			body: JSON.stringify({ collectData: true, coords: [solutionLat, solutionLng] }),
		});
	} catch (err) {
		console.log(err);
	}
}

chrome.runtime.onMessage.addListener(async (request) => {
	switch (request.msg) {
		case "image_evaluated": {
			addModelResult(request.result);
			break;
		}
		case "create_image": {
			const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
			const currentTabId = tabs[0].id;
			// Start all over again
			const { lat, lng } = await fetchSolutionData(request.cookie, request.token);
			await createImage(lat, lng);

			if (dashboard.dataset.roundNumber === "5") {
				chrome.tabs.update({ url: "https://www.geoguessr.com/maps/world/play" });
				console.log("START NEW GAME");
				await new Promise((resolve) => setTimeout(resolve, 2000));
				await chrome.tabs.sendMessage(currentTabId, { msg: "start_new_game", tab: tabs[0] });
				collectDataButton.click();
				dashboard.dataset.roundNumber = 0;
			}
			{
				chrome.tabs.sendMessage(currentTabId, { msg: "reload_page", tab: tabs[0] });
				console.log(dashboard.dataset.roundNumber);
			}

			dashboard.dataset.roundNumber = parseInt(dashboard.dataset.roundNumber) + 1;
			break;
		}
		case "collect_images": {
			await new Promise((resolve) => setTimeout(resolve, 2000));
			console.log("COLLECT IMAGES");
			collectDataButton.click();
			break;
		}
	}
});
