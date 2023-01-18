import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pygeohash as pgh
from utils.geohash_conversion import decimal_to_geohash, create_geocode_mapping
from utils.images import create_combined_image, create_map_plot


# Deep Learning
import torch.nn as nn
import torch
from torchvision import models, transforms

# Utils
import logging
import os
import json
from config import Config

logging.basicConfig(filename='python/logging.log', filemode='a', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


os.chdir(os.path.join(Config.CWD, "server"))

geo_code_to_geohash = create_geocode_mapping(Config.CSV_PATH)

new_im = create_combined_image("images")

new_im.save("images/combined_image.png")


# Load the model
model = models.resnet50()
num_ftrs = model.fc.in_features
model.fc = nn.Linear(num_ftrs, Config.NUM_CLASSES)

checkpoint = torch.load(os.path.join(Config.PRETRAINED_MODELS_PATH, Config.MODEL), map_location=torch.device('cpu'))
model.load_state_dict(checkpoint['model_state_dict'])
model.eval()

transform = transforms.Compose([transforms.ToTensor()])

image_transformed = transform(new_im)

with torch.inference_mode():
    # TODO: Why does the output tensor have 2 dimensions and why do we have to unsqueeze(0) add one dimension?
    # Probably because the model expects a batch of images, which adds an additional dimension?
    output = model(image_transformed.unsqueeze(0))[0]

    # Return the top 5 predictions
    indices_sorted = np.argsort(-output)
    top5 = indices_sorted[:5]
    top_5_coords = [pgh.decode(decimal_to_geohash(geo_code_to_geohash[int(index.data)])) for index in top5]

    prediction_confidence = nn.functional.softmax(output, dim=0)
    top5_predictions_confidence = prediction_confidence[top5]

    # Create a plot of the top 5 predictions
    create_map_plot(top_5_coords, top5_predictions_confidence.tolist())

    index = output.data.cpu().numpy().argmax()
    geohash_decimal = geo_code_to_geohash[index]
    geohash = decimal_to_geohash(geohash_decimal)
    logging.info(f"Geo-Code Prediction: {index}")
    logging.info(f"Geohash Decimal Prediction: { geohash_decimal }")
    logging.info(f"Geohash Code Prediction: { geohash }")
    logging.info(f"Latitude, Longitude {pgh.decode(geohash)}")

    result = {"geocode": index, "geohash": geohash, "lat": pgh.decode(geohash)[0], "lon": pgh.decode(geohash)[1]}
    result = {key: str(value) for key, value in result.items()}
    print(json.dumps(result))
