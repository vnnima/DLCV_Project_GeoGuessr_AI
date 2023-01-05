const express = require("express");
const cors = require("cors");
const ImageDataURI = require("image-data-uri");
const path = require("path");
const { spawn } = require("child_process");
const axios = require("axios");

require("dotenv").config();

// Create the Express app
const app = express();
app.use(express.json({ limit: "50mb" }));
app.use(express.urlencoded({ extended: true, limit: "50mb" })); // for form data
app.use(cors());

function callPythonScript(res) {
	let dataToSend;
	// const python = spawn("python", ["python/script.py"]);
	const python = spawn(process.env.PYTHON_PATH, ["python/model.py"]);

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
	// const python = spawn(process.env.PYTHON_PATH, ["python/model.py"]);
	// let dataToSend, errorToSend;
	// python.stdout.on("data", function (data) {
	// 	dataToSend = data.toString();
	// });
	// python.stderr.on("data", (data) => {
	// 	errorToSend = data.toString();
	// });

	// python.on("close", (code) => {
	// 	console.log(`child process close all stdio with code ${code}`);
	// 	console.log(dataToSend);
	// 	res.json({ name: "SUCCESS: Model evaluated.", result: dataToSend, error: errorToSend });
	// });
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
