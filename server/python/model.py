from utils.geohash_conversion import create_geocode_mapping
from utils.images import create_combined_image
from utils.prediction import end_to_end_prediction, sequential_prediction

import torch.nn as nn
import torch
from torchvision import models, transforms

import os
from config import Config

os.chdir(os.path.join(Config.CWD, "server"))

input_image = create_combined_image("images")

input_image.save("images/combined_image.png")


if "contihead" in Config.MODEL:
    sequential_prediction(input_image)
else:
    end_to_end_prediction(input_image)
