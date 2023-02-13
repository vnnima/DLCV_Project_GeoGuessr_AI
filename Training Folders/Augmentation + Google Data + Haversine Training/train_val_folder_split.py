import os
import random
import shutil

src_folder = r'D:\Projekt'
dst_folder = r'D:\Projekt_val'
# list all files in the source folder
files = os.listdir(src_folder)

# extract a random subset of files
selected_files = random.sample(files, k=17000)

# create the destination folder if it doesn't exist
if not os.path.exists(dst_folder):
    os.makedirs(dst_folder)

# move the selected files to the destination folder
for file in selected_files:
    src_path = os.path.join(src_folder, file)
    dst_path = os.path.join(dst_folder, file)
    shutil.move(src_path, dst_path)