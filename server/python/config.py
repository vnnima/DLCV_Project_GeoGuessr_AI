import os


class Config:
    CROPPED_HEIGHT = 1000
    CROPPED_WIDTH = 1760
    HEIGHT = 512
    WIDTH = 2560
    NUM_CLASSES = 3139
    WEIGHTED_MIDPOINT = False

    CWD = os.path.dirname(os.getcwd())
    PRETRAINED_MODELS_PATH = os.path.join(CWD, "server", "python", "pretrained_models")
    CONTINENT_MODELS_PATH = os.path.join(PRETRAINED_MODELS_PATH, "continent_models")
    MODEL = "pretrainedresnet50_14epoch_contihead.tar"

    PYTHON_PATH = os.path.join(CWD, "server", "python")
    UTILS_PATH = os.path.join(PYTHON_PATH, "utils")
    PERFORMANCE_PATH = os.path.join(PYTHON_PATH, "performance")
    DATASET_PATH = os.path.join(PYTHON_PATH, "dataset")
    SEQUENTIAL_CSV_PATH = os.path.join(UTILS_PATH, "coordinates_sequential.csv")
    CSV_PATH = os.path.join(UTILS_PATH, "coordinates_end_to_end.csv")
    IMAGES_PATH = os.path.join(CWD, "server", "images")
    PREDICTION_PLOT_PATH = os.path.join(CWD, "geoguessr_extension", "assets", "prediction_plot")
