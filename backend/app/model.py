# # """
# # Fracture Detection - Model Module
# # ==================================
# # Defines the ResNet50 model architecture, loads trained weights,
# # and provides inference functions used by the FastAPI backend.

# # This file is imported by main.py.
# # """

# # import torch
# # import torch.nn as nn
# # from torchvision import models, transforms
# # from PIL import Image
# # import io
# # import os

# # # ─── Configuration ───────────────────────────────────────────────────────────

# # MODEL_PATH = os.path.join(os.path.dirname(__file__), "best_model.pth")
# # IMAGE_SIZE = 224
# # CLASS_NAMES = ["no_fractured", "fractured"]
# # LABELS = {
# #     "no_fractured": "No Fracture",
# #     "fractured": "Fracture Detected",
# # }
# # DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# # # ─── Model Architecture ──────────────────────────────────────────────────────

# # def get_model():
# #     """Create ResNet50 model with 2 output classes."""
# #     model = models.resnet50(weights=None)
# #     num_features = model.fc.in_features  # 2048
# #     model.fc = nn.Linear(num_features, 2)
# #     return model


# # # ─── Load Trained Model ──────────────────────────────────────────────────────

# # def load_model_with_key_fix(model_path, model, device):
# #     """
# #     Load state dict with automatic key prefix handling.
# #     Handles both cases: keys with or without 'model.' prefix.
# #     Filters out mismatched keys (e.g., num_batches_tracked).
# #     """
# #     state_dict = torch.load(model_path, map_location=device, weights_only=True)

# #     first_key = list(state_dict.keys())[0]

# #     if first_key.startswith("model."):
# #         # Keys already have 'model.' prefix
# #         model_state = model.state_dict()
# #         filtered = {k: v for k, v in state_dict.items()
# #                     if k in model_state and v.shape == model_state[k].shape}
# #         model.load_state_dict(filtered, strict=False)
# #     else:
# #         # Keys are raw — add 'model.' prefix
# #         model_state = model.state_dict()
# #         new_state_dict = {}
# #         for key, value in state_dict.items():
# #             new_key = "model." + key
# #             if new_key in model_state and value.shape == model_state[new_key].shape:
# #                 new_state_dict[new_key] = value
# #         model.load_state_dict(new_state_dict, strict=False)

# #     return model


# # # ─── Initialize Model ────────────────────────────────────────────────────────

# # model = get_model()
# # model = load_model_with_key_fix(MODEL_PATH, model, DEVICE)
# # model = model.to(DEVICE)
# # model.eval()

# # print(f"[model.py] Model loaded from {MODEL_PATH}")
# # print(f"[model.py] Device: {DEVICE}")
# # print(f"[model.py] Classes: {CLASS_NAMES}")

# # # ─── Preprocessing Pipeline ──────────────────────────────────────────────────

# # transform = transforms.Compose([
# #     transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
# #     transforms.ToTensor(),
# #     transforms.Normalize(
# #         mean=[0.485, 0.456, 0.406],
# #         std=[0.229, 0.224, 0.225]
# #     )
# # ])

# # # ─── Inference Function ──────────────────────────────────────────────────────

# # def predict_image(image_bytes: bytes):
# #     """
# #     Predict whether an X-ray image shows a fracture.

# #     Args:
# #         image_bytes: Raw bytes of the image file

# #     Returns:
# #         dict with 'prediction' and 'confidence' keys
# #     """
# #     image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
# #     image_tensor = transform(image).unsqueeze(0).to(DEVICE)

# #     with torch.no_grad():
# #         outputs = model(image_tensor)
# #         probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
# #         prediction_idx = torch.argmax(probabilities).item()
# #         confidence = probabilities[prediction_idx].item()

# #     pred_class = CLASS_NAMES[prediction_idx]
# #     pred_label = LABELS[pred_class]

