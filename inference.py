"""
Fracture Detection Model - Inference on Sample Images
=====================================================
Runs the saved best_model.pth on sample X-ray images and produces:
  1. Prediction (Fracture / No Fracture)
  2. Confidence Score (softmax probability)
  3. Grad-CAM Heatmap overlay showing where the model is looking
  4. Side-by-side comparison: Original Image | Grad-CAM Overlay

Usage:
    python inference.py --image path/to/image.jpg
    python inference.py --folder path/to/images/
    python inference.py --sample 5          (random 5 images from val set)
"""

import torch
import torch.nn as nn
import torchvision.transforms as transforms
from torchvision import models
from PIL import Image, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
import matplotlib.pyplot as plt
import numpy as np
import os
import argparse
import glob

# ─── Configuration ───────────────────────────────────────────────────────────

MODEL_PATH = "backend/app/best_model.pth"
IMAGE_SIZE = 224
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
CLASS_NAMES = ["fractured", "no_fractured"]

# ─── Model Architecture (ResNet50) ──────────────────────────────────────────

class FractureDetectionModel(nn.Module):
    """
    ResNet50-based model — confirmed by your state_dict
    (3 blocks in layer1, fc=[2,2048]).
    """
    def __init__(self, num_classes=2):
        super(FractureDetectionModel, self).__init__()
        backbone = models.resnet50(weights=None)
        num_features = backbone.fc.in_features  # 2048
        backbone.fc = nn.Linear(num_features, num_classes)
        self.model = backbone

    def forward(self, x):
        return self.model(x)


def load_model_smart(model_path, model, device):
    """
    Load state dict with automatic key prefix handling.
    """
    state_dict = torch.load(model_path, map_location=device, weights_only=True)

    first_key = list(state_dict.keys())[0]

    if first_key.startswith("model."):
        # Keys already have 'model.' prefix
        model_state = model.state_dict()
        filtered = {k: v for k, v in state_dict.items() if k in model_state and v.shape == model_state[k].shape}
        model.load_state_dict(filtered, strict=False)
        print("       (Loaded keys with 'model.' prefix)")
    else:
        # Keys are raw — add 'model.' prefix
        model_state = model.state_dict()
        new_state_dict = {}
        for key, value in state_dict.items():
            new_key = "model." + key
            if new_key in model_state and value.shape == model_state[new_key].shape:
                new_state_dict[new_key] = value
        model.load_state_dict(new_state_dict, strict=False)
        print("       (Added 'model.' prefix to raw keys)")

    return model


# ─── Image Preprocessing ────────────────────────────────────────────────────

def preprocess_image(image_path):
    """Load and preprocess a single image for inference."""
    img = Image.open(image_path).convert("RGB")
    transform = transforms.Compose([
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std=[0.229, 0.224, 0.225]),
    ])
    input_tensor = transform(img).unsqueeze(0).to(DEVICE)
    return img, input_tensor


# ─── Inference ───────────────────────────────────────────────────────────────

def predict(model, input_tensor):
    """Run inference and return prediction + confidence."""
    model.eval()
    with torch.no_grad():
        outputs = model(input_tensor)
        probabilities = torch.softmax(outputs, dim=1)
        confidence, predicted = torch.max(probabilities, 1)

    pred_label = CLASS_NAMES[predicted.item()]
    conf_score = confidence.item()
    all_probs = probabilities[0].cpu().numpy()

    return pred_label, conf_score, all_probs


# ─── Grad-CAM Implementation ─────────────────────────────────────────────────

