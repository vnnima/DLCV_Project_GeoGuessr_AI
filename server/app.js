const express = require("express");
const cors = require("cors");
const ImageDataURI = require("image-data-uri");
const path = require("path");
const { spawn } = require("child_process");

require("dotenv").config();

// Create the Express app
const app = express();
app.use(express.json({ limit: "50mb" }));
app.use(express.urlencoded({ extended: true, limit: "50mb" })); // for form data
app.use(cors());

function callModelScript(res) {
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

function callCreateDataScript(res, coords) {
	const name = `img_${coords.join(",")}`;
	const python = spawn(process.env.PYTHON_PATH, [`python/collect_data.py`, name]);

	let data;

	python.stdout.on("data", function (data) {
		data = data.toString();
	});

	python.stderr.on("data", function (data) {});

	python.on("close", (code) => {
		console.log(`child process close all stdio with code ${code}`);
		res.json({ name: "SUCCESS: Image (sample) evaluated.", result: "IMAGE CREATED" });
	});
}

function callLogPerformanceScript(res, data) {
	dataJSON = JSON.stringify(data);
	let dataToSend;
	const python = spawn(process.env.PYTHON_PATH, ["python/performance.py", dataJSON]);

	python.stdout.on("data", function (data) {
		dataToSend = data.toString();
	});

	python.on("close", (code) => {
		console.log(`child process close all stdio with code ${code}`);
		console.log(dataToSend);
		res.json({ name: "SUCCESS: Performance logged" });
	});
}

app.post("/create-image", (req, res) => {
	callCreateDataScript(res, req.body.coords);
	return;
});

app.get("/evaluate-image", (req, res) => {
	callModelScript(res);
	return;
});

app.post("/log-performance", (req, res) => {
	console.log("LETS GOT PERFORMANCE");
	console.log(req.body);
	callLogPerformanceScript(res, req.body);
	return;
});

app.post("/save-image", async (req, res) => {
	const { image: dataUri, direction } = req.body;

	const filePath = path.join(__dirname, "images", `image_${direction}.png`);

	ImageDataURI.outputFile(dataUri, filePath);

	res.json({ name: "SUCCESS: Image received." });
});

// Start the server
app.listen(3000, () => {
	console.log("Server listening on port 3000");
});
