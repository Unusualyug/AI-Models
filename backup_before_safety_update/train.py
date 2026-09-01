"""Final safer training script.

Run from the project root:
    python train_safe.py

The script uses every valid image currently in dataset/train/ and uses
 dataset/val/ only for validation. It requires exactly these class folders:
    dataset/train/fracture
    dataset/train/no_fracture
    dataset/val/fracture
    dataset/val/no_fracture
"""
import copy
import json
import os
from pathlib import Path

import torch
import torch.nn as nn
import torch.optim as optim
from PIL import ImageFile
from torch.utils.data import DataLoader
from torchvision import datasets, models, transforms

ImageFile.LOAD_TRUNCATED_IMAGES = True

DATA_DIR = Path("dataset")
MODEL_PATH = Path("backend/app/best_model.pth")
METADATA_PATH = Path("backend/app/model_metadata.json")
CLASS_NAMES = ["fracture", "no_fracture"]
BATCH_SIZE = 4
NUM_EPOCHS = 10
PATIENCE = 3
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def validate_folders():
    for split in ("train", "val"):
        for class_name in CLASS_NAMES:
            folder = DATA_DIR / split / class_name
            if not folder.exists():
                raise SystemExit(f"ERROR: required folder is missing: {folder}")

    unexpected = []
    for split in ("train", "val"):
        split_dir = DATA_DIR / split
        names = {path.name for path in split_dir.iterdir() if path.is_dir()}
        unexpected.extend(f"{split}/{name}" for name in names - set(CLASS_NAMES))
    if unexpected:
        raise SystemExit(
            "ERROR: unexpected class folders found: " + ", ".join(unexpected)
        )


def main():
    validate_folders()
    print(f"Using device: {DEVICE}")
    print(f"Classes: {CLASS_NAMES}")

    data_transforms = {
        "train": transforms.Compose([
            transforms.RandomResizedCrop(224, scale=(0.85, 1.0)),
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ]),
        "val": transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ]),
    }

    image_datasets = {
        split: datasets.ImageFolder(str(DATA_DIR / split), data_transforms[split])
        for split in ("train", "val")
    }

    for split, dataset in image_datasets.items():
        if dataset.classes != CLASS_NAMES:
            raise SystemExit(
                f"ERROR: {split} class order is {dataset.classes}; expected {CLASS_NAMES}."
            )
        print(f"{split.title()} images: {len(dataset)}")
        print({name: dataset.targets.count(index) for index, name in enumerate(CLASS_NAMES)})

    dataloaders = {
        "train": DataLoader(image_datasets["train"], batch_size=BATCH_SIZE, shuffle=True, num_workers=0),
        "val": DataLoader(image_datasets["val"], batch_size=BATCH_SIZE, shuffle=False, num_workers=0),
    }
    dataset_sizes = {split: len(image_datasets[split]) for split in ("train", "val")}

    weights = models.ResNet50_Weights.DEFAULT
    model = models.resnet50(weights=weights)
    model.fc = nn.Linear(model.fc.in_features, len(CLASS_NAMES))
    model.to(DEVICE)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=1e-4, weight_decay=1e-5)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode="min", factor=0.3, patience=1
    )

    best_state = copy.deepcopy(model.state_dict())
    best_val_loss = float("inf")
    epochs_without_improvement = 0
    history = []

    print("Starting training...")
    for epoch in range(NUM_EPOCHS):
        print(f"\nEpoch {epoch + 1}/{NUM_EPOCHS}")
        epoch_record = {"epoch": epoch + 1}

        for phase in ("train", "val"):
            model.train(phase == "train")
            running_loss = 0.0
            running_corrects = 0

            for inputs, labels in dataloaders[phase]:
                inputs, labels = inputs.to(DEVICE), labels.to(DEVICE)
                optimizer.zero_grad(set_to_none=True)

                with torch.set_grad_enabled(phase == "train"):
                    outputs = model(inputs)
                    loss = criterion(outputs, labels)
                    predictions = outputs.argmax(dim=1)
                    if phase == "train":
                        loss.backward()
                        optimizer.step()

                running_loss += loss.item() * inputs.size(0)
                running_corrects += (predictions == labels).sum().item()

            epoch_loss = running_loss / dataset_sizes[phase]
            epoch_acc = running_corrects / dataset_sizes[phase]
            epoch_record[f"{phase}_loss"] = epoch_loss
            epoch_record[f"{phase}_accuracy"] = epoch_acc
            print(f"{phase:5s} loss: {epoch_loss:.4f} | accuracy: {epoch_acc:.4f}")

            if phase == "val":
                scheduler.step(epoch_loss)
                if epoch_loss < best_val_loss:
                    best_val_loss = epoch_loss
                    best_state = copy.deepcopy(model.state_dict())
                    epochs_without_improvement = 0
                else:
                    epochs_without_improvement += 1

        history.append(epoch_record)
        if epochs_without_improvement >= PATIENCE:
            print("Early stopping: validation loss did not improve.")
            break

    model.load_state_dict(best_state)
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), MODEL_PATH)
    METADATA_PATH.write_text(json.dumps({
        "classes": CLASS_NAMES,
        "train_images": dataset_sizes["train"],
        "validation_images": dataset_sizes["val"],
        "image_size": 224,
        "model": "ResNet50",
        "best_validation_loss": best_val_loss,
        "history": history,
    }, indent=2))

    print(f"\nBest model saved to: {MODEL_PATH}")
    print(f"Training images used: {dataset_sizes['train']}")
    print(f"Validation images used: {dataset_sizes['val']}")
    print(f"Metadata saved to: {METADATA_PATH}")


if __name__ == "__main__":
    main()
