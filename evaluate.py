# """
# Fracture Detection Model - Evaluation Script
# =============================================
# Evaluates the trained model on the validation/test dataset and produces:
#   1. Confusion Matrix
#   2. Precision, Recall, F1-Score per class
#   3. Classification Report
#   4. ROC Curve and AUC
#   5. Accuracy on test set

# Usage:
#     python evaluate.py

# Requirements:
#     - torch
#     - torchvision
#     - scikit-learn
#     - matplotlib
#     - seaborn
# """

# import torch
# import torch.nn as nn
# from torch.utils.data import DataLoader
# from torchvision import datasets, transforms, models
# from sklearn.metrics import (
#     confusion_matrix,
#     classification_report,
#     precision_score,
#     recall_score,
#     f1_score,
#     roc_curve,
#     auc,
#     roc_auc_score,
# )
# import matplotlib.pyplot as plt
# import seaborn as sns
# import numpy as np
# import os
# from PIL import ImageFile
# ImageFile.LOAD_TRUNCATED_IMAGES = True  # ← ADD THIS LINE

# # ─── Configuration ───────────────────────────────────────────────────────────

# MODEL_PATH = "backend/app/best_model.pth"
# VAL_DIR = "dataset/val"
# IMAGE_SIZE = 224
# BATCH_SIZE = 32
# DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# # ─── Model Architecture (ResNet50 - matching your saved model) ─────────────

# class FractureDetectionModel(nn.Module):
#     """
#     ResNet50-based model — matches your training architecture.
#     Confirmed by state_dict: 3 blocks in layer1, fc=[2,2048].
#     """
#     def __init__(self, num_classes=2):
#         super(FractureDetectionModel, self).__init__()
#         backbone = models.resnet50(weights=None)
#         num_features = backbone.fc.in_features  # 2048
#         backbone.fc = nn.Linear(num_features, num_classes)
#         self.model = backbone

#     def forward(self, x):
#         return self.model(x)


# def load_model_smart(model_path, model, device):
#     """
#     Load state dict with automatic key prefix handling.
#     Handles both cases:
#     - Keys WITH 'model.' prefix (from wrapper class save)
#     - Keys WITHOUT 'model.' prefix (from backbone save)
#     """
#     state_dict = torch.load(model_path, map_location=device, weights_only=True)

#     first_key = list(state_dict.keys())[0]

#     if first_key.startswith("model."):
#         # Keys already have 'model.' prefix — load directly
#         # But handle num_batches_tracked mismatch
#         model_state = model.state_dict()
#         filtered = {k: v for k, v in state_dict.items() if k in model_state}
#         model.load_state_dict(filtered, strict=False)
#         print("       (Loaded keys with 'model.' prefix)")
#     else:
#         # Keys are raw — add 'model.' prefix
#         new_state_dict = {}
#         model_state = model.state_dict()
#         for key, value in state_dict.items():
#             new_key = "model." + key
#             if new_key in model_state:
#                 new_state_dict[new_key] = value
#         model.load_state_dict(new_state_dict, strict=False)
#         print("       (Added 'model.' prefix to raw keys)")

#     return model


# # ─── Data Loading ────────────────────────────────────────────────────────────

# def get_val_transforms():
#     """Transforms for validation/test images (no augmentation)."""
#     return transforms.Compose([
#         transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
#         transforms.ToTensor(),
#         transforms.Normalize(mean=[0.485, 0.456, 0.406],
#                              std=[0.229, 0.224, 0.225]),
#     ])


# def load_test_data(val_dir):
#     """Load validation/test dataset."""
#     dataset = datasets.ImageFolder(
#         root=val_dir,
#         transform=get_val_transforms(),
#     )
#     dataloader = DataLoader(
#         dataset,
#         batch_size=BATCH_SIZE,
#         shuffle=False,
#         num_workers=0,
#         pin_memory=False,
#     )
#     return dataset, dataloader


# # ─── Evaluation ──────────────────────────────────────────────────────────────

# def evaluate_model(model, dataloader, device):
#     """Run inference and collect predictions and probabilities."""
#     model.eval()
#     model.to(device)

#     all_labels = []
#     all_preds = []
#     all_probs = []

#     with torch.no_grad():
#         for images, labels in dataloader:
#             images, labels = images.to(device), labels.to(device)

#             outputs = model(images)
#             probabilities = torch.softmax(outputs, dim=1)

#             _, predicted = torch.max(outputs, 1)

#             all_labels.extend(labels.cpu().numpy())
#             all_preds.extend(predicted.cpu().numpy())
#             all_probs.extend(probabilities.cpu().numpy())

