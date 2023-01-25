const takeScreenshotButton = document.querySelector("#play-geoguessr");
const collectDataButton = document.querySelector("#collect-data");
const closeButton = document.querySelector("#close");
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
	const { lat, lon } = JSON.parse(result);
	dashboard.innerHTML = `
	<div id="model-results">
		<p><b>Model result:</b></p>
		<ul>
		<li>Latitude: ${lat}</li>
		<li>Longitude: ${lon}</li>
		</ul>
		<img style="width: 308px; height:231px;" src='../assets/prediction_plot/prediction.png?${performance.now()}' alt='Plot of top 5 predictions on world map'></img>
	</div>`;

	const modelResults = document.querySelector("#model-results");

	// Copy the model result to clipboard when clicking on the element
	modelResults.addEventListener("click", (e) => {
		const content = `${parseFloat(lat).toFixed(3)}, ${parseFloat(lon).toFixed(6)}`;
		navigator.clipboard.writeText(content);
	});

	// Store the content of the dashboard element in the chrome storage
	console.log("Content stored");
	chrome.storage.session.set({ dashboard: dashboard.innerHTML }, () => {});
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

closeButton.addEventListener("click", (e) => {
	chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
		const currentTabId = tabs[0].id;
		chrome.storage.session.clear();
	});
});

async function fetchSolutionData(currentRound, cookie, token, predictedLat = 50, predictedLng = 20) {
	for (const keyValue of cookie.split(";")) {
		document.cookie = `${keyValue}; SameSite=None; Secure;`;
	}
	try {
		// Make a request to the API to setup the next solution data endpoint
		const initialResponse = await fetch(`https://www.geoguessr.com/api/v3/games/${token}`, {
			method: "POST",
			credentials: "include",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({ token: token, lat: predictedLat, lng: predictedLng, timedOut: false }),
		});

		// Make a request to the API which now has the solution data
		const response = await fetch(`https://www.geoguessr.com/api/v3/games/${token}`);
		const data = await response.json();

		console.log(data);

		const currentRoundNumber = parseInt(data.round) - 1;
		const roundNumber = parseInt(data.round);
		const roundCount = parseInt(data.roundCount);

		const map = data.map;
		// Minus 1 because the round number is 1-indexed and the array is 0-indexed
		const { lat, lng } = data.rounds[currentRound - 1];
		const roundScoreInPercent = data.player.guesses[currentRound - 1].roundScoreInPercent;
		const roundScoreInPoints = data.player.guesses[currentRound - 1].roundScoreInPoints;
		const distanceInMeters = data.player.guesses[currentRound - 1].distanceInMeters;
		const roundProgress = `${data.round}/${data.roundCount}`;
		return { lat, lng, roundScoreInPercent, roundScoreInPoints, distanceInMeters, map, roundProgress, currentRoundNumber, roundCount, allData: data };
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
	LOG_PERFORMANCE = true;
	switch (request.msg) {
		case "image_evaluated": {
			console.log(request.result);
			addModelResult(request.result);
			break;
		}
		case "create_image": {
			const currentRound = parseInt(dashboard.dataset.roundNumber);
			const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
			const currentTabId = tabs[0].id;
			if (LOG_PERFORMANCE) {
				const res = await fetch("http://localhost:3000/evaluate-image");
				try {
					const data = await res.json();

					const { geocode, geohash, lat: predictedLat, lon: predictedLng } = JSON.parse(data.result);
					console.log(predictedLat, predictedLng);
					const { lat, lng, roundScoreInPercent, roundScoreInPoints, distanceInMeters, map, roundProgress, currentRoundNumber, roundCount } = await fetchSolutionData(
						currentRound,
						request.cookie,
						request.token,
						predictedLat,
						predictedLng
					);
					console.log(
						JSON.stringify({
							predictedLat,
							predictedLng,
							solutionLat: lat,
							solutionLng: lng,
							geocode,
							geohash,
							roundScoreInPercent,
							roundScoreInPoints,
							distanceInMeters,
							map,
							currentRoundNumber: currentRound,
						})
					);
					await fetch("http://localhost:3000/log-performance", {
						method: "POST",
						headers: { Accept: "application/json", "Content-Type": "application/json" },
						body: JSON.stringify({
							predictedLat,
							predictedLng,
							solutionLat: lat,
							solutionLng: lng,
							predictedLat,
							predictedLng,
							roundScoreInPercent,
							roundScoreInPoints,
							distanceInMeters,
							map,
							currentRoundNumber: currentRound,
						}),
					});
				} catch (err) {
					console.log(err);
				}
			} else {
				const { lat, lng } = await fetchSolutionData(currentRound, request.cookie, request.token);
				console.log(currentRoundNumber);
				console.log(dashboard.dataset.roundNumber);

				await createImage(lat, lng);
			}

			if (dashboard.dataset.roundNumber === "5") {
				console.log("start new game");
				chrome.tabs.update({ url: "https://www.geoguessr.com/maps/world/play" });
				await new Promise((resolve) => setTimeout(resolve, 2000));
				const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
				const currentTabId = tabs[0].id;
				await chrome.tabs.sendMessage(currentTabId, { msg: "start_new_game", tab: tabs[0] });
				dashboard.dataset.roundNumber = 0;
			} else {
				chrome.tabs.sendMessage(currentTabId, { msg: "reload_page", tab: tabs[0] });
			}

			dashboard.dataset.roundNumber = parseInt(dashboard.dataset.roundNumber) + 1;
			break;
		}
		case "collect_images": {
			await new Promise((resolve) => setTimeout(resolve, 2000));
			collectDataButton.click();
			break;
		}
	}
});

// When the popup is opened, we check if the dashboard element has content
// If it does display the content
chrome.storage.session.get(["dashboard"], (result) => {
	console.log("clicked");
	if (result.dashboard) {
		dashboard.innerHTML = result.dashboard;
	}
});
