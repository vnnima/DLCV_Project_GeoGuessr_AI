# DLCV_Project_GeoGuessr_AI



## Chrome Extension

This chrome extension is used to test the model in-game and measure their performance. The extension takes five screenshots from the geoguessr streetview and sends it to a local server. The local server then runs a python script that utilizes the AI model built using Pytorch to make a prediction. The prediction is then sent back to the extension.

### **Installation and Setup**

1. Install the Google Chrome browser if it is not already installed. (Or any chromium based browser)
1. Download the chrome extension files from the provided source. The files are located in the `chrome_extension` folder.
1. Open Google Chrome and navigate to the chrome://extensions/ page.
1. Turn on the "Developer mode" toggle in the top right corner of the page.
1. Click the "Load unpacked" button and select the folder containing the extension files.
1. The extension should now be installed and appear in the list of installed extensions.

### **Usage**

1. Make sure that the local server is up and running. The setup for the local server is described in this section.
1. Open the Google Chrome browser and navigate to the [GeoGuessr](https://www.geoguessr.com/) website and start a game on the world map. (You need to have a google account to play the game.)
1. After starting the game and seeing the Google Street View panorama, click on the extension icon to activate it.
1. Then press the play button. The extension will take five screenshots of the streetview images and use them to make a prediction. While the extension is making the prediction don't change the current tab or click on anything. The prediction will be displayed on the screen after a few seconds (depending on your hardware this might take longer).
1. In the `config.py` file located `server/python/` folder you can change the model that is used for the prediction. A detailed explanation about the configuration can be found in the `config.py` file.


**Note:** If there is a problem with the extension, you can check the chrome extension page for errors. If there are any errors it is often enough to reload the extension in the chrome extension tab **AND** reload the current GeoGuessr page. If it still does not work please report the error to this email address: `s3645131@stud.uni-frankfurt.de`

### **Requirements**

- Chromium based browser
- A local nodejs server
- Python 3.8 >=

## Node Server
This node server is used to receive the screenshots from the chrome extension and run the python script that utilizes the AI model to make a prediction. The prediction is then sent back to the chrome extension.

### **Installation and Setup**

1. Install **[Node.js](https://nodejs.org/en/)** if it is not already installed.
2. Clone the repository containing the server files.
3. Open the command prompt in the root directory of the server files.
4. Run the command **`npm install`** to install the dependencies specified in the **`package.json`** file.
5. Run the command **`npm run watch`** to start the server.


### **Requirements**

- Node.js