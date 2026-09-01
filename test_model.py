import sys
sys.path.insert(0, "backend")
from app import model

# Test fracture image
with open("dataset/val/fractured/3-rotated3-rotated3.jpg", "rb") as f:
    result = model.predict_image(f.read())
    print(f"Fracture image → {result['prediction']} (confidence: {result['confidence']:.4f})")

# Test no fracture image
with open("dataset/val/no_fractured/IMG0004341.jpg", "rb") as f:
    result = model.predict_image(f.read())
    print(f"No fracture image → {result['prediction']} (confidence: {result['confidence']:.4f})")

# Test a second fracture image
with open("dataset/val/fractured/41372_2006_Article_BF7211581_Fig1_HTML.jpg", "rb") as f:
    result = model.predict_image(f.read())
    print(f"Second fracture image → {result['prediction']} (confidence: {result['confidence']:.4f})")

# Test a second no fracture image
with open("dataset/val/no_fractured/IMG0004346.jpg", "rb") as f:
    result = model.predict_image(f.read())
    print(f"Second no fracture image → {result['prediction']} (confidence: {result['confidence']:.4f})")
