const takeScreenshotButton = document.querySelector("#play-geoguessr");
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
	dashboard.innerHTML = "";
	const modelResult = document.createElement("p");
	modelResult.innerText = result.toString();
	dashboard.appendChild(modelResult);
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
		for (const keyValue of cookie.split(";")) {
			console.log(keyValue);
			document.cookie = `${keyValue}; SameSite=None; Secure;`;
		}
		console.log(cookie);

		fetch(`https://www.geoguessr.com/api/v3/games/${token}`, {
			method: "POST",
			credentials: "include",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({ token: token, lat: 50.12345, lng: 20.12345, timedOut: false }),
		})
			.then((res) => {
				res.json();
				console.log(res);
			})
			.then((data) => {
				fetch(`https://www.geoguessr.com/api/v3/games/${token}`)
					.then((res) => res.json())
					.then((data) => {
						console.log(data);
						const roundNumber = data.round;
						const { lat: solutionLat, lng: solutionLng } = data.rounds[roundNumber - 1];
						const roundScore = data.player.guesses[roundNumber - 2].roundScore.amount;
						const distance = data.player.guesses[roundNumber - 2].distance.meters.amount;

						const solutionElem = document.createElement("div");
						solutionElem.innerHTML = `
						<p>Solution: ${solutionLat}, ${solutionLng}</p>}
						<p>Round score: ${roundScore}</p>
						<p>Distance: ${distance}</p>
						`;
						dashboard.appendChild(solutionElem);
					});
			})
			.catch((err) => console.log(err));
	});
	buttons.appendChild(submitButton);
}

takeScreenshotButton.addEventListener("click", (e) => {
	addLoadingSpinner();
	chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
		const currentTabId = tabs[0].id;
		chrome.tabs.sendMessage(currentTabId, { msg: "screenshot_content_top", tab: tabs[0] });
	});
});

chrome.runtime.onMessage.addListener(async (request) => {
	if (request.msg == "image_evaluated") {
		console.log("Evaluated image:", request.result);
		addModelResult(request.result);
		addSubmitButton(request.token, request.cookie);
	}
});
