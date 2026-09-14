from typing import Iterator, Optional, Dict, Any
from .schemas import AnnotationRecord

def filter_annotations(
    records: Iterator[Dict[str, Any]],
    target_split: Optional[str] = None,
    target_task: Optional[str] = None,
) -> Iterator[AnnotationRecord]:
    """
    Filter raw dictionary records and yield validated AnnotationRecord objects.
    """
    for row in records:
        try:
            record = AnnotationRecord(**row)
        except Exception:
            # Skip invalid records
            continue

        if target_split and record.split != target_split:
            continue
        
        # 'category' in the dataset often maps to the task (e.g., 'vqa', 'grounding', 'adjacency')
        if target_task and record.category != target_task:
            continue

        yield record
