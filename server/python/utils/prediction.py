from config import Config
from . haversine_kmeans import HaversineKMeans
from .images import create_map_plot
from .geohash_conversion import decimal_to_geohash, create_geocode_mapping, create_continent_geocode_mapping
import pygeohash as pgh
import numpy as np
from torchvision import models
import torchvision.transforms as transforms
import torch.nn.functional as F
import torch.nn as nn
import torch
import os
import sys
import json
# Add the parent directory to the Python search path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def end_to_end_prediction(image):
    """Make a prediction on a single image using the end to end model. Prints the result to stdout as JSON.

    Args:
        image (PIL Image): Image to make a prediction on
    """
    if "resnet" in Config.MODEL:
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
    elif "transformer" in Config.MODEL:
        model = models.vit_b_16(weights='IMAGENET1K_SWAG_E2E_V1')
        model.heads.head = nn.Linear(768, 3139)
        checkpoint = torch.load(os.path.join(
            Config.PRETRAINED_MODELS_PATH, Config.MODEL), map_location=torch.device('cpu'))
        model.load_state_dict(checkpoint['model_state_dict'])
        model.eval()
        transform = transforms.Compose([transforms.ToTensor(),
                                        transforms.Normalize(
                                            mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5]),
                                        transforms.Resize((384, 384))])
    elif "regression" in Config.MODEL:
        model = models.resnet18()
        model.fc = nn.Linear(512, 2)
        checkpoint = torch.load(os.path.join(
            Config.PRETRAINED_MODELS_PATH, Config.MODEL), map_location=torch.device('cpu'))
        model.load_state_dict(checkpoint)
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

        # Calculate the weighted midpoint of the top 5 predictions. Use the softmax values as weights.
        if Config.WEIGHTED_MIDPOINT:
            hvk = HaversineKMeans()
            points = torch.deg2rad(torch.tensor(top_5_coords))
            weights = top5_predictions_confidence
            midpoint = hvk.CompMeans(points, weights)
            lat = torch.rad2deg(midpoint[0])[0][0].item()
            lon = torch.rad2deg(midpoint[0])[0][1].item()
            geohash = pgh.encode(lat, lon)
            result = {"geocode": 0, "geohash": geohash,
                      "lat": lat, "lon": lon, "midpoint": True, "model": Config.MODEL}
            result = {key: str(value) for key, value in result.items()}
            print(json.dumps(result))
            return

        index = output.data.cpu().numpy().argmax()
        geohash_decimal = geo_code_to_geohash[index]
        geohash = decimal_to_geohash(geohash_decimal)

        result = {"geocode": index, "geohash": geohash,
                  "lat": pgh.decode_exactly(geohash)[0], "lon": pgh.decode_exactly(geohash)[1], "model": Config.MODEL}
        result = {key: str(value) for key, value in result.items()}
        print(json.dumps(result))


def sequential_prediction(image, conti=None):
    """Make a prediction on a single image using the sequential model. Prints the result to stdout as JSON.

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

        # Load the continent model with specific parameters, based on the prediction of the continent head model
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

        # decode_exactly returns a tuple of (lat, lon, lat_err, lon_err). We only need the first two values.
        top_5_coords = [pgh.decode_exactly(geohashes_with_samples[int(index.data)])[:2] for index in top5]
        prediction_confidence = nn.functional.softmax(output, dim=0)
        top5_predictions_confidence = prediction_confidence[top5]

        # Create a plot of the top 5 predictions
        create_map_plot(top_5_coords, top5_predictions_confidence.tolist())

        if Config.WEIGHTED_MIDPOINT:
            hvk = HaversineKMeans()
            points = torch.deg2rad(torch.tensor(top_5_coords))
            weights = top5_predictions_confidence
            midpoint = hvk.CompMeans(points, weights)
            lat = torch.rad2deg(midpoint[0])[0][0].item()
            lon = torch.rad2deg(midpoint[0])[0][1].item()
            geohash = pgh.encode(lat, lon, precision=3)
            result = {"geocode": 0, "geohash": geohash,
                      "lat": lat, "lon": lon, "top5": top_5_coords}
            result = {key: str(value) for key, value in result.items()}
            print(json.dumps(result))
            return

        # Get the prediction with the highest score
        index = output.data.cpu().numpy().argmax()
        geohash = geohashes_with_samples[int(index)]

        result = {"geocode": index, "geohash": geohash,
                  "lat": pgh.decode_exactly(geohash)[0], "lon": pgh.decode_exactly(geohash)[1], "model": Config.MODEL}
        result = {key: str(value) for key, value in result.items()}
        print(json.dumps(result))
