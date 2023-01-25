
import os
import sys
import json
# Add the parent directory to the Python search path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.transforms as transforms
from torchvision import models
import numpy as np
import pygeohash as pgh
from haversine import haversine

from .geohash_conversion import decimal_to_geohash, create_geocode_mapping, create_continent_geocode_mapping
from .images import create_map_plot
from config import Config


def end_to_end_prediction(image):
    """Make a prediction on a single image using the end to end model.

    Args:
        image (PIL Image): Image to make a prediction on
    """

    # Load the model
    model = models.resnet50()
    num_ftrs = model.fc.in_features
    model.fc = nn.Linear(num_ftrs, Config.NUM_CLASSES)

    checkpoint = torch.load(os.path.join(
        Config.PRETRAINED_MODELS_PATH, Config.MODEL), map_location=torch.device('cpu'))
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()

    transform = transforms.Compose([transforms.ToTensor(),
                                    transforms.Normalize(
                                        mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5]),
                                    transforms.Resize((250, 1000))])

    # Dictionary to map the geocode predictions to geohashes
    geo_code_to_geohash = create_geocode_mapping(Config.CSV_PATH)

    image_transformed = transform(image)

    with torch.inference_mode():
        # Model expects a batch of images, therefore we add an additional dimension for the batch dimension
        output = model(image_transformed.unsqueeze(0))[0]

        # Return the top 5 predictions
        indices_sorted = np.argsort(-output)
        top5 = indices_sorted[:5]
        top_5_coords = [pgh.decode(decimal_to_geohash(
            geo_code_to_geohash[int(index.data)])) for index in top5]

        prediction_confidence = nn.functional.softmax(output, dim=0)
        top5_predictions_confidence = prediction_confidence[top5]

        # Create a plot of the top 5 predictions
        create_map_plot(top_5_coords, top5_predictions_confidence.tolist())

        index = output.data.cpu().numpy().argmax()
        geohash_decimal = geo_code_to_geohash[index]
        geohash = decimal_to_geohash(geohash_decimal)

        result = {"geocode": index, "geohash": geohash,
                  "lat": pgh.decode(geohash)[0], "lon": pgh.decode(geohash)[1]}
        result = {key: str(value) for key, value in result.items()}
        print(json.dumps(result))


def sequential_prediction(image, conti=None):
    """Make a prediction on a single image using the sequential model

    Args:
        image (PIL Image): Image to make a prediction on
        conti (int): Ground truth
    """
    # Load the continent head model
    model = models.resnet50()
    num_ftrs = model.fc.in_features
    model.fc = nn.Linear(num_ftrs, 7)

    checkpoint = torch.load(os.path.join(Config.PRETRAINED_MODELS_PATH, Config.MODEL),
                            map_location=torch.device('cpu'))
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()

    transform = transforms.Compose([transforms.ToTensor(),
                                    transforms.Normalize(
                                        mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5]),
                                    transforms.Resize((250, 1000))])
    image_transformed = transform(image)

    with torch.inference_mode():
        output = model(image_transformed.unsqueeze(0))[0]

        _, pred = torch.max(output, -1)

        # If the continent is antarctica, return a fixed geohash. Antarctica isn't relevant for this model because it has very few samples in the dataset.
        if pred == 4:
            result = {"geocode": 12345, "geohash": "pdn",
                      "lat": -77.72, "lon": 167.01}
            result = {key: str(value) for key, value in result.items()}
            print(json.dumps(result))
            return

        # Load the model which corresponds to the predicted continent
        model_names = ['South_America', 'Asia', 'Africa',
                       'Oceania', "Antarctica", 'North_America', 'Europe']
        model_output_parameters = [447, 734, 183, 172, 0, 779, 745]
        model.fc = nn.Linear(num_ftrs, model_output_parameters[pred])
        checkpoint = torch.load(os.path.join(
            Config.CONTINENT_MODELS_PATH, "pretrainedresnet50_14epoch_" + model_names[pred] + ".tar"), map_location=torch.device('cpu'))
        model.load_state_dict(checkpoint['model_state_dict'])
        model.eval()

        output = model(image_transformed.unsqueeze(0))[0]

        # Return the top 5 predictions
        indices_sorted = np.argsort(-output)
        top5 = indices_sorted[:5]

        continent_label = model_names[pred]
        if continent_label == 'South_America':
            continent_label = 'South America'
        elif continent_label == 'North_America':
            continent_label = 'North America'

        # Dictionary (pandas.Series???) to map the geocode predictions to geohashes
        geohashes_with_samples = create_continent_geocode_mapping(
            Config.SEQUENTIAL_CSV_PATH, continent_label)

        top_5_coords = [pgh.decode(
            geohashes_with_samples[int(index.data)]) for index in top5]
        prediction_confidence = nn.functional.softmax(output, dim=0)
        top5_predictions_confidence = prediction_confidence[top5]

        # Create a plot of the top 5 predictions
        create_map_plot(top_5_coords, top5_predictions_confidence.tolist())

        # Get the prediction with the highest score
        index = output.data.cpu().numpy().argmax()
        geohash = geohashes_with_samples[int(index)]

        result = {"geocode": index, "geohash": geohash,
                  "lat": pgh.decode(geohash)[0], "lon": pgh.decode(geohash)[1]}
        result = {key: str(value) for key, value in result.items()}
        print(json.dumps(result))
