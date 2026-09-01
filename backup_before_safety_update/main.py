# """
# Fracture Detection - FastAPI Backend
# =====================================
# Loads the trained model (best_model.pth) via model.py,
# accepts X-ray image uploads via /predict,
# and returns prediction + confidence + Grad-CAM heatmap.

# Usage:
#     cd backend
#     uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# """

# from fastapi import FastAPI, UploadFile, File, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from . import model
# from .gradcam import GradCAM
# import torch
# import numpy as np
# import io
# import base64
# from PIL import Image
# import cv2

# app = FastAPI(title="Fracture Detection API")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # ─── Global Variables ────────────────────────────────────────────────────────

# gradcam_instance = None
# model_loaded = False


# # ─── Startup ─────────────────────────────────────────────────────────────────

# @app.on_event("startup")
# async def load_model_on_startup():
#     """Initialize Grad-CAM after model.py loads the model on import."""
#     global gradcam_instance, model_loaded

#     try:
#         # model.py already loaded best_model.pth on import
#         # model.model is the ResNet50 backbone, model.model.layer4 is the target
#         gradcam_instance = GradCAM(model.model, model.model.layer4)
#         model_loaded = True

#         print("=" * 50)
#         print("  FRACTURE DETECTION API STARTUP")
#         print("=" * 50)
#         print(f"  Model loaded: {model_loaded}")
#         print(f"  Device: {model.DEVICE}")
#         print(f"  Classes: {model.CLASS_NAMES}")
#         print(f"  Grad-CAM initialized: True")
#         print("=" * 50)

#     except Exception as e:
#         print(f"  WARNING: Grad-CAM init failed: {str(e)}")
#         model_loaded = True  # Model still works, just no Grad-CAM


# # ─── API Endpoints ───────────────────────────────────────────────────────────

# @app.get("/")
# def read_root():
#     """Health check endpoint."""
#     return {
#         "message": "Fracture Detection API is running",
#         "model_loaded": model_loaded,
#         "version": "1.0.0",
#     }


# @app.post("/predict")
# async def predict_fracture(
#     file: UploadFile = File(...),
#     include_heatmap: bool = True,
# ):
#     """
#     Predict whether an X-ray image shows a fracture.

#     Upload an image file and receive:
#     - prediction: 'Fracture Detected' or 'No Fracture'
#     - confidence: probability score (0.0 - 1.0)
#     - heatmap: base64-encoded Grad-CAM overlay image

#     Frontend usage example:
#         const formData = new FormData();
#         formData.append('file', imageFile);
#         formData.append('include_heatmap', 'true');
#         const response = await fetch('http://localhost:8000/predict', {
#             method: 'POST',
#             body: formData,
#         });
#         const data = await response.json();
#         // data.prediction = "Fracture Detected"
#         // data.confidence = 0.9975
#         // data.heatmap_data_url = "data:image/png;base64,..."
#     """
#     if not model_loaded:
#         raise HTTPException(
#             status_code=503,
#             detail="Model not loaded. Please check server logs."
#         )

#     # Validate file type
#     allowed_types = [
#         "image/jpeg", "image/jpg", "image/png",
#         "image/bmp", "image/tiff"
#     ]
#     if file.content_type not in allowed_types:
#         raise HTTPException(
#             status_code=400,
#             detail=f"Invalid file type. Allowed: {', '.join(allowed_types)}"
#         )

#     try:
#         contents = await file.read()

#         # 1. Get Prediction (uses model.predict_image from model.py)
#         result = model.predict_image(contents)

#         # 2. Build base response
#         response = {
#             "prediction": result["prediction"],
#             "confidence": round(result["confidence"], 4),
#             "confidence_percentage": round(result["confidence"] * 100, 2),
#             "class_name": result.get("class_name", ""),
#             "probabilities": result.get("probabilities", {}),
#             "model_version": "1.0.0",
#         }

#         # 3. Generate Grad-CAM Heatmap (if requested)
#         if include_heatmap:
#             try:
#                 image = Image.open(io.BytesIO(contents)).convert("RGB")
#                 image_tensor = model.transform(image).unsqueeze(0).to(model.DEVICE)

#                 mask = gradcam_instance.generate(image_tensor)

#                 # Apply heatmap using OpenCV
#                 heatmap = cv2.applyColorMap(
#                     np.uint8(255 * mask), cv2.COLORMAP_JET
#                 )
#                 heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)

#                 original_img = np.array(image.resize((224, 224)))
#                 overlayed = cv2.addWeighted(
#                     original_img, 0.6, heatmap, 0.4, 0
#                 )

