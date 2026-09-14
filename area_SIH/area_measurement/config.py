"""
Configuration for the Area Measurement module.

Contains class taxonomy (derived from BigEarthNet.txt CLC-19 nomenclature),
color mappings, thresholds, and model parameters.
"""

# ── Minimum region area threshold (in pixels) ──
# Regions smaller than this are treated as noise and ignored.
MIN_REGION_AREA_PX = 500

# ── Model input size ──
# DeepLabV3 works best at this resolution; original resolution is preserved for output.
MODEL_INPUT_SIZE = (520, 520)

# ── Confidence threshold for segmentation ──
SEGMENTATION_CONFIDENCE_THRESHOLD = 0.3

# ── Land-Cover Class Taxonomy ──
# Simplified from CLC-19 (CORINE Land Cover) used in BigEarthNet v2.0.
# Each class maps to one or more CLC-19 categories.
#
# CLC-19 Classes in BigEarthNet v2.0:
#  1: Urban fabric
#  2: Industrial or commercial units
#  3: Arable land
#  4: Permanent crops
#  5: Pastures
#  6: Complex cultivation patterns
#  7: Land principally occupied by agriculture
#  8: Agro-forestry areas
#  9: Broad-leaved forest
# 10: Coniferous forest
# 11: Mixed forest
# 12: Natural grassland and sparsely vegetated areas
# 13: Moors, heathland and sclerophyllous vegetation
# 14: Transitional woodland/shrub
# 15: Beaches, dunes, sands
# 16: Inland wetlands
# 17: Coastal wetlands
# 18: Inland waters
# 19: Marine waters

LAND_COVER_CLASSES = {
    0: {
        "name": "Background",
        "clc_ids": [],
        "color_bgr": (50, 50, 50),       # Dark grey
        "color_rgb": (50, 50, 50),
        "display": False,
    },
    1: {
        "name": "Building / Urban",
        "clc_ids": [1],
        "color_bgr": (0, 200, 0),         # GREEN — required for project demo
        "color_rgb": (0, 200, 0),
        "display": True,
    },
    2: {
        "name": "Industrial",
        "clc_ids": [2],
        "color_bgr": (0, 200, 200),       # Cyan
        "color_rgb": (200, 200, 0),
        "display": True,
    },
    3: {
        "name": "Agriculture",
        "clc_ids": [3, 4, 5, 6, 7, 8],
        "color_bgr": (0, 255, 255),       # Yellow in BGR
        "color_rgb": (255, 255, 0),
        "display": True,
    },
    4: {
        "name": "Forest",
        "clc_ids": [9, 10, 11],
        "color_bgr": (0, 100, 0),         # Dark green
        "color_rgb": (0, 100, 0),
        "display": True,
    },
    5: {
        "name": "Vegetation",
        "clc_ids": [12, 13, 14],
        "color_bgr": (50, 205, 50),       # Lime green
        "color_rgb": (50, 205, 50),
        "display": True,
    },
    6: {
        "name": "Water",
        "clc_ids": [18, 19],
        "color_bgr": (255, 100, 30),      # Blue in BGR
        "color_rgb": (30, 100, 255),
        "display": True,
    },
    7: {
        "name": "Wetland",
        "clc_ids": [16, 17],
        "color_bgr": (180, 130, 70),      # Teal
        "color_rgb": (70, 130, 180),
        "display": True,
    },
    8: {
        "name": "Bare Land",
        "clc_ids": [15],
        "color_bgr": (42, 42, 165),       # Brown in BGR
        "color_rgb": (165, 42, 42),
        "display": True,
    },
    9: {
        "name": "Road",
        "clc_ids": [],
        "color_bgr": (0, 165, 255),       # Orange in BGR
        "color_rgb": (255, 165, 0),
        "display": True,
    },
}

NUM_CLASSES = len(LAND_COVER_CLASSES)

# ── VOC Class to Land-Cover Mapping ──
# PASCAL VOC 2012 has 21 classes (0=background, 1-20=objects).
# We map them to our land-cover taxonomy for inference on general images.
VOC_TO_LANDCOVER = {
    0: 0,   # background → Background
    1: 5,   # aeroplane → Vegetation (sky/field context)
    2: 5,   # bicycle → Vegetation (street context, minor)
    3: 5,   # bird → Vegetation
    4: 6,   # boat → Water
    5: 0,   # bottle → Background
    6: 9,   # bus → Road
    7: 9,   # car → Road
    8: 5,   # cat → Vegetation (indoor → ignore)
    9: 0,   # chair → Background
    10: 5,  # cow → Vegetation (pasture)
    11: 0,  # dining table → Background
    12: 5,  # dog → Vegetation
    13: 5,  # horse → Vegetation (pasture)
    14: 9,  # motorbike → Road
    15: 1,  # person → Building / Urban
    16: 5,  # potted plant → Vegetation
    17: 5,  # sheep → Vegetation (pasture)
    18: 0,  # sofa → Background
    19: 9,  # train → Road
    20: 0,  # tv/monitor → Background
}

# ── Mask overlay transparency ──
MASK_ALPHA = 0.40

# ── Bounding box line thickness ──
BBOX_THICKNESS = 2

# ── Label font scale ──
LABEL_FONT_SCALE = 0.5
LABEL_THICKNESS = 1

# ── Sentinel-2 band information ──
# 10m bands: B2 (Blue), B3 (Green), B4 (Red), B8 (NIR)
# 20m bands: B5, B6, B7, B8A, B11, B12
SENTINEL2_10M_BANDS = ["B02", "B03", "B04", "B08"]
SENTINEL2_20M_BANDS = ["B05", "B06", "B07", "B8A", "B11", "B12"]
SENTINEL2_SPATIAL_RESOLUTION_M = 10  # meters per pixel for 10m bands
