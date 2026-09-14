"""
Flask Web Application for the Area Measurement module.

Provides a premium dark-mode UI for uploading satellite/remote-sensing
images and viewing area analysis results with annotated visualizations.

Run: python app.py
Open: http://localhost:5000
"""

import os
import io
import base64
import json
import numpy as np
from PIL import Image
from flask import Flask, render_template, request, jsonify, send_file

from area_measurement.inference import analyze_area
from grounding.api import ground_objects

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50MB max upload

# Store results temporarily for download
_latest_result = {}

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "tif", "tiff", "bmp", "webp"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def numpy_to_base64(img_array: np.ndarray, format: str = "PNG") -> str:
    """Convert numpy RGB array to base64-encoded string for HTML embedding."""
    img = Image.fromarray(img_array.astype(np.uint8))
    buffer = io.BytesIO()
    img.save(buffer, format=format, quality=95)
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


@app.route("/")
def index():
    """Serve the main upload page."""
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    """
    Analyze an uploaded image for area measurement.
    
    Accepts multipart form data with an image file.
    Returns JSON with base64-encoded annotated image and area statistics.
    """
    global _latest_result

    if "image" not in request.files:
        return jsonify({"error": "No image file provided."}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "No file selected."}), 400

    if not allowed_file(file.filename):
        return jsonify({
            "error": f"Unsupported file format. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        }), 400

    # Check if satellite mode is requested
    force_satellite = request.form.get("satellite_mode", "false").lower() == "true"

    try:
        # Load image
        img_bytes = file.read()
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        original_array = np.array(img)

        # Run analysis
        result = analyze_area(img, force_satellite_mode=force_satellite)

        # Convert images to base64 for JSON response
        original_b64 = numpy_to_base64(original_array)
        annotated_b64 = numpy_to_base64(result["annotated_image"])
        summary_b64 = numpy_to_base64(result["summary_image"])

        # Store for download
        _latest_result = {
            "annotated_image": result["annotated_image"],
            "original_filename": file.filename,
        }

        # Prepare class data for JSON (remove numpy types)
        classes_json = []
        for cls in result["classes"]:
            cls_clean = {
                "class_id": int(cls["class_id"]),
                "class_name": cls["class_name"],
                "color_rgb": list(cls["color_rgb"]),
                "pixel_area": int(cls["pixel_area"]),
                "coverage_percent": float(cls["coverage_percent"]),
                "coverage_tier": cls["coverage_tier"],
                "num_instances": int(cls["num_instances"]),
                "area_m2": float(cls["area_m2"]) if cls["area_m2"] is not None else None,
                "area_hectares": float(cls["area_hectares"]) if cls["area_hectares"] is not None else None,
                "area_km2": float(cls["area_km2"]) if cls["area_km2"] is not None else None,
            }
            classes_json.append(cls_clean)

        response = {
            "success": True,
            "original_image": original_b64,
            "annotated_image": annotated_b64,
            "summary_image": summary_b64,
            "classes": classes_json,
            "total_pixels": int(result["total_pixels"]),
            "image_dimensions": result["image_dimensions"],
            "has_physical_area": bool(result["has_physical_area"]),
            "spatial_resolution_m": float(result["spatial_resolution_m"]) if result["spatial_resolution_m"] else None,
            "total_coverage_percent": float(result["total_coverage_percent"]),
            "physical_area_note": result["physical_area_note"],
            "summary_text": result["summary_text"],
            "processing_time_seconds": float(result["processing_time_seconds"]),
            "model_used": result["model_used"],
        }

        return jsonify(response)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500


@app.route("/ground", methods=["POST"])
def ground():
    """
    Object detection / grounding based on text query.
    """
    global _latest_result

    if "image" not in request.files:
        return jsonify({"error": "No image file provided."}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "No file selected."}), 400

    query = request.form.get("query", "").strip()
    if not query:
        return jsonify({"error": "No query provided."}), 400

    try:
        box_threshold = float(request.form.get("box_threshold", 0.3))
    except ValueError:
        box_threshold = 0.3

    if not allowed_file(file.filename):
        return jsonify({
            "error": f"Unsupported file format. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        }), 400

    try:
        img_bytes = file.read()
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        original_array = np.array(img)

        result = ground_objects(img, query, box_threshold=box_threshold)

        original_b64 = numpy_to_base64(original_array)
        annotated_b64 = numpy_to_base64(result["annotated_image"])

        _latest_result = {
            "annotated_image": result["annotated_image"],
            "original_filename": file.filename,
        }

        response = {
            "success": True,
            "query": result["query"],
            "target_label": result.get("target_label", ""),
            "count": result.get("count", 0),
            "detections": result["detections"],
            "original_image": original_b64,
            "annotated_image": annotated_b64,
            "processing_time": result["processing_time"],
            "pipeline_info": result.get("pipeline_info", {})
        }

        return jsonify(response)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Grounding failed: {str(e)}"}), 500


@app.route("/download")
def download():
    """Download the latest annotated image."""
    global _latest_result

    if "annotated_image" not in _latest_result:
        return jsonify({"error": "No analysis result available."}), 404

    img = Image.fromarray(_latest_result["annotated_image"].astype(np.uint8))
    buffer = io.BytesIO()
    img.save(buffer, format="PNG", quality=95)
    buffer.seek(0)

    orig_name = _latest_result.get("original_filename", "image")
    base_name = os.path.splitext(orig_name)[0]
    download_name = f"{base_name}_area_analysis.png"

    return send_file(
        buffer,
        mimetype="image/png",
        as_attachment=True,
        download_name=download_name,
    )


if __name__ == "__main__":
    print("=" * 60)
    print("  AREA MEASUREMENT MODULE")
    print("  Reference: BigEarthNet.txt (arXiv:2603.29630)")
    print("=" * 60)
    print()
    print("  Open in browser: http://localhost:5000")
    print()
    app.run(host="0.0.0.0", port=5000, debug=False)