#                 # Encode as base64 PNG for frontend
#                 _, buffer = cv2.imencode(".png", overlayed)
#                 heatmap_b64 = base64.b64encode(buffer).decode("utf-8")

#                 response["heatmap"] = heatmap_b64
#                 response["heatmap_format"] = "base64_png"
#                 response["heatmap_data_url"] = f"data:image/png;base64,{heatmap_b64}"

#             except Exception as heatmap_err:
#                 print(f"  Grad-CAM warning: {str(heatmap_err)}")
#                 response["heatmap_error"] = str(heatmap_err)

#         return response

#     except HTTPException:
#         raise
#     except Exception as e:
#         print(f"  ERROR in /predict: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))


# @app.get("/classes")
# async def get_classes():
#     """Return the model's class labels."""
#     return {
#         "classes": model.CLASS_NAMES,
#         "labels": model.LABELS,
#         "num_classes": len(model.CLASS_NAMES),
#     }


# @app.get("/health")
# async def health_check():
#     """Detailed health check."""
#     return {
#         "status": "healthy" if model_loaded else "degraded",
#         "model_loaded": model_loaded,
#         "device": str(model.DEVICE),
#         "version": "1.0.0",
#     }


# """
# Fracture Detection - FastAPI Backend
# =====================================
# Loads the trained model (best_model.pth) via model.py,
# accepts X-ray image uploads via /predict,
# and returns prediction + confidence + Grad-CAM heatmap.

# Usage:
#     cd backend
#     uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# """

# from fastapi import FastAPI, UploadFile, File, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from . import model
# from .gradcam import GradCAM
# import numpy as np
# import io
# import base64
# from PIL import Image
# import cv2

# app = FastAPI(title="Fracture Detection API")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # ───────────────────────────────────────────────────────────────
# # Global Variables
# # ───────────────────────────────────────────────────────────────

# gradcam_instance = None
# model_loaded = False


# # ───────────────────────────────────────────────────────────────
# # Startup
# # ───────────────────────────────────────────────────────────────

# @app.on_event("startup")
# async def load_model_on_startup():
#     """Initialize Grad-CAM after model.py loads the model."""

#     global gradcam_instance, model_loaded

#     try:
#         gradcam_instance = GradCAM(model.model, model.model.layer4)
#         model_loaded = True

#         print("=" * 50)
#         print(" FRACTURE DETECTION API STARTUP")
#         print("=" * 50)
#         print(f"Model loaded: {model_loaded}")
#         print(f"Device: {model.DEVICE}")
#         print(f"Classes: {model.CLASS_NAMES}")
#         print("Grad-CAM initialized: True")
#         print("=" * 50)

#     except Exception as e:
#         print(f"WARNING: Grad-CAM init failed: {e}")
#         model_loaded = True


# # ───────────────────────────────────────────────────────────────
# # Routes
# # ───────────────────────────────────────────────────────────────

# @app.get("/")
# def read_root():
#     return {
#         "message": "Fracture Detection API is running",
#         "model_loaded": model_loaded,
#         "version": "1.0.0",
#     }


# @app.post("/predict")
# async def predict_fracture(
#     file: UploadFile = File(...),
#     include_heatmap: bool = True,
# ):
#     """
#     Predict fracture from uploaded X-ray image.
#     """

#     if not model_loaded:
#         raise HTTPException(
#             status_code=503,
#             detail="Model not loaded. Please check server logs."
#         )

#     allowed_types = [
#         "image/jpeg",
#         "image/jpg",
#         "image/png",
#         "image/bmp",
#         "image/tiff",
#     ]

#     if file.content_type not in allowed_types:
#         raise HTTPException(
#             status_code=400,
#             detail=f"Invalid file type. Allowed: {', '.join(allowed_types)}"
#         )

#     try:

#         contents = await file.read()

#         # -------------------------------------------------------
#         # Reset model state before every prediction
#         # -------------------------------------------------------

#         model.model.eval()
#         model.model.zero_grad()

#         # -------------------------------------------------------
#         # Prediction
#         # -------------------------------------------------------

#         result = model.predict_image(contents)

#         response = {
#             "prediction": result["prediction"],
#             "confidence": round(result["confidence"], 4),
#             "confidence_percentage": round(result["confidence"] * 100, 2),
#             "class_name": result.get("class_name", ""),
#             "probabilities": result.get("probabilities", {}),
#             "model_version": "1.0.0",
#         }

#         # -------------------------------------------------------
#         # Grad-CAM
#         # -------------------------------------------------------

#         if include_heatmap:

#             try:

#                 image = Image.open(io.BytesIO(contents)).convert("RGB")

#                 image_tensor = (
#                     model.transform(image)
#                     .unsqueeze(0)
#                     .to(model.DEVICE)
#                 )

