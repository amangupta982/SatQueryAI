"""
Tests for BigEarthNet.txt dataset parser, task classification, and sample validator.
"""

import os
import json
import pytest
from pathlib import Path

from vqa_captioning.preprocessing.bigearthnet_parser import BigEarthNetParser
from vqa_captioning.preprocessing.sample_validator import SampleValidator
from vqa_captioning.preprocessing.data_statistics import DatasetStatistics
from common.constants.lulc_taxonomy import BigEarthNetTask, SatQueryCategory

def test_parse_binary_presence_record():
    parser = BigEarthNetParser()
    raw = {
        "patch_id": "S2A_MSIL2A_20170613T101031_0_45",
        "question": "Is water present in the satellite image?",
        "answer": "Yes",
        "task": "presence",
        "metadata": {
            "country": "Austria",
            "season": "Summer",
            "classes": ["Water bodies", "Coniferous forest"]
        }
    }
    sample = parser.parse_raw_record(raw)

    assert sample.patch_id == "S2A_MSIL2A_20170613T101031_0_45"
    assert sample.question == "Is water present in the satellite image?"
    assert sample.answer == "Yes"
    assert sample.task == "presence"
    assert sample.metadata.country == "Austria"
    assert "Water bodies" in sample.metadata.lulc_classes

def test_task_classification_mapping():
    parser = BigEarthNetParser()
    assert parser.map_task_to_category("presence") == SatQueryCategory.PRESENCE.value
    assert parser.map_task_to_category("count") == SatQueryCategory.COUNT.value
    assert parser.map_task_to_category("size") == SatQueryCategory.AREA.value
    assert parser.map_task_to_category("adjacency") == SatQueryCategory.SPATIAL.value
    assert parser.map_task_to_category("referring_lulc_detection") == SatQueryCategory.GROUNDING.value
    assert parser.map_task_to_category("caption") == SatQueryCategory.CAPTIONING.value
    assert parser.map_task_to_category("country") == SatQueryCategory.METADATA.value

def test_conversational_instruction_format_parsing():
    parser = BigEarthNetParser()
    raw = {
        "id": "patch_100",
        "conversations": [
            {"from": "human", "value": "<image>\nWhich covers more area, forest or arable land?"},
            {"from": "gpt", "value": "Broad-leaved forest covers more area than arable land."}
        ],
        "task": "size"
    }
    sample = parser.parse_raw_record(raw)
    assert sample.question == "Which covers more area, forest or arable land?"
    assert "Broad-leaved forest" in sample.answer
    assert sample.task == "size"

def test_sample_validator_empty_text():
    validator = SampleValidator(check_image_exists=False)
    valid, reason = validator.validate_sample({"sample_id": "s1", "image_path": "x.png", "question": "", "answer": "Yes"})
    assert not valid
    assert "Empty or missing question" in reason

def test_sample_validator_duplicate_ids():
    validator = SampleValidator(check_image_exists=False)
    s = {"sample_id": "dup_1", "image_path": "x.png", "question": "q?", "answer": "a"}
    valid1, _ = validator.validate_sample(s)
    valid2, reason2 = validator.validate_sample(s)
    assert valid1 is True
    assert valid2 is False
    assert "Duplicate" in reason2

def test_dataset_statistics_computation():
    parser = BigEarthNetParser()
    samples = [
        parser.parse_raw_record({"patch_id": "p1", "question": "q1", "answer": "Yes", "task": "presence"}),
        parser.parse_raw_record({"patch_id": "p2", "question": "q2", "answer": "No", "task": "presence"}),
        parser.parse_raw_record({"patch_id": "p3", "question": "q3", "answer": "2", "task": "count"}),
    ]
    stats_calc = DatasetStatistics(samples)
    stats = stats_calc.compute()

    assert stats["total_annotations"] == 3
    assert stats["total_unique_patches"] == 3
    assert stats["task_distribution"]["presence"] == 2
    assert stats["task_distribution"]["count"] == 1
    assert stats["answer_type_distribution"]["binary_yes_no"] == 2
