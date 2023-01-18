import os
import sys
import json
import pandas as pd
from config import Config


# Take a JSON string and append it to a csv file
def append_to_csv(json_string, csv_file):
    data = json.loads(json_string)
    df = pd.DataFrame(data, index=[0])
    df.to_csv(csv_file, mode='a', header=False, index=False)


if __name__ == "__main__":
    dataJSON = sys.argv[1]
    print(dataJSON)
    model_name = Config.MODEL.split("_")[0]
    append_to_csv(dataJSON, os.path.join(Config.PERFORMANCE_PATH, f"{model_name}_performance.csv"))

