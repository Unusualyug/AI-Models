"""
Fracture Detection - Grad-CAM Visualization
============================================
Implements Grad-CAM to highlight regions of interest in X-ray images.

This file is imported by main.py.
"""

import torch
import cv2
import numpy as np
import io
from PIL import Image


class GradCAM:
    """
    Grad-CAM implementation for ResNet50.
    Highlights the region of the image the model focuses on for prediction.
    """

    def __init__(self, model, target_layer):
        """
        Args:
            model: The ResNet50 model (backbone)
            target_layer: The target convolutional layer (e.g., model.layer4)
        """
        self.model = model
        self.target_layer = target_layer
        self.gradients = None
        self.activations = None

        # Use register_full_backward_hook to avoid FutureWarning
        self.target_layer.register_forward_hook(self.save_activations)
        self.target_layer.register_full_backward_hook(self.save_gradients)

    def save_activations(self, module, input, output):
        """Forward hook to save activations."""
        self.activations = output.detach()

    def save_gradients(self, module, grad_input, grad_output):
        """Full backward hook to save gradients."""
        self.gradients = grad_output[0].detach()

    def generate(self, input_tensor, class_idx=None):
        """
        Generate Grad-CAM heatmap.

        Args:
            input_tensor: Preprocessed image tensor [1, 3, 224, 224]
            class_idx: Target class index (None = use predicted class)

        Returns:
            Normalized heatmap array (values 0-1)
        """
        # Forward pass
        output = self.model(input_tensor)

        if class_idx is None:
            class_idx = output.argmax().item()

        # Backward pass
        target = output[0, class_idx]
        self.model.zero_grad()
        target.backward(retain_graph=True)

        # Compute weighted combination of activations
        gradients = self.gradients
        activations = self.activations

        weights = torch.mean(gradients, dim=(2, 3))[0]

        cam = torch.zeros(activations.shape[2], activations.shape[3])
        for i, w in enumerate(weights):
            cam += w * activations[0, i]

        # Apply ReLU and normalize
        cam = torch.relu(cam)
        cam = cam.detach().cpu().numpy()

        # Resize to input image size
        cam = cv2.resize(cam, (input_tensor.shape[3], input_tensor.shape[2]))
        cam = np.maximum(cam, 0)
        cam = cam / (cam.max() + 1e-8)

        return cam