#     return np.array(all_labels), np.array(all_preds), np.array(all_probs)


# # ─── Visualization Functions ─────────────────────────────────────────────────

# def plot_confusion_matrix(y_true, y_pred, class_names):
#     """Plot and save confusion matrix."""
#     cm = confusion_matrix(y_true, y_pred)
#     plt.figure(figsize=(6, 5))
#     sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
#                 xticklabels=class_names, yticklabels=class_names)
#     plt.xlabel("Predicted Label")
#     plt.ylabel("True Label")
#     plt.title("Confusion Matrix")
#     plt.tight_layout()
#     plt.savefig("evaluation_results/confusion_matrix.png", dpi=150)
#     plt.close()
#     print("  -> Confusion Matrix saved to evaluation_results/confusion_matrix.png")
#     return cm


# def plot_roc_curve(y_true, y_probs, class_names):
#     """Plot and save ROC curve with AUC score."""
#     plt.figure(figsize=(6, 5))

#     if len(class_names) == 2:
#         # Binary: use probability of class 1
#         prob_class1 = y_probs[:, 1]
#         fpr, tpr, thresholds = roc_curve(y_true, prob_class1)
#         roc_auc = auc(fpr, tpr)
#         plt.plot(fpr, tpr, color="darkorange", lw=2,
#                  label=f"ROC curve (AUC = {roc_auc:.4f})")
#         plt.plot([0, 1], [0, 1], color="navy", lw=2, linestyle="--")
#         plt.legend(loc="lower right")
#     else:
#         # Multi-class: one-vs-rest
#         for i, cls_name in enumerate(class_names):
#             y_true_bin = (y_true == i).astype(int)
#             fpr, tpr, _ = roc_curve(y_true_bin, y_probs[:, i])
#             roc_auc_i = auc(fpr, tpr)
#             plt.plot(fpr, tpr, lw=2,
#                      label=f"{cls_name} (AUC = {roc_auc_i:.4f})")
#         plt.plot([0, 1], [0, 1], color="navy", lw=2, linestyle="--")
#         plt.legend(loc="lower right")

#     plt.xlim([0.0, 1.0])
#     plt.ylim([0.0, 1.05])
#     plt.xlabel("False Positive Rate")
#     plt.ylabel("True Positive Rate")
#     plt.title("Receiver Operating Characteristic (ROC) Curve")
#     plt.tight_layout()
#     plt.savefig("evaluation_results/roc_curve.png", dpi=150)
#     plt.close()
#     print("  -> ROC Curve saved to evaluation_results/roc_curve.png")


# def plot_class_distribution(y_true, y_pred, class_names):
#     """Plot bar chart of predicted vs actual class distribution."""
#     fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))

#     unique, counts_true = np.unique(y_true, return_counts=True)
#     ax1.bar([class_names[i] for i in unique], counts_true, color="steelblue")
#     ax1.set_title("True Label Distribution")
#     ax1.set_ylabel("Count")

#     unique_p, counts_pred = np.unique(y_pred, return_counts=True)
#     ax2.bar([class_names[i] for i in unique_p], counts_pred, color="coral")
#     ax2.set_title("Predicted Label Distribution")
#     ax2.set_ylabel("Count")

#     plt.tight_layout()
#     plt.savefig("evaluation_results/class_distribution.png", dpi=150)
#     plt.close()
#     print("  -> Class Distribution saved to evaluation_results/class_distribution.png")


# # ─── Main ────────────────────────────────────────────────────────────────────

# def main():
#     print("=" * 60)
#     print("  FRACTURE DETECTION MODEL - EVALUATION")
#     print("=" * 60)

#     # Create output directory
#     os.makedirs("evaluation_results", exist_ok=True)

#     # 1. Load data
#     print("\n[1/5] Loading test/validation data...")
#     dataset, dataloader = load_test_data(VAL_DIR)
#     class_names = dataset.classes
#     print(f"       Classes: {class_names}")
#     print(f"       Total images: {len(dataset)}")
#     for cls_name in class_names:
#         cls_idx = class_names.index(cls_name)
#         count = sum(1 for y in dataset.targets if y == cls_idx)
#         print(f"         - {cls_name}: {count} images")

#     # 2. Load model
#     print(f"\n[2/5] Loading model from {MODEL_PATH}...")
#     model = FractureDetectionModel(num_classes=len(class_names))
#     model = load_model_smart(MODEL_PATH, model, DEVICE)
#     print("       Model loaded successfully.")

