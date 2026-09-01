# import os
# import shutil
# import pandas as pd
# import random

# # Read the labels CSV file
# labels = pd.read_csv("raw_data/labels.csv")

# # Create folder structure
# os.makedirs("dataset/train/fracture", exist_ok=True)
# os.makedirs("dataset/train/no_fracture", exist_ok=True)
# os.makedirs("dataset/val/fracture", exist_ok=True)
# os.makedirs("dataset/val/no_fracture", exist_ok=True)

# for _, row in labels.iterrows():
#     image_name = row["image"]
#     label = row["label"]

#     # Source path
#     src = os.path.join("raw_data/images", image_name)
    
#     # Decide folder
#     if label == 1 or label == "fracture":
#         folder = "fracture"
#     else:
#         folder = "no_fracture"
    
#     # Copy to train or val (80% train, 20% val)
#     if random.random() < 0.8:
#         dst = f"dataset/train/{folder}/{image_name}"
#     else:
#         dst = f"dataset/val/{folder}/{image_name}"
    
#     shutil.copy2(src, dst)

# print("Done! Images separated into folders.")

import os
import shutil
import random

# Set paths - UPDATE these to match your actual folders
images_dir = "raw_data/images"
labels_dir = "raw_data/labels"

output_train_fracture = "dataset/train/fracture"
output_train_nofracture = "dataset/train/no_fracture"
output_val_fracture = "dataset/val/fracture"
output_val_nofracture = "dataset/val/no_fracture"

# Create output folders
os.makedirs(output_train_fracture, exist_ok=True)
os.makedirs(output_train_nofracture, exist_ok=True)
os.makedirs(output_val_fracture, exist_ok=True)
os.makedirs(output_val_nofracture, exist_ok=True)

# Image extensions to look for
image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']

# Counters
fracture_count = 0
nofracture_count = 0
skipped = 0
errors = 0

# Get all files in images folder
files = os.listdir(images_dir)

for filename in files:
    # Check if it's an image file
    ext = os.path.splitext(filename)[1].lower()
    if ext not in image_extensions:
        continue
    
    # Find corresponding .txt file in labels folder
    txt_filename = os.path.splitext(filename)[0] + '.txt'
    txt_path = os.path.join(labels_dir, txt_filename)
    
    # Check if image already exists in dataset (prevent duplicates)
    train_f = os.path.join(output_train_fracture, filename)
    train_nf = os.path.join(output_train_nofracture, filename)
    val_f = os.path.join(output_val_fracture, filename)
    val_nf = os.path.join(output_val_nofracture, filename)
    
    if (os.path.exists(train_f) or os.path.exists(train_nf) or 
        os.path.exists(val_f) or os.path.exists(val_nf)):
        skipped += 1
        continue
    
    # Decide folder based on .txt file
    if os.path.exists(txt_path) and os.path.getsize(txt_path) > 0:
        # Non-empty txt = FRACTURE
        if random.random() < 0.8:
            dst = os.path.join(output_train_fracture, filename)
        else:
            dst = os.path.join(output_val_fracture, filename)
        shutil.copy2(os.path.join(images_dir, filename), dst)
        fracture_count += 1
    else:
        # Empty or missing txt = NO FRACTURE
        if random.random() < 0.8:
            dst = os.path.join(output_train_nofracture, filename)
        else:
            dst = os.path.join(output_val_nofracture, filename)
        shutil.copy2(os.path.join(images_dir, filename), dst)
        nofracture_count += 1

print(f"Done!")
print(f"Fracture images separated: {fracture_count}")
print(f"No fracture images separated: {nofracture_count}")
print(f"Already existed (skipped): {skipped}")
print(f"Errors: {errors}")
print()