# #     return {
# #         "prediction": pred_label,
# #         "confidence": confidence,
# #         "class_index": prediction_idx,
# #         "class_name": pred_class,
# #         "probabilities": {
# #             CLASS_NAMES[0]: float(probabilities[0].item()),
# #             CLASS_NAMES[1]: float(probabilities[1].item()),
# #         },
# #     }


# """
# Fracture Detection - Model Module
# ==================================
# Defines the ResNet50 model architecture, loads trained weights,
# and provides inference functions used by the FastAPI backend.
# """

# import io
# import os

# import torch
# import torch.nn as nn
# from PIL import Image
# from torchvision import models, transforms

# # ───────────────────────────────────────────────────────────────
# # Configuration
# # ───────────────────────────────────────────────────────────────

# MODEL_PATH = os.path.join(os.path.dirname(__file__), "best_model.pth")

# IMAGE_SIZE = 224

# CLASS_NAMES = [
#     "no_fractured",
#     "fractured",
# ]

# LABELS = {
#     "no_fractured": "No Fracture",
#     "fractured": "Fracture Detected",
# }

# DEVICE = torch.device(
#     "cuda" if torch.cuda.is_available() else "cpu"
# )

# # ───────────────────────────────────────────────────────────────
# # Model Architecture
# # ───────────────────────────────────────────────────────────────


# def get_model():
#     """Create ResNet50 model."""

#     model = models.resnet50(weights=None)

#     num_features = model.fc.in_features

#     model.fc = nn.Linear(num_features, 2)

#     return model


# # ───────────────────────────────────────────────────────────────
# # Load Weights
# # ───────────────────────────────────────────────────────────────


# def load_model_with_key_fix(model_path, model, device):
#     """
#     Load checkpoint while handling different key formats.
#     """

#     state_dict = torch.load(
#         model_path,
#         map_location=device,
#         weights_only=True,
#     )

#     first_key = list(state_dict.keys())[0]

#     if first_key.startswith("model."):

#         model_state = model.state_dict()

#         filtered = {
#             k: v
#             for k, v in state_dict.items()
#             if k in model_state
#             and v.shape == model_state[k].shape
#         }

#         model.load_state_dict(
#             filtered,
#             strict=False,
#         )

#     else:

#         model_state = model.state_dict()

#         new_state = {}

#         for key, value in state_dict.items():

#             new_key = "model." + key

#             if (
#                 new_key in model_state
#                 and value.shape == model_state[new_key].shape
#             ):
#                 new_state[new_key] = value

#         model.load_state_dict(
#             new_state,
#             strict=False,
#         )

#     return model


# # ───────────────────────────────────────────────────────────────
# # Initialize Model
# # ───────────────────────────────────────────────────────────────

# model = get_model()

# model = load_model_with_key_fix(
#     MODEL_PATH,
#     model,
#     DEVICE,
# )

# model = model.to(DEVICE)

# model.eval()

# print(f"[model.py] Model loaded from {MODEL_PATH}")
# print(f"[model.py] Device: {DEVICE}")
# print(f"[model.py] Classes: {CLASS_NAMES}")

# # ───────────────────────────────────────────────────────────────
# # Image Transform
# # ───────────────────────────────────────────────────────────────

# transform = transforms.Compose(
#     [
#         transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
#         transforms.ToTensor(),
#         transforms.Normalize(
#             mean=[0.485, 0.456, 0.406],
#             std=[0.229, 0.224, 0.225],
#         ),
#     ]
# )

# # ───────────────────────────────────────────────────────────────
# # Prediction
# # ───────────────────────────────────────────────────────────────


# def predict_image(image_bytes: bytes):
#     """
#     Predict whether an X-ray contains a fracture.
#     """

#     # Always keep model in evaluation mode
#     model.eval()

#     # Clear any leftover gradients
#     model.zero_grad()

#     image = Image.open(
#         io.BytesIO(image_bytes)
#     ).convert("RGB")

#     image_tensor = (
#         transform(image)
#         .unsqueeze(0)
#         .to(DEVICE)
#     )

