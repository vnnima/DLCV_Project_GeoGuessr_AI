import os
from PIL import Image
from config import Config

def create_combined_image(path):
    """Create a combined image from the images in the given path. Images are combined along the x-axis.

    Args:
        path (str): Path to the images
    
    Returns:
        Image (PIL Image): Combined image
    """

    image_paths = os.listdir(path)
    image_directions = [image_path.replace("image_", "").split(".")[0] for image_path in image_paths]
    images = dict(zip(image_directions, image_paths))

    pil_images = []
    for direction in ["top", "top_right", "bottom_right", "bottom_left", "top_left"]:
        pil_images.append(Image.open("images/" + images[direction]))



    # Crop the images and then paste them together
    new_im = Image.new('RGB', (Config.WIDTH * 5, Config.HEIGHT))

    x_offset = 0
    for im in pil_images:
        width, height = im.size  
        # Crop the image at the center
        left = (width - Config.WIDTH)/2
        top = (height - Config.HEIGHT)/2
        right = (width + Config.WIDTH)/2
        bottom = (height + Config.HEIGHT)/2

        # Paste the cropped image into the new image
        im = im.crop((left, top, right, bottom))

        new_im.paste(im, (x_offset, 0))
        x_offset += im.size[0]  

    
    return new_im
# Each image will be cropped to these dimensions



