import pytest
from app.datasets.bigearthnet.schemas import AnnotationRecord
from app.datasets.bigearthnet.filtering import filter_annotations
from app.datasets.bigearthnet.grouping import group_annotations_by_pair
from app.datasets.bigearthnet.sampler import sample_image_pairs

@pytest.fixture
def mock_records():
    return [
        {
            "ID": 1, "s1_name": "S1_A", "patch_id": "S2_A", "input": "Q1", "output": "A1",
            "type": "binary", "category": "vqa", "split": "train",
            "latitude": 0.0, "longitude": 0.0, "country": "US", "season": "Summer", "climate_zone": "A"
        },
        {
            "ID": 2, "s1_name": "S1_A", "patch_id": "S2_A", "input": "Q2", "output": "A2",
            "type": "binary", "category": "vqa", "split": "train",
            "latitude": 0.0, "longitude": 0.0, "country": "US", "season": "Summer", "climate_zone": "A"
        },
        {
            "ID": 3, "s1_name": "S1_B", "patch_id": "S2_B", "input": "Q3", "output": "A3",
            "type": "binary", "category": "grounding", "split": "validation",
            "latitude": 0.0, "longitude": 0.0, "country": "US", "season": "Summer", "climate_zone": "A"
        },
        {
            "ID": 4, "s1_name": "S1_C", "patch_id": "S2_C", "input": "Q4", "output": "A4",
            "type": "binary", "category": "vqa", "split": "test",
            "latitude": 0.0, "longitude": 0.0, "country": "US", "season": "Summer", "climate_zone": "A"
        }
    ]

def test_filtering(mock_records):
    filtered = list(filter_annotations(mock_records, target_split="train"))
    assert len(filtered) == 2
    assert all(r.split == "train" for r in filtered)

    filtered_task = list(filter_annotations(mock_records, target_task="grounding"))
    assert len(filtered_task) == 1
    assert filtered_task[0].category == "grounding"

def test_grouping(mock_records):
    records = list(filter_annotations(mock_records))
    grouped = group_annotations_by_pair(records)
    
    assert len(grouped) == 3
    assert "S1_A_S2_A" in grouped
    assert len(grouped["S1_A_S2_A"]) == 2

def test_sampling(mock_records):
    records = list(filter_annotations(mock_records))
    grouped = group_annotations_by_pair(records)
    
    # Sample 2 pairs from 3 available
    sampled = sample_image_pairs(grouped, max_pairs=2, seed=42)
    assert len(sampled) == 2
    
    # Should be deterministic
    sampled2 = sample_image_pairs(grouped, max_pairs=2, seed=42)
    assert set(sampled.keys()) == set(sampled2.keys())
    
    # Sample more than available
    sampled3 = sample_image_pairs(grouped, max_pairs=10, seed=42)
    assert len(sampled3) == 3