#     with torch.no_grad():

#         outputs = model(image_tensor)

#         probabilities = torch.nn.functional.softmax(
#             outputs[0],
#             dim=0,
#         )

#         prediction_idx = torch.argmax(
#             probabilities
#         ).item()

#         confidence = probabilities[
#             prediction_idx
#         ].item()

#     pred_class = CLASS_NAMES[prediction_idx]

#     pred_label = LABELS[pred_class]

#     return {
#         "prediction": pred_label,
#         "confidence": confidence,
#         "class_index": prediction_idx,
#         "class_name": pred_class,
#         "probabilities": {
#             CLASS_NAMES[0]: float(
#                 probabilities[0].item()
#             ),
#             CLASS_NAMES[1]: float(
#                 probabilities[1].item()
#             ),
#         },
#     }

"""
Fracture Detection - Model Module
==================================
"""

# import torch
# import torch.nn as nn
# from torchvision import models, transforms
# from PIL import Image
# import io
# import os

# # ─── Configuration ───────────────────────────────────────────────────────────

# MODEL_PATH = os.path.join(os.path.dirname(__file__), "best_model.pth")
# IMAGE_SIZE = 224
# CLASS_NAMES = ["fractured", "no_fractured"]
# LABELS = {
#     "no_fractured": "No Fracture",
#     "fractured": "Fracture Detected",
# }
# DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# # ─── Model Architecture ──────────────────────────────────────────────────────

# def get_model():
#     """Create ResNet50 model with 2 output classes."""
#     model = models.resnet50(weights=None)
#     num_features = model.fc.in_features
#     model.fc = nn.Linear(num_features, 2)
#     return model

# # ─── Load Trained Model ──────────────────────────────────────────────────────

# def load_model_with_key_fix(model_path, model, device):
#     state_dict = torch.load(model_path, map_location=device, weights_only=True)
    
#     first_key = list(state_dict.keys())[0]
#     print(f"[model.py] First key in checkpoint: {first_key}")
    
#     model_state = model.state_dict()
    
#     # Match keys regardless of 'model.' prefix
#     filtered = {}
#     for key, value in state_dict.items():
#         # Try with prefix
#         if key in model_state and value.shape == model_state[key].shape:
#             filtered[key] = value
#         # Try without prefix
#         elif "model." + key in model_state and value.shape == model_state["model." + key].shape:
#             filtered["model." + key] = value
#         # Try removing prefix
#         elif key.startswith("model.") and key[6:] in model_state:
#             clean_key = key[6:]
#             if clean_key in model_state and value.shape == model_state[clean_key].shape:
#                 filtered[clean_key] = value
    
#     if len(filtered) == 0:
#         raise RuntimeError(f"[model.py] ERROR: No matching keys found! Checkpoint has {len(state_dict)} keys, model expects {len(model_state)} keys.")
    
#     missing, unexpected = model.load_state_dict(filtered, strict=False)
#     print(f"[model.py] Loaded {len(filtered)}/{len(model_state)} parameters")
#     if missing:
#         print(f"[model.py] MISSING keys: {missing[:5]}")
#     if unexpected:
#         print(f"[model.py] UNEXPECTED keys: {unexpected[:5]}")
    
#     return model

# # ─── Initialize Model ────────────────────────────────────────────────────────

# model = get_model()
# model = load_model_with_key_fix(MODEL_PATH, model, DEVICE)
# model = model.to(DEVICE)
# model.eval()

# print(f"[model.py] Model loaded from {MODEL_PATH}")
# print(f"[model.py] Device: {DEVICE}")
# print(f"[model.py] Classes: {CLASS_NAMES}")

# # ─── Preprocessing Pipeline ──────────────────────────────────────────────────

# transform = transforms.Compose([
#     transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
#     transforms.ToTensor(),
#     transforms.Normalize(
#         mean=[0.485, 0.456, 0.406],
#         std=[0.229, 0.224, 0.225]
#     )
# ])