#                 mask = gradcam_instance.generate(image_tensor)

#                 heatmap = cv2.applyColorMap(
#                     np.uint8(mask * 255),
#                     cv2.COLORMAP_JET,
#                 )

#                 heatmap = cv2.cvtColor(
#                     heatmap,
#                     cv2.COLOR_BGR2RGB,
#                 )

#                 original = np.array(image.resize((224, 224)))

#                 overlay = cv2.addWeighted(
#                     original,
#                     0.6,
#                     heatmap,
#                     0.4,
#                     0,
#                 )

#                 _, buffer = cv2.imencode(".png", overlay)

#                 heatmap_b64 = base64.b64encode(buffer).decode("utf-8")

#                 response["heatmap"] = heatmap_b64
#                 response["heatmap_format"] = "base64_png"
#                 response["heatmap_data_url"] = (
#                     f"data:image/png;base64,{heatmap_b64}"
#                 )

#             except Exception as heatmap_err:

#                 print(f"Grad-CAM warning: {heatmap_err}")

#                 response["heatmap_error"] = str(heatmap_err)

#         return response

#     except HTTPException:
#         raise

#     except Exception as e:

#         print(f"ERROR in /predict: {e}")

#         raise HTTPException(
#             status_code=500,
#             detail=str(e),
#         )


# @app.get("/classes")
# async def get_classes():
#     return {
#         "classes": model.CLASS_NAMES,
#         "labels": model.LABELS,
#         "num_classes": len(model.CLASS_NAMES),
#     }


# @app.get("/health")
# async def health_check():
#     return {
#         "status": "healthy" if model_loaded else "degraded",
#         "model_loaded": model_loaded,
#         "device": str(model.DEVICE),
#         "version": "1.0.0",
#     }

import base64
import io

import cv2
import numpy as np
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image

from . import model
from .gradcam import GradCAM


app = FastAPI(title="Fracture Detection API", version="1.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ALLOWED_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/bmp",
    "image/tiff",
}

RESEARCH_WARNING = (
    "Research prototype only. This result is not a medical diagnosis. "
    "A qualified radiologist or doctor must review the X-ray."
)

gradcam_instance = None


@app.on_event("startup")
async def initialize_gradcam():
    global gradcam_instance
    try:
        gradcam_instance = GradCAM(model.model, model.model.layer4)
        print("Grad-CAM initialized successfully")
    except Exception as exc:
        gradcam_instance = None
        print(f"Grad-CAM unavailable: {exc}")


@app.get("/")
def read_root():
    return {
        "message": "Fracture Detection API is running",
        "model_loaded": True,
        "research_warning": RESEARCH_WARNING,
        "version": "1.1.0",
    }


@app.post("/predict")
async def predict_fracture(
    file: UploadFile = File(...),
    include_heatmap: bool = True,
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Please upload a JPG, PNG, BMP, or TIFF image.",
        )

    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")

    try:
        # Validate that the uploaded bytes are a readable image.
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        result = model.predict_image(contents)

        response = {
            **result,
            "confidence_percentage": round(result["confidence"] * 100, 2),
            "research_warning": RESEARCH_WARNING,
            "model_version": "1.1.0",
        }

        if result["review_required"]:
            response["display_prediction"] = "Uncertain—professional review required"
            response["review_message"] = (
                "The model confidence is below the review threshold. Do not rely on "
                "this result; obtain professional interpretation."
            )
        else:
            response["display_prediction"] = result["prediction"]
            response["review_message"] = (
                "Professional review is still required, even when confidence is high."
            )

        if include_heatmap and gradcam_instance is not None:
            try:
                image_tensor = model.transform(image).unsqueeze(0).to(model.DEVICE)
                mask = gradcam_instance.generate(
                    image_tensor,
                    class_idx=result["class_index"],
                )

                heatmap = cv2.applyColorMap(
                    np.uint8(np.clip(mask, 0, 1) * 255),
                    cv2.COLORMAP_JET,
                )
                heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
                original = np.array(image.resize((224, 224)))
                overlay = cv2.addWeighted(original, 0.6, heatmap, 0.4, 0)
                success, buffer = cv2.imencode(".png", overlay)
                if success:
                    encoded = base64.b64encode(buffer).decode("utf-8")
                    response["heatmap_data_url"] = f"data:image/png;base64,{encoded}"
            except Exception as exc:
                response["heatmap_error"] = str(exc)

        return response

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Image processing failed: {exc}")


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "model_loaded": True,
        "device": str(model.DEVICE),
        "classes": model.CLASS_NAMES,
        "version": "1.1.0",
    }