#     # 3. Run evaluation
#     print("\n[3/5] Running inference on test set...")
#     y_true, y_pred, y_probs = evaluate_model(model, dataloader, DEVICE)
#     print("       Inference complete.")

#     # 4. Compute metrics
#     print("\n[4/5] Computing metrics...")

#     # Overall accuracy
#     accuracy = np.mean(y_true == y_pred)
#     print(f"\n       Overall Accuracy:  {accuracy:.4f} ({accuracy*100:.2f}%)")

#     # Per-class Precision, Recall, F1
#     print("\n       ┌──────────────────────────────────────────────────┐")
#     print("       │         Per-Class Performance Metrics            │")
#     print("       └──────────────────────────────────────────────────┘")

#     for i, cls_name in enumerate(class_names):
#         cls_mask = y_true == i
#         if np.sum(cls_mask) == 0:
#             print(f"\n       Class '{cls_name}': No samples found in test set.")
#             continue

#         prec = precision_score(y_true, y_pred, labels=[i], zero_division=0)
#         rec = recall_score(y_true, y_pred, labels=[i], zero_division=0)
#         f1 = f1_score(y_true, y_pred, labels=[i], zero_division=0)

#         print(f"\n       Class: {cls_name}")
#         print(f"         Precision:  {prec:.4f}")
#         print(f"         Recall:     {rec:.4f}")
#         print(f"         F1-Score:   {f1:.4f}")

#     # Classification report
#     print("\n       ┌──────────────────────────────────────────────────┐")
#     print("       │              Classification Report               │")
#     print("       └──────────────────────────────────────────────────┘")
#     report = classification_report(y_true, y_pred, target_names=class_names)
#     print(report)

#     # ROC AUC
#     if len(class_names) == 2:
#         roc_auc_val = roc_auc_score(y_true, y_probs[:, 1])
#         print(f"       ROC AUC Score:   {roc_auc_val:.4f}")

#     # Save metrics to text file
#     with open("evaluation_results/metrics.txt", "w") as f:
#         f.write("=" * 50 + "\n")
#         f.write("FRACTURE DETECTION MODEL - EVALUATION METRICS\n")
#         f.write("=" * 50 + "\n\n")
#         f.write(f"Overall Accuracy:  {accuracy:.4f} ({accuracy*100:.2f}%)\n\n")
#         f.write("Per-Class Metrics:\n")
#         for i, cls_name in enumerate(class_names):
#             prec = precision_score(y_true, y_pred, labels=[i], zero_division=0)
#             rec = recall_score(y_true, y_pred, labels=[i], zero_division=0)
#             f1 = f1_score(y_true, y_pred, labels=[i], zero_division=0)
#             f.write(f"\n  Class: {cls_name}\n")
#             f.write(f"    Precision: {prec:.4f}\n")
#             f.write(f"    Recall:    {rec:.4f}\n")
#             f.write(f"    F1-Score:  {f1:.4f}\n")
#         f.write(f"\nClassification Report:\n")
#         f.write(report)
#         if len(class_names) == 2:
#             f.write(f"\nROC AUC Score: {roc_auc_val:.4f}\n")
#     print("       -> Metrics saved to evaluation_results/metrics.txt")

#     # 5. Generate visualizations
#     print("\n[5/5] Generating visualizations...")

#     cm = plot_confusion_matrix(y_true, y_pred, class_names)
#     plot_roc_curve(y_true, y_probs, class_names)
#     plot_class_distribution(y_true, y_pred, class_names)

#     print("\n" + "=" * 60)
#     print("  EVALUATION COMPLETE!")
#     print("  Results saved to: evaluation_results/")
#     print("=" * 60)


# if __name__ == "__main__":
#     main()


