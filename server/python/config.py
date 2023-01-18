import os

class Config:
    CROPPED_HEIGHT = 1000
    CROPPED_WIDTH = 1760
    HEIGHT = 512
    WIDTH = 2560
    MODEL = "pretrainedresnet50_14epoch.tar"
    CWD = os.path.dirname(os.getcwd())
    PRETRAINED_MODELS_PATH = os.path.join(CWD , "server", "python", "pretrained_models")
    NUM_CLASSES = 3139
    CSV_PATH = os.path.join(CWD , "server", "python", "utils", "coordinates2.csv")
    DATASET_PATH = os.path.join(CWD , "server", "python", "dataset")
    IMAGES_PATH = os.path.join(CWD , "server", "images")
    PERFORMANCE_PATH = os.path.join(CWD , "server","python" ,"performance")
    PREDICTION_PLOT_PATH = os.path.join(CWD, "geoguessr_extension", "assets", "prediction_plot")
