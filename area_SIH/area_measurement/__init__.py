"""
Area Measurement Module for Remote Sensing Images.

This module provides land-cover semantic segmentation and area calculation
for satellite/remote-sensing imagery. It is designed as a standalone component
that can be integrated into the larger Agentic Remote Sensing pipeline as
"Tool 5 — Area Measurement".

Reference Dataset: BigEarthNet.txt (arXiv:2603.29630)
- 464,044 co-registered Sentinel-1/Sentinel-2 image pairs
- Pixel-level LULC reference maps based on CORINE Land Cover (CLC) 2018
- Class taxonomy derived from CLC-19 nomenclature

Usage:
    from area_measurement.inference import analyze_area
    result = analyze_area("path/to/satellite_image.tif")
"""

from area_measurement.inference import analyze_area

__version__ = "1.0.0"
__all__ = ["analyze_area"]