# # ─── Inference Function ──────────────────────────────────────────────────────

# def predict_image(image_bytes: bytes):
#     model.eval()
    
#     image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
#     image_tensor = transform(image).unsqueeze(0).to(DEVICE)

#     with torch.no_grad():
#         model.zero_grad()
#         outputs = model(image_tensor)
#         probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
#         prediction_idx = torch.argmax(probabilities).item()
#         confidence = probabilities[prediction_idx].item()
        
#         # Debug: print raw outputs
#         raw_values = outputs[0].cpu().numpy()
#         print(f"[model.py] Raw logits: {raw_values}")
#         print(f"[model.py] Softmax probs: class0={probabilities[0].item():.6f}, class1={probabilities[1].item():.6f}")

#     pred_class = CLASS_NAMES[prediction_idx]
#     pred_label = LABELS[pred_class]

#     return {
#         "prediction": pred_label,
#         "confidence": confidence,
#         "class_index": prediction_idx,
#         "class_name": pred_class,
#         "probabilities": {
#             CLASS_NAMES[0]: float(probabilities[0].item()),
#             CLASS_NAMES[1]: float(probabilities[1].item()),
#         },
#     }

import io
import os

import torch
import torch.nn as nn
from PIL import Image
from torchvision import models, transforms


MODEL_PATH = os.path.join(os.path.dirname(__file__), "best_model.pth")
IMAGE_SIZE = 224
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# This order must match the folder order used during training:
# fracture = 0, no_fracture = 1.
CLASS_NAMES = ["fracture", "no_fracture"]
LABELS = {
    "fracture": "Fracture Detected",
    "no_fracture": "No Fracture",
}

# This is a safety-review threshold, not a clinically validated threshold.
UNCERTAINTY_THRESHOLD = 0.80


def get_model():
    backbone = models.resnet50(weights=None)
    backbone.fc = nn.Linear(backbone.fc.in_features, len(CLASS_NAMES))
    return backbone


def load_model(model_path=MODEL_PATH):
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model checkpoint not found: {model_path}")

    model = get_model()
    checkpoint = torch.load(model_path, map_location=DEVICE, weights_only=True)

    # Support a raw ResNet checkpoint and a checkpoint saved through a wrapper.
    if any(key.startswith("model.") for key in checkpoint):
        checkpoint = {
            key[len("model."):]: value
            for key, value in checkpoint.items()
            if key.startswith("model.")
        }

    expected = model.state_dict()
    compatible = {
        key: value
        for key, value in checkpoint.items()
        if key in expected and value.shape == expected[key].shape
    }

    if len(compatible) != len(expected):
        missing = sorted(set(expected) - set(compatible))
        raise RuntimeError(
            "Checkpoint does not match the two-class ResNet50 architecture. "
            f"Loaded {len(compatible)}/{len(expected)} parameters. "
            f"Missing example: {missing[:3]}"
        )

    model.load_state_dict(compatible, strict=True)
    model.to(DEVICE)
    model.eval()
    return model


model = load_model()

transform = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225],
    ),
])


def predict_image(image_bytes: bytes):
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    image_tensor = transform(image).unsqueeze(0).to(DEVICE)

    with torch.inference_mode():
        probabilities = torch.softmax(model(image_tensor)[0], dim=0)

    predicted_index = int(torch.argmax(probabilities).item())
    confidence = float(probabilities[predicted_index].item())
    predicted_class = CLASS_NAMES[predicted_index]
    review_required = confidence < UNCERTAINTY_THRESHOLD

    return {
        "prediction": LABELS[predicted_class],
        "class_name": predicted_class,
        "class_index": predicted_index,
        "confidence": confidence,
        "probabilities": {
            CLASS_NAMES[index]: float(probabilities[index].item())
            for index in range(len(CLASS_NAMES))
        },
        "review_required": review_required,
        "uncertainty_threshold": UNCERTAINTY_THRESHOLD,
    }
