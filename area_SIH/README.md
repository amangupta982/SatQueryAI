# Area Measurement Module (Agentic RS)

This is the standalone **Area Measurement** module for the Agentic Remote Sensing project. It provides semantic segmentation and area calculation for satellite/remote-sensing imagery based on the methodology described in the [BigEarthNet.txt paper](https://arxiv.org/abs/2603.29630).

## 🚀 How to Run

1. **Install Dependencies:**
   Ensure you have Python installed, then run:
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the Web UI:**
   Run the Flask application:
   ```bash
   python app.py
   ```

3. **Use the App:**
   Open your browser and navigate to:
   [http://localhost:5000](http://localhost:5000)

## 🏗️ Architecture

This module is designed to be fully modular so it can be easily plugged into the main agentic pipeline later as "Tool 5".

```
area_measurement/
├── inference.py         # Main API: analyze_area()
├── preprocessing.py     # Image loading, GeoTIFF handling
├── segmentation.py      # DeepLabV3 & HSV color-space segmentation
├── area_calculation.py  # Area computation (pixel & physical)
├── visualization.py     # Bounding boxes, masks, and legends
├── utils.py             # Helpers & formatting
└── config.py            # CLC-aligned class taxonomy
```

## 🤖 Integration with Main Agent

To use this module programmatically in the main agentic pipeline:

```python
from area_measurement.inference import analyze_area

# Run analysis
# Set force_satellite_mode=True for better results on pure satellite imagery
result = analyze_area("path/to/image.tif", force_satellite_mode=True)

# Access results
print(result["summary_text"])
cv2.imwrite("output.png", result["annotated_image"])

# Access specific class data
for cls in result["classes"]:
    if cls["class_name"] == "Building / Urban":
        print(f"Urban Coverage: {cls['coverage_percent']}%")
```

## 📊 Features

- **Dual-Mode Segmentation:**
  - Standard RGB: Uses DeepLabV3-ResNet101 (auto-downloads weights).
  - Satellite Mode: Uses specialized HSV color-space analysis tuned for Earth Observation data.
- **Accurate Area Calculation:** Area is calculated strictly from the segmentation masks, NOT from bounding box dimensions.
- **Physical Area Support:** Automatically extracts spatial resolution from GeoTIFFs to calculate area in m², hectares, and km².
- **Premium UI:** Dark-mode, glassmorphism web interface with side-by-side comparison and data tables.
