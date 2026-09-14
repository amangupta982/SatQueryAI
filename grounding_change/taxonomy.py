"""
Taxonomy Registry for Remote-Sensing Change Intelligence.
Defines extensible semantic land-cover categories, universal change types,
and transition mapping.
"""

from enum import Enum
from typing import Dict, List, Optional, Set, Tuple
from pydantic import BaseModel, Field


class ChangeType(str, Enum):
    """Universal change types supported across all semantic categories."""
    UNCHANGED = "unchanged"
    ADDED = "added"
    REMOVED = "removed"
    EXPANDED = "expanded"
    REDUCED = "reduced"
    CONVERTED = "converted"
    FRAGMENTED = "fragmented"
    MERGED = "merged"
    RELOCATED = "relocated"


class SuperCategory(str, Enum):
    """Broad remote-sensing domain categories."""
    BUILT_ENVIRONMENT = "built_environment"
    VEGETATION = "vegetation"
    WATER = "water"
    GROUND_LAND = "ground_land"
    INFRASTRUCTURE = "infrastructure"
    BACKGROUND = "background"


class CategoryDefinition(BaseModel):
    """Metadata for a single semantic land-cover category."""
    id: int
    name: str
    display_name: str
    super_category: SuperCategory
    color_rgb: Tuple[int, int, int] = (128, 128, 128)
    color_hex: str = "#808080"
    aliases: List[str] = Field(default_factory=list)
    description: str = ""


class TaxonomyRegistry:
    """
    Extensible registry for remote-sensing semantic categories.
    Can register new classes at runtime without modifying model code.
    """
    def __init__(self):
        self._categories: Dict[int, CategoryDefinition] = {}
        self._name_to_id: Dict[str, int] = {}
        self._initialize_defaults()

    def _initialize_defaults(self):
        # 0: Background / No-data / Unclassified
        self.register(CategoryDefinition(
            id=0,
            name="background",
            display_name="Background / Unclassified",
            super_category=SuperCategory.BACKGROUND,
            color_rgb=(0, 0, 0),
            color_hex="#000000",
            aliases=["none", "unclassified", "no_data", "nodata"],
            description="Background, unclassified, or outside region of interest"
        ))

        # 1: Built Environment / Buildings
        self.register(CategoryDefinition(
            id=1,
            name="building",
            display_name="Buildings & Construction",
            super_category=SuperCategory.BUILT_ENVIRONMENT,
            color_rgb=(255, 77, 77),
            color_hex="#ff4d4d",
            aliases=["buildings", "structure", "structures", "house", "houses", "urban", "new construction", "developed land", "terminal", "terminals", "hangar", "hangars", "facility", "facilities", "industrial"],
            description="Residential, commercial, and industrial buildings"
        ))

        # 2: Vegetation (Trees / Forest)
        self.register(CategoryDefinition(
            id=2,
            name="vegetation",
            display_name="Vegetation & Forest",
            super_category=SuperCategory.VEGETATION,
            color_rgb=(46, 204, 113),
            color_hex="#2ecc71",
            aliases=["tree", "trees", "forest", "woodland", "greenery", "canopy", "regrowth", "dense trees"],
            description="Dense tree cover, woodland, and natural forest"
        ))

        # 3: Low Vegetation (Crops / Grass)
        self.register(CategoryDefinition(
            id=3,
            name="low_vegetation",
            display_name="Low Vegetation & Crops",
            super_category=SuperCategory.VEGETATION,
            color_rgb=(168, 230, 207),
            color_hex="#a8e6cf",
            aliases=["grass", "cropland", "crops", "pasture", "lawn", "shrub", "farmland", "airfield grass", "field", "fields", "meadow", "open ground"],
            description="Agricultural fields, crops, pastures, and low grasses"
        ))

        # 4: Water Bodies
        self.register(CategoryDefinition(
            id=4,
            name="water",
            display_name="Water Bodies",
            super_category=SuperCategory.WATER,
            color_rgb=(52, 152, 219),
            color_hex="#3498db",
            aliases=["river", "rivers", "lake", "lakes", "pond", "ponds", "reservoir", "flooding", "waterway"],
            description="Natural and artificial surface water bodies"
        ))

        # 5: Ground / Bare Land
        self.register(CategoryDefinition(
            id=5,
            name="bare_land",
            display_name="Bare Soil & Exposed Land",
            super_category=SuperCategory.GROUND_LAND,
            color_rgb=(211, 84, 0),
            color_hex="#d35400",
            aliases=["bare soil", "barren land", "exposed ground", "excavation", "land clearing", "dirt", "sand"],
            description="Unvegetated soil, exposed ground, sand, and excavation sites"
        ))

        # 6: Infrastructure / Roads & Paved Surfaces
        self.register(CategoryDefinition(
            id=6,
            name="infrastructure",
            display_name="Infrastructure & Roads",
            super_category=SuperCategory.INFRASTRUCTURE,
            color_rgb=(155, 89, 182),
            color_hex="#9b59b6",
            aliases=["road", "roads", "path", "paths", "parking", "parking areas", "pavement", "highway", "runway", "runways", "taxiway", "taxiways", "tarmac", "apron", "airport", "airfield", "airstrip", "playground"],
            description="Transportation infrastructure, roads, parking facilities, and paved grounds"
        ))

    def register(self, cat: CategoryDefinition):
        """Register or override a category in the taxonomy."""
        self._categories[cat.id] = cat
        self._name_to_id[cat.name.lower()] = cat.id
        for alias in cat.aliases:
            self._name_to_id[alias.lower()] = cat.id

    def get_by_id(self, cat_id: int) -> CategoryDefinition:
        """Lookup category by ID, falling back to background if not found."""
        return self._categories.get(cat_id, self._categories[0])

    def get_by_name(self, name: str) -> Optional[CategoryDefinition]:
        """Lookup category by exact name or alias."""
        clean = name.strip().lower()
        if clean in self._name_to_id:
            return self._categories[self._name_to_id[clean]]
        # Partial match
        for key, cat_id in self._name_to_id.items():
            if clean in key or key in clean:
                return self._categories[cat_id]
        return None

    def match_category(self, query: str) -> Optional[CategoryDefinition]:
        """Fuzzy/substring match category from user query text."""
        q = query.lower()
        for key, cat_id in self._name_to_id.items():
            if key in q:
                return self._categories[cat_id]
        return None

    @property
    def all_categories(self) -> List[CategoryDefinition]:
        """List of all registered categories sorted by ID."""
        return sorted(self._categories.values(), key=lambda c: c.id)

    @property
    def num_classes(self) -> int:
        return len(self._categories)

    def to_palette(self) -> Dict[str, str]:
        """Map category names to hex color codes for UI rendering."""
        return {cat.name: cat.color_hex for cat in self._categories.values() if cat.id > 0}


# Global singleton instance
taxonomy = TaxonomyRegistry()
