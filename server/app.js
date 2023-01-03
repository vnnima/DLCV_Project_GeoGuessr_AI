const express = require("express");
const cors = require("cors");
const ImageDataURI = require("image-data-uri");
const path = require("path");
const { spawn } = require("child_process");
const axios = require("axios");

// Create the Express app
const app = express();
app.use(express.json({ limit: "50mb" }));
app.use(express.urlencoded({ extended: true, limit: "50mb" })); // for form data
app.use(cors());

function callPythonScript(res) {
	let dataToSend;
	const python = spawn("python", ["python/script.py"]);

	python.stdout.on("data", function (data) {
		dataToSend = data.toString();
	});

	python.on("close", (code) => {
		console.log(`child process close all stdio with code ${code}`);
		console.log(dataToSend);
		res.json({ name: "SUCCESS: Model evaluated.", result: dataToSend });
	});
}

app.get("/", (req, res) => {
	axios({
		method: "post",
		withCredentials: true,
		url: "https://www.geoguessr.com/api/v3/games/GWk670jZno6e6Bv6",
		data: { token: "GWk670jZno6e6Bv6", lat: 50.12345, lng: 20.12345, timedOut: false },
		headers: {
			"Content-Type": "application/json",
			"Cookies": "_ncfa=8ZAYivsh54qo%2Byc5tkA9%2FPqiIOnfEzznl9A%2FxxuUuqE%3DFt4pdMlQtQlmVaLlvo%2BuZVSZZsGE%2FLXfXpe1l%2FjpgK2PNEEGzjZ9UBjetRXPzGvQ; devicetoken=35F011162F;",
		},
	}).then((res) => console.log(res));
	res.send("HI");
});

// Create an endpoint to receive the image data
app.post("/images", async (req, res) => {
	const { image: dataUri, direction, isFinal } = req.body;

	const filePath = path.join(__dirname, "images", `image_${direction}.png`);

	ImageDataURI.outputFile(dataUri, filePath);

	if (isFinal) {
		callPythonScript(res);
		return;
	}
	res.json({ name: "SUCCESS: Image received." });
});

// Start the server
app.listen(3000, () => {
	console.log("Server listening on port 3000");
});
