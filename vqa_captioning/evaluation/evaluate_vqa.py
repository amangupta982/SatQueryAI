"""
Benchmark evaluation runner for SatQuery-VQA.
Evaluates base pretrained VLM vs. fine-tuned SatQuery-VQA on BigEarthNet.txt benchmark splits.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from tqdm import tqdm

from vqa_captioning.models.satquery_vqa_model import SatQueryVQA
from vqa_captioning.preprocessing.bigearthnet_parser import BigEarthNetParser
from vqa_captioning.evaluation.metrics import VQAMetricsCalculator
from common.schemas.vqa import UnifiedVQASample

logger = logging.getLogger(__name__)

class VQAEvaluator:
    """Evaluates SatQuery-VQA on benchmark datasets."""

    def __init__(
        self,
        model_name_or_path: str = "Qwen/Qwen2.5-VL-3B-Instruct",
        adapter_path: Optional[str] = None,
    ):
        self.vqa_model = SatQueryVQA(
            model_name_or_path=model_name_or_path,
            adapter_path=adapter_path,
        )
        self.metrics_calculator = VQAMetricsCalculator()
        self.parser = BigEarthNetParser()

    def evaluate_split(
        self,
        split_path: Union[str, Path],
        max_samples: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Evaluate model on a dataset file.
        """
        path = Path(split_path)
        if not path.exists():
            raise FileNotFoundError(f"Evaluation file not found: {path}")

        samples: List[UnifiedVQASample] = self.parser.parse_file(path)
        if max_samples and max_samples < len(samples):
            samples = samples[:max_samples]

        logger.info(f"Evaluating {len(samples)} samples from: {path.name}")
        records = []

        for sample in tqdm(samples, desc="Evaluating"):
            # Inference
            pred_out = self.vqa_model.predict(
                image=sample.image_path if sample.image_path and Path(sample.image_path).exists() else None,
                question=sample.question,
                task=sample.task,
                sensor=sample.sensor,
                choices=sample.metadata.choices,
            )

            record = {
                "sample_id": sample.sample_id,
                "patch_id": sample.patch_id,
                "question": sample.question,
                "ground_truth": sample.answer,
                "prediction": pred_out.get("answer", ""),
                "task": sample.task,
                "category": self.parser.map_task_to_category(sample.task),
                "confidence": pred_out.get("confidence"),
                "pred_boxes": pred_out.get("evidence", {}).get("bounding_boxes", []),
                "gt_boxes": sample.evidence.bounding_boxes if sample.evidence else [],
            }
            records.append(record)

        # Compute metrics
        eval_results = self.metrics_calculator.evaluate_predictions(records)
        eval_results["dataset_file"] = str(path.name)
        eval_results["model_name"] = "SatQuery-VQA" if self.vqa_model.adapter_path else "Base Pretrained VLM"

        return eval_results

    def generate_markdown_report(self, results: Dict[str, Any]) -> str:
        """Render evaluation results into markdown."""
        lines = [
            f"# SatQuery-VQA Benchmark Evaluation Report",
            f"- **Model**: {results.get('model_name', 'SatQuery-VQA')}",
            f"- **Dataset File**: `{results.get('dataset_file', 'benchmark.json')}`",
            f"- **Total Evaluated Samples**: {results.get('total_evaluated', 0):,}",
            f"- **Overall Exact Match / Accuracy**: **{results.get('overall_accuracy', 0.0):.2f}%**",
            "",
        ]

        if "count_mae" in results:
            lines.append(f"- **Counting MAE**: {results['count_mae']} (RMSE: {results.get('count_rmse', 'N/A')})")
        if "mean_iou" in results:
            lines.append(f"- **Grounding Mean IoU**: {results['mean_iou']:.4f}")

        lines.extend([
            "",
            "## Per-Task Accuracy Breakdown",
            "| Task Type | Samples | Accuracy |",
            "|---|---|---|",
        ])
        for task, data in results.get("per_task_metrics", {}).items():
            lines.append(f"| `{task}` | {data['total']} | {data['accuracy']:.1f}% |")

        lines.extend([
            "",
            "## SatQuery Category Breakdown",
            "| High-Level Category | Samples | Accuracy |",
            "|---|---|---|",
        ])
        for cat, data in results.get("per_category_metrics", {}).items():
            lines.append(f"| `{cat}` | {data['total']} | {data['accuracy']:.1f}% |")

        return "\n".join(lines)