"""Evaluate the saved model on dataset/val.

Run from the project root:
    python evaluate_safe.py

For a trustworthy final claim, point EVAL_DIR to a completely untouched test
set instead of the validation set.
"""
"""import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import torch
import torch.nn as nn
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_recall_fscore_support,
    roc_auc_score,
    roc_curve,
)
from torch.utils.data import DataLoader
from torchvision import datasets, models, transforms

EVAL_DIR = Path("dataset/val")
MODEL_PATH = Path("backend/app/best_model.pth")
OUTPUT_DIR = Path("evaluation_results")
CLASS_NAMES = ["fracture", "no_fracture"]
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def load_model():
    model = models.resnet50(weights=None)
    model.fc = nn.Linear(model.fc.in_features, 2)
    checkpoint = torch.load(MODEL_PATH, map_location=DEVICE, weights_only=True)
    if any(key.startswith("model.") for key in checkpoint):
        checkpoint = {key[6:]: value for key, value in checkpoint.items() if key.startswith("model.")}
    model.load_state_dict(checkpoint, strict=True)
    return model.to(DEVICE).eval()


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])
    dataset = datasets.ImageFolder(str(EVAL_DIR), transform=transform)
    if dataset.classes != CLASS_NAMES:
        raise SystemExit(f"ERROR: found classes {dataset.classes}; expected {CLASS_NAMES}")

    loader = DataLoader(dataset, batch_size=32, shuffle=False, num_workers=0)
    model = load_model()
    y_true, y_pred, y_prob = [], [], []

    with torch.inference_mode():
        for images, labels in loader:
            outputs = model(images.to(DEVICE))
            probs = torch.softmax(outputs, dim=1).cpu().numpy()
            y_true.extend(labels.numpy())
            y_pred.extend(outputs.argmax(dim=1).cpu().numpy())
            y_prob.extend(probs)

    y_true, y_pred, y_prob = np.array(y_true), np.array(y_pred), np.array(y_prob)
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    precision, recall, f1, support = precision_recall_fscore_support(
        y_true, y_pred, labels=[0, 1], zero_division=0
    )
    accuracy = accuracy_score(y_true, y_pred)
    auc = roc_auc_score(y_true, y_prob[:, 1]) if len(np.unique(y_true)) == 2 else None

    # For class 0 = fracture: TP=cm[0,0], FN=cm[0,1], FP=cm[1,0], TN=cm[1,1].
    tn, fp, fn, tp = cm.ravel()
    specificity = tn / (tn + fp) if (tn + fp) else 0.0

    print("\nEVALUATION RESULTS")
    print("=" * 60)
    print(f"Evaluation folder: {EVAL_DIR}")
    print(f"Images evaluated: {len(dataset)}")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"ROC-AUC: {auc:.4f}" if auc is not None else "ROC-AUC: unavailable")
    print(f"Fracture sensitivity/recall: {recall[0]:.4f}")
    print(f"No-fracture specificity: {specificity:.4f}")
    print("\n" + classification_report(y_true, y_pred, target_names=CLASS_NAMES, zero_division=0))

    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=CLASS_NAMES, yticklabels=CLASS_NAMES)
    plt.xlabel("Predicted label")
    plt.ylabel("True label")
    plt.title("Confusion Matrix")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "confusion_matrix.png", dpi=180)
    plt.close()

    if auc is not None:
        fpr, tpr, _ = roc_curve(y_true, y_prob[:, 1])
        plt.figure(figsize=(6, 5))
        plt.plot(fpr, tpr, label=f"AUC = {auc:.4f}", linewidth=2)
        plt.plot([0, 1], [0, 1], "--", color="gray")
        plt.xlabel("False positive rate")
        plt.ylabel("True positive rate")
        plt.title("ROC Curve")
        plt.legend(loc="lower right")
        plt.tight_layout()
        plt.savefig(OUTPUT_DIR / "roc_curve.png", dpi=180)
        plt.close()

    metrics = {
        "evaluation_folder": str(EVAL_DIR),
        "images_evaluated": len(dataset),
        "classes": CLASS_NAMES,
        "accuracy": float(accuracy),
        "roc_auc": float(auc) if auc is not None else None,
        "fracture_sensitivity": float(recall[0]),
        "no_fracture_specificity": float(specificity),
        "confusion_matrix": cm.tolist(),
        "precision": precision.tolist(),
        "recall": recall.tolist(),
        "f1": f1.tolist(),
        "support": support.tolist(),
    }
    (OUTPUT_DIR / "metrics_safe.json").write_text(json.dumps(metrics, indent=2))
    print(f"Saved evaluation files to {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
"""

"""Robust evaluation script.
Run from the project root with: python evaluate_fixed.py
It skips unreadable/corrupt images and records their paths.
"""
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import torch
import torch.nn as nn
from PIL import Image, ImageFile, UnidentifiedImageError
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_recall_fscore_support,
    roc_auc_score,
    roc_curve,
)
from torch.utils.data import DataLoader
from torchvision import datasets, models, transforms

ImageFile.LOAD_TRUNCATED_IMAGES = True
EVAL_DIR = Path("dataset/val")
MODEL_PATH = Path("backend/app/best_model.pth")
OUTPUT_DIR = Path("evaluation_results")
CLASS_NAMES = ["fracture", "no_fracture"]
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def readable(path):
    try:
        with Image.open(path) as image:
            image.verify()
        return True
    except (UnidentifiedImageError, OSError, ValueError):
        return False