class GradCAM:
    """
    Grad-CAM implementation for ResNet50.
    Highlights the region of the image the model focuses on.
    """
    def __init__(self, model, target_layer_name="layer4"):
        self.model = model
        self.target_layer_name = target_layer_name
        self.gradients = None
        self.activations = None
        self._register_hooks()

    def _register_hooks(self):
        target_layer = self._find_target_layer()

        def forward_hook(module, input, output):
            self.activations = output.detach()

        def backward_hook(module, grad_input, grad_output):
            self.gradients = grad_output[0].detach()

        target_layer.register_forward_hook(forward_hook)
        target_layer.register_backward_hook(backward_hook)

    def _find_target_layer(self):
        """Find the target layer by name (searches inside model.model)."""
        for name, module in self.model.model.named_modules():
            if name == self.target_layer_name:
                return module
        raise ValueError(f"Target layer '{self.target_layer_name}' not found in model.")

    def generate(self, input_tensor, target_class=None):
        """Generate Grad-CAM heatmap."""
        self.model.zero_grad()
        output = self.model(input_tensor)

        if target_class is None:
            target_class = torch.argmax(output, dim=1).item()

        score = output[0, target_class]
        score.backward()

        gradients = self.gradients
        activations = self.activations

        pooled_gradients = torch.mean(gradients, dim=[0, 2, 3])

        for i in range(activations.shape[1]):
            activations[0, i, :, :] *= pooled_gradients[i]

        heatmap = torch.mean(activations[0], dim=0).cpu().numpy()
        heatmap = np.maximum(heatmap, 0)  # ReLU
        heatmap = heatmap / (heatmap.max() + 1e-8)

        return heatmap

    def overlay_on_image(self, image, heatmap, alpha=0.4):
        """Overlay the Grad-CAM heatmap on the original image."""
        heatmap_resized = Image.fromarray((heatmap * 255).astype(np.uint8))
        heatmap_resized = heatmap_resized.resize(
            (image.width, image.height), Image.BILINEAR
        )
        heatmap_array = np.array(heatmap_resized)

        # Apply red-yellow colormap
        colored = np.zeros((*heatmap_array.shape, 3), dtype=np.float32)
        colored[:, :, 0] = np.clip(heatmap_array * 2, 0, 255)
        colored[:, :, 1] = np.clip(heatmap_array * 2 - 128, 0, 255)
        colored[:, :, 2] = np.clip(255 - heatmap_array * 2, 0, 255)

        img_array = np.array(image).astype(np.float32)
        overlay = (1 - alpha) * img_array + alpha * colored
        overlay = np.clip(overlay, 0, 255).astype(np.uint8)

        return overlay


# ─── Visualization ───────────────────────────────────────────────────────────

def visualize_prediction(image, pred_label, confidence, all_probs,
                         heatmap_overlay=None, save_path=None):
    """Create a visual display of the prediction."""

    fig, axes = plt.subplots(1, 2, figsize=(12, 6))

    # Left: Original image
    axes[0].imshow(image)
    axes[0].set_title("Original X-Ray", fontsize=14)
    axes[0].axis("off")

    color = "red" if pred_label == "fractured" else "green"
    axes[0].text(0.02, 0.98, f"Prediction: {pred_label.upper()}",
                 transform=axes[0].transAxes, fontsize=12, color=color,
                 fontweight="bold", va="top",
                 bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                           edgecolor=color, alpha=0.8))

    # Right: Grad-CAM overlay
    if heatmap_overlay is not None:
        axes[1].imshow(heatmap_overlay)
        axes[1].set_title("Grad-CAM Heatmap Overlay", fontsize=14)

    axes[1].text(0.5, -0.05,
                 f"Confidence: {confidence:.4f} ({confidence*100:.1f}%)",
                 transform=axes[1].transAxes, ha="center", fontsize=11,
                 style="italic")

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"  -> Saved to: {save_path}")

    plt.close()


