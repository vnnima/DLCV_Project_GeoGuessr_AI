from torch.utils.data import Dataset
import pandas as pd
import os
from skimage import io
import torch
import numpy as np

class GeoImageDataset(Dataset):
    def __init__(self, root_dir, annotation_file, transform=None):
        self.root_dir = root_dir
        self.annotations = pd.read_csv(annotation_file)
        self.transform = transform

    def __len__(self):
        return len(self.annotations)

    def __getitem__(self, index):
        img_id = self.annotations.iloc[index, 0]
        img = torch.tensor(io.imread(os.path.join(self.root_dir, img_id)), dtype=torch.float32)
        y_label = torch.tensor(np.array([float(self.annotations.iloc[index, 1]), float(self.annotations.iloc[index, 2])]), dtype=torch.float32)

        if self.transform is not None:
            img = self.transform(img)

        return (img, y_label)