def load_model():
    model = models.resnet50(weights=None)
    model.fc = nn.Linear(model.fc.in_features, 2)
    state = torch.load(MODEL_PATH, map_location=DEVICE, weights_only=True)
    if any(key.startswith("model.") for key in state):
        state = {key[6:]: value for key, value in state.items() if key.startswith("model.")}
    model.load_state_dict(state, strict=True)
    return model.to(DEVICE).eval()


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])
    dataset = datasets.ImageFolder(str(EVAL_DIR), transform=transform)
    if dataset.classes != CLASS_NAMES:
        raise SystemExit(f"ERROR: found classes {dataset.classes}; expected {CLASS_NAMES}")

    original = list(dataset.samples)
    valid_samples = [(path, target) for path, target in original if readable(path)]
    skipped = [path for path, _ in original if not readable(path)]
    dataset.samples = valid_samples
    dataset.imgs = valid_samples
    dataset.targets = [target for _, target in valid_samples]

    print(f"Skipped unreadable images: {len(skipped)}")
    for path in skipped:
        print(f"  {path}")
    (OUTPUT_DIR / "unreadable_images.txt").write_text("\n".join(skipped))

    if not valid_samples:
        raise SystemExit("ERROR: no readable evaluation images remain.")

    loader = DataLoader(dataset, batch_size=32, shuffle=False, num_workers=0)
    model = load_model()
    y_true, y_pred, y_prob = [], [], []

    with torch.inference_mode():
        for images, labels in loader:
            outputs = model(images.to(DEVICE))
            probabilities = torch.softmax(outputs, dim=1).cpu().numpy()
            y_true.extend(labels.numpy())
            y_pred.extend(outputs.argmax(dim=1).cpu().numpy())
            y_prob.extend(probabilities)

    y_true, y_pred, y_prob = map(np.asarray, (y_true, y_pred, y_prob))
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    precision, recall, f1, support = precision_recall_fscore_support(
        y_true, y_pred, labels=[0, 1], zero_division=0
    )
    accuracy = accuracy_score(y_true, y_pred)
    auc = roc_auc_score(y_true, y_prob[:, 1]) if len(np.unique(y_true)) == 2 else None
    # Since class 0 is fracture, recall[0] is fracture sensitivity.
    fracture_sensitivity = float(recall[0])
    tn, fp, fn, tp = cm.ravel()
    no_fracture_specificity = float(tn / (tn + fp)) if tn + fp else 0.0

    print("\nEVALUATION RESULTS")
    print("=" * 60)
    print(f"Readable images evaluated: {len(dataset)}")
    print(f"Accuracy: {accuracy:.4f} ({accuracy * 100:.2f}%)")
    print(f"ROC-AUC: {auc:.4f}" if auc is not None else "ROC-AUC: unavailable")
    print(f"Fracture sensitivity/recall: {fracture_sensitivity:.4f}")
    print(f"No-fracture specificity: {no_fracture_specificity:.4f}")
    print("\n" + classification_report(y_true, y_pred, target_names=CLASS_NAMES, zero_division=0))

    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=CLASS_NAMES, yticklabels=CLASS_NAMES)
    plt.xlabel("Predicted label")
    plt.ylabel("True label")
    plt.title("Confusion Matrix")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "confusion_matrix.png", dpi=180)
    plt.close()

    if auc is not None:
        fpr, tpr, _ = roc_curve(y_true, y_prob[:, 1])
        plt.figure(figsize=(6, 5))
        plt.plot(fpr, tpr, label=f"AUC = {auc:.4f}", linewidth=2)
        plt.plot([0, 1], [0, 1], "--", color="gray")
        plt.xlabel("False positive rate")
        plt.ylabel("True positive rate")
        plt.title("ROC Curve")
        plt.legend(loc="lower right")
        plt.tight_layout()
        plt.savefig(OUTPUT_DIR / "roc_curve.png", dpi=180)
        plt.close()

    metrics = {
        "evaluation_folder": str(EVAL_DIR),
        "readable_images_evaluated": len(dataset),
        "unreadable_images_skipped": len(skipped),
        "classes": CLASS_NAMES,
        "accuracy": float(accuracy),
        "roc_auc": float(auc) if auc is not None else None,
        "fracture_sensitivity": fracture_sensitivity,
        "no_fracture_specificity": no_fracture_specificity,
        "confusion_matrix": cm.tolist(),
        "precision": precision.tolist(),
        "recall": recall.tolist(),
        "f1": f1.tolist(),
        "support": support.tolist(),
    }
    (OUTPUT_DIR / "metrics_safe.json").write_text(json.dumps(metrics, indent=2))
    print(f"Results saved to {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()