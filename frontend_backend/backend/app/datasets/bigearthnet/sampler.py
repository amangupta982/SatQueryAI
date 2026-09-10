import random
from typing import Dict, List
from .schemas import AnnotationRecord

def sample_image_pairs(
    grouped_pairs: Dict[str, List[AnnotationRecord]],
    max_pairs: int,
    seed: int
) -> Dict[str, List[AnnotationRecord]]:
    """
    Deterministically samples up to max_pairs unique image pairs.
    Returns a new dictionary with the selected pairs and their annotations.
    """
    pair_ids = list(grouped_pairs.keys())
    
    # Sort for deterministic sampling before random seed is applied, 
    # to ensure consistency across different runs.
    pair_ids.sort()
    
    random.seed(seed)
    
    if len(pair_ids) > max_pairs:
        selected_pair_ids = random.sample(pair_ids, max_pairs)
    else:
        selected_pair_ids = pair_ids
        
    return {pair_id: grouped_pairs[pair_id] for pair_id in selected_pair_ids}
