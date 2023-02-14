# Outperforming Humans in GeoGuessr with Deep Learning - DLCV Project

- [DLCV\_Project\_GeoGuessr\_AI](#dlcv_project_geoguessr_ai)
  - [Introduction](#introduction)
  - [Chrome Extension](#chrome-extension)
    - [**Requirements**](#requirements)
    - [**Installation and Setup**](#installation-and-setup)
    - [**Usage**](#usage)
  - [Node-Server](#node-server)
    - [**Requirements**](#requirements-1)
    - [**Installation and Setup**](#installation-and-setup-1)


## Introduction
In this repository, you will find the code for our project, which is aimed at developing a machine learning model that can predict the geographic location of an image.
This project is a part of the "Deep Learning for Computer Vision" (2023) course at the Goethe University Frankfurt by Prof. Dr. Gemma Roig. 

Our project's main objective is to achieve optimal performance in the [GeoGuessr](https://www.geoguessr.com/) game and improve the accuracy of existing models. To achieve this, we conducted an extensive literature review and tested various computer vision techniques to determine the most effective model for our task. Our findings indicate that using regular ResNets with an end-to-end learning approach was the most effective approach. Additionally, we found that data augmentation, a custom loss-function specifically designed for this task, and increasing the size of the dataset also produced positive results.

We would like to express our gratitude to [Traversed](https://www.youtube.com/@TraversedTV), whose [youtube video](https://www.youtube.com/watch?v=0k-SJgv-laM) inspired us to undertake this project and who was so kind to share his dataset with us.

## Chrome Extension

This chrome extension is used to test the models in-game and measure their performance. The extension takes five screenshots from the GeoGuessr Street View and sends it to a local server. The server then runs a python script that utilizes the AI model built using PyTorch to make a prediction. The prediction is then sent back to the extension to make the final guess.

### **Requirements**

- Chromium based browser
- A local nodejs server
- Python 3.9
- PyTorch, pandas, haversine, pygeohash, matplotlib

### **Installation and Setup**

1. Install the Google Chrome browser if it is not already installed. (Or any chromium based browser)
1. Download the chrome extension files from the provided source. The files are located in the `chrome_extension` folder.
1. Open Google Chrome and navigate to the chrome://extensions/ page.
1. Turn on the "Developer mode" toggle in the top right corner of the page.
1. Click the "Load unpacked" button and select the folder containing the extension files.
1. The extension should now be installed and appear in the list of installed extensions.
1. Install the python dependencies by running the command `pip install -r requirements.txt` in the `server/python` folder.

### **Usage**

1. Make sure that the local server is up and running. The setup for the local server is described in this [section](#node-server).
1. Open the Google Chrome browser and navigate to the [GeoGuessr](https://www.geoguessr.com/) website and start a game on the world map. (You need to have a GeoGuessr account to play the game.)
1. After starting the game and seeing the Google Street View panorama, click the gear icon in the bottom left corner of the screen and turn "Classic Compass" on.
1. Now you can start the extension by clicking on the extension icon in the top right corner of the browser. The extension icon should look like a globe with some markers on it.
1. Then press the play button. The extension will take five screenshots of the Street View images and use them to make a prediction. While the extension is making the prediction don't change the current tab or click on anything. The prediction will be displayed on the screen after a few seconds (depending on your hardware this might take longer).
1. In the `config.py` file located `server/python/` folder you can change the model that is used for the prediction. A detailed explanation about the configuration can be found in the `config.py` file.


**Note:** If there is a problem with the extension, you can check the chrome extension page for errors. If there are any errors it is often enough to reload the extension in the chrome extension tab **AND** reload the current GeoGuessr page. If it still does not work please report the error to this email address: `s3645131@stud.uni-frankfurt.de`


## Node-Server
This node server is used to receive the screenshots from the chrome extension and run the python script that utilizes the AI model to make a prediction. The prediction is then sent back to the chrome extension.

### **Requirements**

- Node.js
- npm

### **Installation and Setup**

1. Install **[Node.js](https://nodejs.org/en/)** if it is not already installed.
2. Clone the repository containing the server files.
1. Download the model state files from this [link](https://hessenbox-a10.rz.uni-frankfurt.de/getlink/fiJLp4TD4kDs67qHbkT5az/pretrained_models) and move these files into the `server/python/pretrained_models` folder.
1. In the `.env` file located in the `server` folder you have to change the `PYTHON_PATH` environment variable to the path of your python executable. You can find the path by running the command `where python` in the command prompt. 
3. Open the command prompt in the root directory of the server files.
4. Run the command **`npm install`** to install the dependencies specified in the **`package.json`** file.
5. Run the command **`npm run watch`** to start the server.

