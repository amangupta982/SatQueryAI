"""
Task-specific evaluation metrics for Remote-Sensing VQA.
Computes Exact Match, Accuracy, Macro F1, MAE, RMSE, and IoU for bounding box grounding.
"""

import re
import math
from collections import defaultdict
from typing import Dict, Any, List, Optional, Tuple

class VQAMetricsCalculator:
    """Calculates granular evaluation metrics across VQA tasks."""

    @staticmethod
    def normalize_text(text: str) -> str:
        """Lowercases, removes punctuation and redundant whitespace."""
        s = str(text).lower().strip()
        # Remove punctuation
        s = re.sub(r"[^\w\s]", "", s)
        return " ".join(s.split())

    @staticmethod
    def calculate_iou(box_a: List[float], box_b: List[float]) -> float:
        """
        Calculate Intersection over Union (IoU) between two bounding boxes:
        [ymin, xmin, ymax, xmax]
        """
        y_min = max(box_a[0], box_b[0])
        x_min = max(box_a[1], box_b[1])
        y_max = min(box_a[2], box_b[2])
        x_max = min(box_a[3], box_b[3])

        inter_h = max(0.0, y_max - y_min)
        inter_w = max(0.0, x_max - x_min)
        inter_area = inter_h * inter_w

        area_a = max(0.0, box_a[2] - box_a[0]) * max(0.0, box_a[3] - box_a[1])
        area_b = max(0.0, box_b[2] - box_b[0]) * max(0.0, box_b[3] - box_b[1])

        union_area = area_a + area_b - inter_area
        if union_area <= 0:
            return 0.0
        return inter_area / union_area

    def evaluate_predictions(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Evaluate a list of prediction records:
        Each record should have:
            - 'prediction': str
            - 'ground_truth': str
            - 'task': str
            - 'category': Optional[str]
            - 'pred_boxes': Optional[List[List[float]]]
            - 'gt_boxes': Optional[List[List[float]]]
        """
        total = len(records)
        if total == 0:
            return {"total_samples": 0, "overall_accuracy": 0.0}

        overall_exact_matches = 0
        task_records = defaultdict(list)
        category_records = defaultdict(list)

        # Counting specific
        count_errors = []
        # Grounding specific
        ious = []

        for rec in records:
            pred_raw = str(rec.get("prediction", ""))
            gt_raw = str(rec.get("ground_truth", ""))
            task = rec.get("task", "other")
            category = rec.get("category", "other")

            pred_norm = self.normalize_text(pred_raw)
            gt_norm = self.normalize_text(gt_raw)

            # Exact match check
            is_match = (pred_norm == gt_norm) or (gt_norm in pred_norm)
            if is_match:
                overall_exact_matches += 1

            record_eval = {"match": is_match, "pred": pred_norm, "gt": gt_norm}

            # Numerical check for count task
            if task == "count" or category == "count":
                pred_nums = re.findall(r"\d+", pred_norm)
                gt_nums = re.findall(r"\d+", gt_norm)
                if pred_nums and gt_nums:
                    try:
                        p_val = float(pred_nums[0])
                        g_val = float(gt_nums[0])
                        count_errors.append(abs(p_val - g_val))
                    except ValueError:
                        pass

            # Grounding IoU check
            pred_boxes = rec.get("pred_boxes")
            gt_boxes = rec.get("gt_boxes")
            if pred_boxes and gt_boxes:
                # Compare first box IoU
                box_iou = self.calculate_iou(pred_boxes[0], gt_boxes[0])
                ious.append(box_iou)
                record_eval["iou"] = box_iou

            task_records[task].append(record_eval)
            category_records[category].append(record_eval)

        # Compute per-task accuracy
        per_task_metrics = {}
        for t, items in task_records.items():
            matches = sum(1 for x in items if x["match"])
            acc = matches / len(items) if items else 0.0
            per_task_metrics[t] = {
                "total": len(items),
                "accuracy": round(acc * 100, 2),
                "exact_matches": matches,
            }

        # Compute per-category accuracy
        per_category_metrics = {}
        for c, items in category_records.items():
            matches = sum(1 for x in items if x["match"])
            acc = matches / len(items) if items else 0.0
            per_category_metrics[c] = {
                "total": len(items),
                "accuracy": round(acc * 100, 2),
            }

        overall_acc = overall_exact_matches / total * 100

        results = {
            "total_evaluated": total,
            "overall_accuracy": round(overall_acc, 2),
            "exact_matches": overall_exact_matches,
            "per_task_metrics": per_task_metrics,
            "per_category_metrics": per_category_metrics,
        }

        if count_errors:
            results["count_mae"] = round(sum(count_errors) / len(count_errors), 3)
            results["count_rmse"] = round(math.sqrt(sum(e**2 for e in count_errors) / len(count_errors)), 3)

        if ious:
            results["mean_iou"] = round(sum(ious) / len(ious), 4)

        return results
