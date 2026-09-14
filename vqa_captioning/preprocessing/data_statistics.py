"""
Dataset statistics analyzer for BigEarthNet.txt and SatQuery-VQA datasets.
Generates comprehensive breakdowns of tasks, splits, LULC classes, and sensors.
"""

from collections import Counter, defaultdict
from typing import List, Dict, Any, Optional
from common.schemas.vqa import UnifiedVQASample

class DatasetStatistics:
    """Computes and formats statistics across VQA samples."""

    def __init__(self, samples: Optional[List[UnifiedVQASample]] = None):
        self.samples = samples or []

    def compute(self) -> Dict[str, Any]:
        """Compute all statistical aggregations."""
        total_samples = len(self.samples)
        unique_patches = set()
        task_counts = Counter()
        category_counts = Counter()
        split_counts = Counter()
        sensor_counts = Counter()
        lulc_counts = Counter()
        answer_types = Counter()
        countries = Counter()
        seasons = Counter()

        for s in self.samples:
            unique_patches.add(s.patch_id)
            task_counts[s.task] += 1
            split_counts[s.metadata.split or "unspecified"] += 1
            sensor_counts[s.sensor] += 1

            if s.metadata.country:
                countries[s.metadata.country] += 1
            if s.metadata.season:
                seasons[s.metadata.season] += 1

            for lulc in s.metadata.lulc_classes:
                lulc_counts[lulc] += 1

            # Answer type detection
            ans_clean = s.answer.lower().strip()
            if ans_clean in ["yes", "no"]:
                answer_types["binary_yes_no"] += 1
            elif s.metadata.format_type == "mcq" or s.metadata.choices:
                answer_types["multiple_choice"] += 1
            elif s.evidence and s.evidence.bounding_boxes:
                answer_types["grounding_box"] += 1
            elif len(s.answer.split()) > 15:
                answer_types["descriptive_caption"] += 1
            else:
                answer_types["short_answer"] += 1

        return {
            "total_annotations": total_samples,
            "total_unique_patches": len(unique_patches),
            "split_distribution": dict(split_counts),
            "task_distribution": dict(task_counts),
            "answer_type_distribution": dict(answer_types),
            "sensor_distribution": dict(sensor_counts),
            "country_distribution": dict(countries.most_common(10)),
            "season_distribution": dict(seasons),
            "top_lulc_classes": dict(lulc_counts.most_common(15)),
        }

    def generate_report(self) -> str:
        """Render a readable GitHub-flavored markdown report."""
        stats = self.compute()
        lines = [
            "# SatQuery-VQA Dataset Statistics Report",
            "",
            f"- **Total Annotations (QA / Captions / Grounding)**: {stats['total_annotations']:,}",
            f"- **Total Unique Satellite Patches**: {stats['total_unique_patches']:,}",
            "",
            "## Split Breakdown",
            "| Split | Count | Percentage |",
            "|---|---|---|",
        ]

        total = max(stats["total_annotations"], 1)
        for split, count in stats["split_distribution"].items():
            lines.append(f"| {split} | {count:,} | {count / total * 100:.1f}% |")

        lines.extend([
            "",
            "## Task Breakdown",
            "| Task Type | Count | Percentage |",
            "|---|---|---|",
        ])
        for task, count in stats["task_distribution"].items():
            lines.append(f"| `{task}` | {count:,} | {count / total * 100:.1f}% |")

        lines.extend([
            "",
            "## Answer Type Distribution",
            "| Answer Type | Count | Percentage |",
            "|---|---|---|",
        ])
        for atype, count in stats["answer_type_distribution"].items():
            lines.append(f"| {atype} | {count:,} | {count / total * 100:.1f}% |")

        lines.extend([
            "",
            "## Sensor Modality Breakdown",
            "| Sensor | Count | Percentage |",
            "|---|---|---|",
        ])
        for sensor, count in stats["sensor_distribution"].items():
            lines.append(f"| {sensor} | {count:,} | {count / total * 100:.1f}% |")

        if stats["top_lulc_classes"]:
            lines.extend([
                "",
                "## Top CORINE Land Cover (CLC) Classes",
                "| Land Cover Class | Occurrences |",
                "|---|---|",
            ])
            for clc, count in stats["top_lulc_classes"].items():
                lines.append(f"| {clc} | {count:,} |")

        return "\n".join(lines)
