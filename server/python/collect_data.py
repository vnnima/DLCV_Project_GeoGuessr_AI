from config import Config 
import sys
from utils.images import create_combined_image

name = sys.argv[1] + ".jpg"
create_combined_image(Config.IMAGES_PATH).save(Config.DATASET_PATH + "\\" + name)



