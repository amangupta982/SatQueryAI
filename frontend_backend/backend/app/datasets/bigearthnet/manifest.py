import json
import os
from typing import Dict, List
from .schemas import AnnotationRecord, ManifestRecord, SelectedAnnotation

def generate_manifest_and_annotations(
    sampled_pairs: Dict[str, List[AnnotationRecord]],
    output_dir: str
):
    """
    Generates manifest.jsonl and annotations.jsonl from the sampled pairs.
    """
    os.makedirs(output_dir, exist_ok=True)
    manifest_path = os.path.join(output_dir, "manifest.jsonl")
    annotations_path = os.path.join(output_dir, "annotations.jsonl")

    manifest_records = []
    annotation_records = []

    for pair_id, annotations in sampled_pairs.items():
        if not annotations:
            continue

        # Extract pair metadata from the first annotation
        # (These values should be consistent across all annotations for the pair)
        first_ann = annotations[0]
        
        # Expected paths if downloaded
        optical_path = f"images/optical/{first_ann.patch_id}.tif"
        sar_path = f"images/sar/{first_ann.s1_name}.tif"

        # unique tasks for this pair
        tasks = list(set([a.category for a in annotations]))

        manifest_record = ManifestRecord(
            pair_id=pair_id,
            sentinel1_id=first_ann.s1_name,
            sentinel2_id=first_ann.patch_id,
            optical_path=optical_path,
            sar_path=sar_path,
            latitude=first_ann.latitude,
            longitude=first_ann.longitude,
            country=first_ann.country,
            season=first_ann.season,
            climate_zone=first_ann.climate_zone,
            split=first_ann.split,
            annotation_count=len(annotations),
            tasks=tasks
        )
        manifest_records.append(manifest_record)

        for ann in annotations:
            sel_ann = SelectedAnnotation(
                pair_id=pair_id,
                input=ann.input,
                output=ann.output,
                type=ann.type,
                category=ann.category,
                split=ann.split,
                original_id=ann.id
            )
            annotation_records.append(sel_ann)

    # Write manifest
    with open(manifest_path, "w", encoding="utf-8") as f:
        for rec in manifest_records:
            f.write(rec.model_dump_json() + "\n")

    # Write annotations
    with open(annotations_path, "w", encoding="utf-8") as f:
        for rec in annotation_records:
            f.write(rec.model_dump_json() + "\n")

    return manifest_path, annotations_path
