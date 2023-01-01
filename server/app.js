const express = require("express");
const cors = require("cors");
const ImageDataURI = require("image-data-uri");
const path = require("path");
const { spawn } = require("child_process");

// Create the Express app
const app = express();
app.use(express.json({ limit: "50mb" }));
app.use(express.urlencoded({ extended: true, limit: "50mb" })); // for form data
app.use(cors());

function callPythonScript() {
	let dataToSend;
	const python = spawn("python", ["python/script.py"]);

	python.stdout.on("data", function (data) {
		dataToSend = data.toString();
	});

	python.on("close", (code) => {
		console.log(`child process close all stdio with code ${code}`);
		// send data to browser
		console.log(dataToSend);
		res.json({ name: "SUCCESS: Image received.", data: dataToSend });
	});
}

// Create an endpoint to receive the image data
app.post("/images", async (req, res) => {
	const { image: dataUri, direction, isFinal } = req.body;

	const filePath = path.join(__dirname, "images", `image_${direction}.png`);

	ImageDataURI.outputFile(dataUri, filePath);
	console.log("HI");

	// spawn new child process to call the python script
});

// Start the server
app.listen(3000, () => {
	console.log("Server listening on port 3000");
});
