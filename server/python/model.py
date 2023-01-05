import numpy as np
import pandas as pd
import pygeohash as pgh

# Deep Learning
from PIL import Image
import torch.nn as nn
import torch
from torchvision import models, transforms, datasets
import torchvision

# Utils
import logging
import os
import json

logging.basicConfig(filename='logging.log', filemode='a', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

HEIGHT = 512
WIDTH = 2560

def decimal_to_base32(decimal):
    base32_digits = "0123456789abcdefghijklmnopqrstuvwxyz"
    base32 = ""
    while decimal > 0:
        base32 = base32_digits[decimal % 32] + base32
        decimal //= 32
    return base32


def decimal_to_base32_alt(decimal):
    base32_digits = '0123456789bcdefghjkmnpqrstuvwxyz';
    base32 = ""
    while decimal > 0:
        base32 = base32_digits[decimal % 32] + base32
        decimal //= 32
    return base32




os.chdir(r"C:\Users\valdr\OneDrive\Vali Studium\Deep_Learning_for_Computer_Vision\Project\DLCV_Project_GeoGuessr_AI\server")

df = pd.read_csv("python/coordinates2.csv")
df_geo = df[["geohash_decimal", "geo_code"]]

df_geo = df_geo.drop_duplicates()

geo_code_to_geohash = dict(zip(df_geo["geo_code"], df_geo["geohash_decimal"]))

# Get images in images folder
image_paths = os.listdir("images")

image_directions = [image_path.split("_")[1].split(".")[0] for image_path in image_paths]

images = dict(zip(image_directions, image_paths))

pil_images = []

for direction in ["top", "right", "bottom", "left"]:
    pil_images.append(Image.open("images/" + images[direction]))


widths, heights = zip(*(i.size for i in pil_images))

total_width = sum(widths)
max_height = max(heights)
# new_im = Image.new('RGB', (total_width, max_height))
new_im = Image.new('RGB', (WIDTH, HEIGHT))

x_offset = 0
for im in pil_images:
    width, height = im.size   # Get dimensions

    left = (width - WIDTH/4)/2
    top = (height - HEIGHT)/2
    right = (width + WIDTH/4)/2
    bottom = (height + HEIGHT)/2
    im = im.crop((left, top, right, bottom))

    new_im.paste(im, (x_offset, 0))
    x_offset += im.size[0]


new_im.save('images/combined_image.jpg')


model = models.resnet50()
num_ftrs = model.fc.in_features
model.fc = nn.Linear(num_ftrs, 3139)

path = r"C:\Users\valdr\OneDrive\Vali Studium\Deep_Learning_for_Computer_Vision\Project\DLCV_Project_GeoGuessr_AI\server\python\pretrainedresnet50_14epoch.tar"
checkpoint = torch.load(path, map_location=torch.device('cpu'))
model.load_state_dict(checkpoint['model_state_dict'])
# optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
# epoch = checkpoint['epoch']
# loss = checkpoint['loss']

transform = transforms.Compose([transforms.ToTensor(),  # convert images to tensors
                                # transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5]),  # normalize images
                                # transforms.Resize((250, 1000))
                                ])

image_transformed = transform(new_im)

with torch.inference_mode():
    # TODO: Why does the output tensor have 2 dimensions and why do we have to unsqueeze(0) add one dimension?
    output = model(image_transformed.unsqueeze(0))[0]

    # Return the top 5 predictions
    # indices_sorted =output[np.argsort(-output[0])]
    # top5 = indices_sorted[:5]
    # print("Top 5 predictions:", top5)

    index = output.data.cpu().numpy().argmax()
    geohash_decimal = geo_code_to_geohash[index]
    geohash = "1" #decimal_to_base32(geohash_decimal)
    geohash_alt = decimal_to_base32_alt(geohash_decimal)
    logging.info(f"Geo-Code Prediction: {index}")
    logging.info(f"Geohash Decimal Prediction: { geohash_decimal }")
    logging.info(f"Geohash Code Prediction: { geohash }")
    logging.info(f"ALT: Geohash Code Prediction: { geohash_alt }")
    logging.info(f"Latitude, Longitude {pgh.decode(geohash)}")
    logging.info(f"ALT: Latitude, Longitude {pgh.decode(geohash_alt)}")

    # result = {"geo-code": index, "geohash": geohash, "geohash_alt": geohash_alt, "lat": pgh.decode(geohash)[0], "lon": pgh.decode(geohash)[1], "lat_alt": pgh.decode(geohash_alt)[0], "lon_alt": pgh.decode(geohash_alt)[1]}
    result_alt = {"geo-code": index, "geohash_alt": geohash_alt, "lat_alt": pgh.decode(geohash_alt)[0], "lon_alt": pgh.decode(geohash_alt)[1]}
    result = {key: str(value) for key, value in result_alt.items()}
    print(json.dumps(result))



