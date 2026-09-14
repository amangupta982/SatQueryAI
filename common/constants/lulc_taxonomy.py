"""
CORINE Land Cover (CLC) taxonomy and task constants for BigEarthNet and SatQuery AI.
"""

from enum import Enum
from typing import List, Dict

# 19 Generalized CORINE Land Cover classes used in BigEarthNet v2.0 / BigEarthNet.txt
BIGEARTHNET_19_CLASSES = [
    "Urban fabric",
    "Industrial or commercial units",
    "Arable land",
    "Permanent crops",
    "Pastures",
    "Complex cultivation patterns",
    "Land principally occupied by agriculture, with significant areas of natural vegetation",
    "Agro-forestry areas",
    "Broad-leaved forest",
    "Coniferous forest",
    "Mixed forest",
    "Natural grassland and sparsely vegetated areas",
    "Moors, heathland and sclerophyllous vegetation",
    "Transitional woodland, shrub",
    "Beaches, dunes, sands",
    "Inland wetlands",
    "Coastal wetlands",
    "Inland waters",
    "Marine waters",
]

# Original 43 CORINE Land Cover Level-3 classes
CORINE_43_CLASSES = [
    "Continuous urban fabric",
    "Discontinuous urban fabric",
    "Industrial or commercial units",
    "Road and rail networks and associated land",
    "Port areas",
    "Airports",
    "Mineral extraction sites",
    "Dump sites",
    "Construction sites",
    "Green urban areas",
    "Sport and leisure facilities",
    "Non-irrigated arable land",
    "Permanently irrigated land",
    "Rice fields",
    "Vineyards",
    "Fruit trees and berry plantations",
    "Olive groves",
    "Pastures",
    "Annual crops associated with permanent crops",
    "Complex cultivation patterns",
    "Land principally occupied by agriculture, with significant areas of natural vegetation",
    "Agro-forestry areas",
    "Broad-leaved forest",
    "Coniferous forest",
    "Mixed forest",
    "Natural grasslands",
    "Moors and heathland",
    "Sclerophyllous vegetation",
    "Transitional woodland-shrub",
    "Beaches, dunes, sands",
    "Bare rocks",
    "Sparsely vegetated areas",
    "Burnt areas",
    "Inland marshes",
    "Peat bogs",
    "Salt marshes",
    "Salines",
    "Intertidal flats",
    "Water courses",
    "Water bodies",
    "Coastal lagoons",
    "Estuaries",
    "Sea and ocean",
]

# Köppen-Geiger climate zones represented in BigEarthNet.txt
CLIMATE_ZONES = [
    "Af (Tropical rainforest)",
    "Am (Tropical monsoon)",
    "Aw (Tropical savannah)",
    "BSh (Hot semi-arid)",
    "BSk (Cold semi-arid)",
    "BWh (Hot desert)",
    "BWk (Cold desert)",
    "Cfa (Humid subtropical)",
    "Cfb (Oceanic)",
    "Cfc (Subpolar oceanic)",
    "Csa (Hot-summer Mediterranean)",
    "Csb (Warm-summer Mediterranean)",
    "Dfa (Hot-summer humid continental)",
    "Dfb (Warm-summer humid continental)",
    "Dfc (Subarctic)",
    "Dsc (Mediterranean-influenced subarctic)",
    "ET (Tundra)",
]

# Acquisition Seasons
SEASONS = ["Spring", "Summer", "Autumn", "Winter"]

# BigEarthNet 10 countries
COUNTRIES = [
    "Austria",
    "Belgium",
    "Finland",
    "Ireland",
    "Kosovo",
    "Lithuania",
    "Luxembourg",
    "Portugal",
    "Serbia",
    "Switzerland",
]

# Task classification mapping
class BigEarthNetTask(str, Enum):
    PRESENCE = "presence"
    COUNT = "count"
    SIZE = "size"
    ADJACENCY = "adjacency"
    RELATIVE_POSITION = "relative_position"
    COUNTRY = "country"
    SEASON = "season"
    CLIMATE_ZONE = "climate_zone"
    CAPTION = "caption"
    REFERRING_LULC_DETECTION = "referring_lulc_detection"
    REFERRING_POINT_DETECTION = "referring_point_detection"
    OTHER = "other"

class SatQueryCategory(str, Enum):
    SEMANTIC = "semantic"
    PRESENCE = "presence"
    COUNT = "count"
    AREA = "area"
    SPATIAL = "spatial"
    GROUNDING = "grounding"
    METADATA = "metadata"
    CAPTIONING = "captioning"
    OTHER = "other"

TASK_TO_SATQUERY_CATEGORY: Dict[BigEarthNetTask, SatQueryCategory] = {
    BigEarthNetTask.PRESENCE: SatQueryCategory.PRESENCE,
    BigEarthNetTask.COUNT: SatQueryCategory.COUNT,
    BigEarthNetTask.SIZE: SatQueryCategory.AREA,
    BigEarthNetTask.ADJACENCY: SatQueryCategory.SPATIAL,
    BigEarthNetTask.RELATIVE_POSITION: SatQueryCategory.SPATIAL,
    BigEarthNetTask.COUNTRY: SatQueryCategory.METADATA,
    BigEarthNetTask.SEASON: SatQueryCategory.METADATA,
    BigEarthNetTask.CLIMATE_ZONE: SatQueryCategory.METADATA,
    BigEarthNetTask.CAPTION: SatQueryCategory.CAPTIONING,
    BigEarthNetTask.REFERRING_LULC_DETECTION: SatQueryCategory.GROUNDING,
    BigEarthNetTask.REFERRING_POINT_DETECTION: SatQueryCategory.GROUNDING,
    BigEarthNetTask.OTHER: SatQueryCategory.OTHER,
}
