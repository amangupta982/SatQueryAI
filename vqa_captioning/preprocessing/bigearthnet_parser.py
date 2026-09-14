"""
BigEarthNet.txt dataset parser.
Extracts annotations for Binary VQA, MCQ VQA, Captions, and Referring Expressions,
normalizing them into the SatQuery-VQA unified schema.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Generator

from common.schemas.vqa import UnifiedVQASample, UnifiedSampleMetadata, EvidenceData
from common.constants.lulc_taxonomy import (
    BigEarthNetTask,
    SatQueryCategory,
    TASK_TO_SATQUERY_CATEGORY,
    BIGEARTHNET_19_CLASSES,
)

logger = logging.getLogger(__name__)

class BigEarthNetParser:
    """
    Parses BigEarthNet.txt annotations into the standard SatQuery AI representation.
    """

    def __init__(self, dataset_dir: Optional[str] = None):
        self.dataset_dir = Path(dataset_dir) if dataset_dir else None

    def map_task_to_category(self, task_name: str) -> str:
        """Map granular task to high-level SatQuery category."""
        clean_task = str(task_name).lower().strip()
        try:
            task_enum = BigEarthNetTask(clean_task)
            return TASK_TO_SATQUERY_CATEGORY.get(task_enum, SatQueryCategory.OTHER).value
        except ValueError:
            # Fallback heuristic mapping if task name has variation
            if "presen" in clean_task:
                return SatQueryCategory.PRESENCE.value
            elif "count" in clean_task or "number" in clean_task:
                return SatQueryCategory.COUNT.value
            elif "size" in clean_task or "area" in clean_task or "cover" in clean_task:
                return SatQueryCategory.AREA.value
            elif "adjacen" in clean_task or "relat" in clean_task or "spatial" in clean_task:
                return SatQueryCategory.SPATIAL.value
            elif "ground" in clean_task or "refer" in clean_task or "bbox" in clean_task or "point" in clean_task:
                return SatQueryCategory.GROUNDING.value
            elif "caption" in clean_task:
                return SatQueryCategory.CAPTIONING.value
            elif any(m in clean_task for m in ["country", "season", "climate"]):
                return SatQueryCategory.METADATA.value
            return SatQueryCategory.OTHER.value

    def parse_raw_record(self, record: Dict[str, Any], default_split: str = "train") -> UnifiedVQASample:
        """
        Parse a single dictionary record into a UnifiedVQASample.
        Supports standard BigEarthNet.txt JSON structure as well as VLM conversation schemas.
        """
        # 1. Identify Patch and Sample IDs
        patch_id = record.get("patch_id") or record.get("image_id") or record.get("id") or "unknown_patch"
        sample_id = record.get("sample_id") or f"{patch_id}_{record.get('task', 'vqa')}_{record.get('index', 0)}"

        # 2. Extract Question and Answer
        question = ""
        answer = ""
        if "conversations" in record:
            # Standard instruction-tuning format (e.g. LLaVA / InternVL style)
            convs = record["conversations"]
            for i in range(len(convs) - 1):
                if convs[i].get("from") in ["human", "user"] and convs[i + 1].get("from") in ["gpt", "assistant"]:
                    question = convs[i].get("value", "")
                    answer = convs[i + 1].get("value", "")
                    break
        else:
            question = (
                record.get("input")
                or record.get("question")
                or record.get("query")
                or record.get("instruction")
                or ""
            )
            answer = (
                record.get("output")
                or record.get("answer")
                or record.get("response")
                or record.get("caption")
                or ""
            )

        # Clean text
        question = str(question).replace("<image>", "").replace("<image>\n", "").strip()
        answer = str(answer).strip()

        # 3. Task extraction (supports BigEarthNet.txt 'category' and 'type' columns)
        raw_task = record.get("category") or record.get("type") or record.get("task")
        if not raw_task:
            # Infer from task_type or question
            q_lower = question.lower()
            if "is " in q_lower or "are " in q_lower or "present" in q_lower:
                raw_task = "presence"
            elif "how many" in q_lower:
                raw_task = "count"
            elif "area" in q_lower or "cover" in q_lower or "size" in q_lower:
                raw_task = "size"
            elif "next to" in q_lower or "adjacent" in q_lower or "near" in q_lower:
                raw_task = "adjacency"
            elif "locate" in q_lower or "where is" in q_lower or "box" in q_lower:
                raw_task = "referring_lulc_detection"
            elif "describe" in q_lower or len(answer) > 100:
                raw_task = "caption"
            else:
                raw_task = "other"

        # 4. Resolve Image and SAR paths
        image_path = record.get("image_path") or record.get("image") or ""
        sar_path = record.get("sar_path") or record.get("sar_image") or None

        if self.dataset_dir and not os.path.isabs(image_path):
            potential_s2 = self.dataset_dir / "images" / f"{patch_id}.png"
            if potential_s2.exists():
                image_path = str(potential_s2)
            elif (self.dataset_dir / image_path).exists():
                image_path = str(self.dataset_dir / image_path)

        # 5. Extract Evidence (bounding boxes, coverage info)
        evidence = EvidenceData()
        if "bbox" in record:
            bbox = record["bbox"]
            if isinstance(bbox, list):
                if len(bbox) == 4 and isinstance(bbox[0], (int, float)):
                    evidence.bounding_boxes = [bbox]
                elif all(isinstance(b, list) and len(b) == 4 for b in bbox):
                    evidence.bounding_boxes = bbox

        if "coverage_tier" in record:
            evidence.coverage_tier = record["coverage_tier"]
        elif "coverage" in record:
            evidence.coverage_tier = str(record["coverage"])

        if "area_m2" in record:
            try:
                evidence.approx_area_m2 = float(record["area_m2"])
            except (ValueError, TypeError):
                pass

        # 6. Extract Metadata
        meta_dict = record.get("metadata", {})
        split = record.get("split") or meta_dict.get("split") or default_split
        lulc_classes = record.get("lulc_classes") or meta_dict.get("classes") or []
        country = record.get("country") or meta_dict.get("country")
        season = record.get("season") or meta_dict.get("season")
        climate_zone = record.get("climate_zone") or meta_dict.get("climate_zone")
        format_type = record.get("format") or record.get("type") or ("mcq" if "choices" in record else "binary")
        choices = record.get("choices")

        metadata = UnifiedSampleMetadata(
            country=country,
            season=season,
            climate_zone=climate_zone,
            lulc_classes=lulc_classes,
            split=split,
            source="BigEarthNet.txt",
            format_type=format_type,
            choices=choices,
        )

        sensor = record.get("sensor") or ("Sentinel-1+2" if sar_path else "Sentinel-2")

        return UnifiedVQASample(
            sample_id=str(sample_id),
            patch_id=str(patch_id),
            image_path=str(image_path),
            sar_path=str(sar_path) if sar_path else None,
            question=question,
            answer=answer,
            task=str(raw_task),
            sensor=sensor,
            metadata=metadata,
            evidence=evidence,
        )

    def parse_file(self, file_path: Union[str, Path], split: str = "train") -> List[UnifiedVQASample]:
        """
        Parse a JSON or JSONL file into a list of UnifiedVQASamples.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Annotation file not found: {path}")

        samples: List[UnifiedVQASample] = []
        if path.suffix in [".jsonl", ".txt"]:
            with open(path, "r", encoding="utf-8") as f:
                for idx, line in enumerate(f):
                    line = line.strip()
                    if not line:
                        continue
                    record = json.loads(line)
                    record["index"] = idx
                    samples.append(self.parse_raw_record(record, default_split=split))
        elif path.suffix == ".json":
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    for idx, record in enumerate(data):
                        record["index"] = idx
                        samples.append(self.parse_raw_record(record, default_split=split))
                elif isinstance(data, dict):
                    # Could be dictionary mapping patch_id -> list of QA pairs
                    for patch_id, records in data.items():
                        if isinstance(records, list):
                            for idx, record in enumerate(records):
                                if isinstance(record, dict):
                                    record.setdefault("patch_id", patch_id)
                                    record["index"] = idx
                                    samples.append(self.parse_raw_record(record, default_split=split))
                        elif isinstance(records, dict):
                            records.setdefault("patch_id", patch_id)
                            samples.append(self.parse_raw_record(records, default_split=split))
        elif path.suffix == ".parquet":
            try:
                import pandas as pd
                df = pd.read_parquet(path)
                for idx, row in df.iterrows():
                    rec = row.to_dict()
                    rec["index"] = idx
                    samples.append(self.parse_raw_record(rec, default_split=split))
            except Exception as e:
                logger.error(f"Error reading parquet file {path}: {e}")
                raise

        return samples
