from config import Config
import os
import sys
from PIL import Image

from shapely.geometry import Point
import geopandas as gpd
from geopandas import GeoDataFrame
import matplotlib.pyplot as plt
import pandas as pd

# Add the parent directory to the Python search path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def create_map_plot(coords, confidence):
    """Create a plot of the given coordinates and save it to the prediction plot path.
    The plot shows the top n predictions and scales the marker size based on the confidence.

    Args:
        coords (list): List of tuples with predicted coordinates: (latitude, longitude)
        confidence (list): List of confidence values. These are the softmax values of the predictions.
    """

    df = pd.DataFrame(coords, columns=['lat', 'lng'])
    df["confidence"] = confidence
    # Scale the confidence values to use them as marker sizes
    df["confidence"] = (df["confidence"] / df["confidence"].sum()) * 30
    geometry = [Point(lng, lat) for lat, lng in coords]
    gdf = GeoDataFrame(df, geometry=geometry)

    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    ax = world.plot(color="#5c5c7e")
    gdf.plot(ax=ax, marker='o', color='red', markersize=gdf["confidence"])

    # Set the x and y limits of the plot
    minx = min([point.x for point in geometry])
    miny = min([point.y for point in geometry])
    maxx = max([point.x for point in geometry])
    maxy = max([point.y for point in geometry])

    # Add some padding to the plot
    ax.set_xlim(minx - 20, maxx + 20)
    ax.set_ylim(miny - 20, maxy + 20)

    plt.gca().set_axis_off()
    plt.gcf().set_size_inches(3.5, 1)
    plt.savefig(os.path.join(Config.PREDICTION_PLOT_PATH, 'prediction.png'), bbox_inches="tight", pad_inches=0.0, dpi=300)


def create_combined_image(path):
    """Create a combined image from the images in the given path. Images are combined along the x-axis.

    Args:
        path (str): Path to the images

    Returns:
        Image (PIL Image): Combined image
    """

    image_paths = os.listdir(os.path.join(Config.CWD, "server", path))
    image_directions = [image_path.replace("image_", "").split(".")[0] for image_path in image_paths]
    images = dict(zip(image_directions, image_paths))

    pil_images = []
    for direction in ["top", "top_left", "bottom_left", "bottom_right", "top_right"]:
        pil_images.append(Image.open("images/" + images[direction]))

    # Crop the images and then paste them together
    new_im = Image.new('RGB', (Config.CROPPED_WIDTH * 5, Config.CROPPED_HEIGHT))

    x_offset = 0
    for im in pil_images:
        width, height = im.size
        # Crop the image at the center
        left = (width - Config.CROPPED_WIDTH) / 2
        top = (height - Config.CROPPED_HEIGHT) / 2
        right = (width + Config.CROPPED_WIDTH) / 2
        bottom = (height + Config.CROPPED_HEIGHT) / 2

        # Paste the cropped image into the new image
        im = im.crop((left, top, right, bottom))

        new_im.paste(im, (x_offset, 0))
        x_offset += im.size[0]

    new_im = new_im.resize((Config.WIDTH, Config.HEIGHT), Image.ANTIALIAS)
    return new_im
