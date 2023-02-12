import os


class Config:
    """Configuration class for the server and model.

    To change the model which is used to make the prediction you have to change the MODEL attribute and depending on the model also the NUM_CLASSES and CSV_PATH attributes.

    You probably have to change the CROPPED_HEIGHT and CROPPED_WIDTH attributes. 
    These values are used to remove the UI elements from the screenshot such as the map or score overview.
    These values depend on your monitor size and you might have to try out some values to get the best result. 
    In the "images" folder you can find the image called "combined_image.png" that is used as the input for the model.
    Check if there are any UI elements in the image and if so, change the CROPPED_HEIGHT and CROPPED_WIDTH attributes.
    This image will be created after you run the extension and press the play button.


    Attributes:
        CROPPED_HEIGHT (int): Height of the cropped image.
        CROPPED_WIDTH (int): Width of the cropped image.
        HEIGHT (int): Height of the input image.
        WIDTH (int): Width of the input image.
        NUM_CLASSES (int): Number of classes (geohashes). Depending on the model, this number can be different, because the model was trained on a different dataset.
        WEIGHTED_MIDPOINT (bool): Whether to use the weighted midpoint or not. If True, the model will predict the weighted midpoint of the top five predictions using the haversine distance.
        CWD (str): Current working directory.
        PRETRAINED_MODELS_PATH (str): Path to the pretrained models.
        CONTINENT_MODELS_PATH (str): Path to the continent models.
        MODEL (str): Name of the pretrained model state file.
    """
    CROPPED_HEIGHT = 1000
    CROPPED_WIDTH = 1760
    HEIGHT = 512
    WIDTH = 2560
    # NUM_CLASSES = 3139 # Default
    NUM_CLASSES = 3725  # Use this for the "finalpretrainedresnet50_14epoch_all_Hav_Aug_Google3.tar" model
    # NUM_CLASSES = 3789  # Use this for the "stratsamppretrainedresnet50_14epoch_all_Hav_Aug_Google3.tar" model
    WEIGHTED_MIDPOINT = False

    CWD = os.path.dirname(os.getcwd())
    PRETRAINED_MODELS_PATH = os.path.join(CWD, "server", "python", "pretrained_models")
    CONTINENT_MODELS_PATH = os.path.join(PRETRAINED_MODELS_PATH, "continent_models")
    # MODEL = "pretrainedresnet50contihead_14epoch.tar"
    # MODEL = "pretrainedtransformer_14epoch.tar"
    # MODEL = "pretrainedresnet50_20epoch_all.tar"
    # MODEL = "haversinepretrainedresnet50_14epoch.tar"
    # MODEL = "augmentedpretrainedresnet50_14epoch.tar"
    MODEL = "finalpretrainedresnet50_14epoch_all_Hav_Aug_Google3.tar"
    # MODEL = "stratsamppretrainedresnet50_14epoch_all_Hav_Aug_Google_StratSamp.tar"

    PYTHON_PATH = os.path.join(CWD, "server", "python")
    UTILS_PATH = os.path.join(PYTHON_PATH, "utils")
    PERFORMANCE_PATH = os.path.join(PYTHON_PATH, "performance")
    DATASET_PATH = os.path.join(PYTHON_PATH, "dataset")
    SEQUENTIAL_CSV_PATH = os.path.join(UTILS_PATH, "coordinates_sequential.csv")
    # CSV_PATH = os.path.join(UTILS_PATH, "coordinates_end_to_end.csv")
    CSV_PATH = os.path.join(UTILS_PATH, "mapping_augment_google.csv")  # Use this for the "finalpretrainedresnet50_14epoch_all_Hav_Aug_Google3.tar" model
    # CSV_PATH = os.path.join(UTILS_PATH, "mapping_augmented_google_stratsamp.csv")  # Use this for the "startsamppretrainedresnet50_14epoch_all_Hav_Aug_Google3.tar" model

    IMAGES_PATH = os.path.join(CWD, "server", "images")
    PREDICTION_PLOT_PATH = os.path.join(CWD, "geoguessr_extension", "assets", "prediction_plot")