def save_results_summary(results, output_dir):
    """Save a summary table of all predictions."""
    summary_path = os.path.join(output_dir, "inference_summary.txt")
    with open(summary_path, "w") as f:
        f.write("=" * 70 + "\n")
        f.write("FRACTURE DETECTION - INFERENCE RESULTS SUMMARY\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Model: {MODEL_PATH}\n")
        f.write(f"Total Images Tested: {len(results)}\n\n")

        fracture_count = sum(1 for r in results if r["prediction"] == "fractured")
        no_fracture_count = len(results) - fracture_count

        f.write(f"Predictions:\n")
        f.write(f"  Fractured:    {fracture_count}\n")
        f.write(f"  No Fractured: {no_fracture_count}\n\n")

        f.write(f"{'Image':<50} {'Prediction':<15} {'Confidence':<12}\n")
        f.write("-" * 70 + "\n")
        for r in results:
            f.write(f"{r['image_name']:<50} {r['prediction']:<15} {r['confidence']:.4f}\n")

        avg_conf = np.mean([r["confidence"] for r in results])
        f.write(f"\nAverage Confidence: {avg_conf:.4f} ({avg_conf*100:.1f}%)\n")

    print(f"\n  -> Summary saved to: {summary_path}")


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Run inference on X-ray images with Grad-CAM visualization."
    )
    parser.add_argument("--image", type=str, help="Path to a single X-ray image")
    parser.add_argument("--folder", type=str, help="Path to a folder of X-ray images")
    parser.add_argument("--sample", type=int, default=0,
                        help="Number of random sample images from val set")
    parser.add_argument("--val-dir", type=str, default="dataset/val",
                        help="Validation directory for random sampling")
    args = parser.parse_args()

    print("=" * 60)
    print("  FRACTURE DETECTION - INFERENCE ON SAMPLE IMAGES")
    print("=" * 60)

    output_dir = "inference_results"
    os.makedirs(output_dir, exist_ok=True)

    # Load model
    print(f"\n[1/3] Loading model from {MODEL_PATH}...")
    model = FractureDetectionModel(num_classes=len(CLASS_NAMES))
    model = load_model_smart(MODEL_PATH, model, DEVICE)
    model.to(DEVICE)
    model.eval()
    print("       Model loaded successfully.")

    # Initialize Grad-CAM
    print("       Initializing Grad-CAM...")
    gradcam = GradCAM(model, target_layer_name="layer4")
    print("       Grad-CAM ready.")

    # Collect images
    image_paths = []

    if args.image:
        if not os.path.exists(args.image):
            print(f"Error: Image not found: {args.image}")
            return
        image_paths.append(args.image)
        print(f"\n[2/3] Testing on 1 image...")

    elif args.folder:
        if not os.path.isdir(args.folder):
            print(f"Error: Folder not found: {args.folder}")
            return
        extensions = ["*.jpg", "*.jpeg", "*.png", "*.bmp", "*.tif"]
        for ext in extensions:
            image_paths.extend(glob.glob(os.path.join(args.folder, ext)))
            image_paths.extend(glob.glob(os.path.join(args.folder, ext.upper())))
        print(f"\n[2/3] Testing on {len(image_paths)} images from {args.folder}...")

    elif args.sample > 0:
        print(f"\n[2/3] Sampling {args.sample} random images from {args.val_dir}...")
        all_images = []
        extensions = ["*.jpg", "*.jpeg", "*.png", "*.bmp", "*.tif"]
        for ext in extensions:
            all_images.extend(glob.glob(
                os.path.join(args.val_dir, "**", ext), recursive=True
            ))
            all_images.extend(glob.glob(
                os.path.join(args.val_dir, "**", ext.upper()), recursive=True
            ))
        if not all_images:
            print("Error: No images found in validation directory.")
            return
        image_paths = np.random.choice(all_images,
                                       size=min(args.sample, len(all_images)),
                                       replace=False).tolist()
        print(f"       Selected {len(image_paths)} random images.")

    else:
        print("\nPlease provide --image, --folder, or --sample argument.")
        print("Examples:")
        print("  python inference.py --image path/to/xray.jpg")
        print("  python inference.py --folder path/to/images/")
        print("  python inference.py --sample 10")
        return

    # Run inference on each image
    print(f"\n[3/3] Running inference...")
    print("-" * 60)

    results = []

    for idx, img_path in enumerate(image_paths):
        image_name = os.path.basename(img_path)
        print(f"\n  [{idx+1}/{len(image_paths)}] Processing: {image_name}")

        original_img, input_tensor = preprocess_image(img_path)
        pred_label, confidence, all_probs = predict(model, input_tensor)

        print(f"    Prediction:  {pred_label.upper()}")
        print(f"    Confidence:  {confidence:.4f} ({confidence*100:.1f}%)")

        heatmap = gradcam.generate(input_tensor)
        overlay = gradcam.overlay_on_image(original_img, heatmap)

        save_path = os.path.join(
            output_dir, f"result_{idx+1:03d}_{os.path.splitext(image_name)[0]}.png"
        )
        visualize_prediction(
            original_img, pred_label, confidence, all_probs,
            heatmap_overlay=overlay, save_path=save_path
        )

        results.append({
            "image_name": image_name,
            "prediction": pred_label,
            "confidence": confidence,
            "probabilities": all_probs,
            "save_path": save_path,
        })

    save_results_summary(results, output_dir)

    print("\n" + "=" * 60)
    print("  INFERENCE COMPLETE!")
    print(f"  Results saved to: {output_dir}/")
    print("=" * 60)


if __name__ == "__main__":
    main()
