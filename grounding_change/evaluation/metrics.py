"""
Evaluation Metrics for Multitemporal Change Intelligence.
Computes:
- Binary Change: Precision, Recall, F1, IoU, Dice
- Semantic Segmentation: mIoU, per-class IoU, Confusion Matrix
- Visual Grounding: Mask IoU, Bounding Box IoU
- Temporal VQA: Accuracy, Exact Match
- Quantification: Area Error, Change Percentage Absolute Error
- Geospatial: Coordinate consistency error
"""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from ..taxonomy import taxonomy


class ChangeMetrics:
    """
    Standard quantitative evaluation metrics for change detection and segmentation.
    """

    @staticmethod
    def binary_change_metrics(
        pred_mask: np.ndarray,
        target_mask: np.ndarray,
        smooth: float = 1e-6
    ) -> Dict[str, float]:
        """
        Calculates Precision, Recall, F1, IoU, and Dice on binary change masks.
        """
        p = (pred_mask > 0).astype(bool)
        t = (target_mask > 0).astype(bool)

        tp = np.logical_and(p, t).sum()
        fp = np.logical_and(p, ~t).sum()
        fn = np.logical_and(~p, t).sum()
        tn = np.logical_and(~p, ~t).sum()

        precision = (tp + smooth) / (tp + fp + smooth)
        recall = (tp + smooth) / (tp + fn + smooth)
        f1 = (2 * precision * recall) / (precision + recall + smooth)
        iou = (tp + smooth) / (tp + fp + fn + smooth)
        dice = (2 * tp + smooth) / (p.sum() + t.sum() + smooth)

        return {
            "precision": round(float(precision), 4),
            "recall": round(float(recall), 4),
            "f1": round(float(f1), 4),
            "iou": round(float(iou), 4),
            "dice": round(float(dice), 4),
            "true_positives": int(tp),
            "false_positives": int(fp),
            "false_negatives": int(fn),
        }

    @staticmethod
    def semantic_change_metrics(
        pred_classes: np.ndarray,
        target_classes: np.ndarray,
        num_classes: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Computes mean IoU (mIoU), per-class IoU, and confusion matrix for multi-class maps.
        """
        k = num_classes or taxonomy.num_classes
        confusion_matrix = np.zeros((k, k), dtype=np.int64)

        for true_c in range(k):
            for pred_c in range(k):
                confusion_matrix[true_c, pred_c] = np.sum((target_classes == true_c) & (pred_classes == pred_c))

        per_class_iou = {}
        ious = []
        for c in range(k):
            tp = confusion_matrix[c, c]
            fp = confusion_matrix[:, c].sum() - tp
            fn = confusion_matrix[c, :].sum() - tp
            denom = tp + fp + fn
            cat_name = taxonomy.get_by_id(c).name
            if denom > 0:
                iou_c = tp / denom
                per_class_iou[cat_name] = round(float(iou_c), 4)
                ious.append(iou_c)
            else:
                per_class_iou[cat_name] = 1.0

        miou = np.mean(ious) if ious else 0.0

        return {
            "mIoU": round(float(miou), 4),
            "per_class_iou": per_class_iou,
            "confusion_matrix": confusion_matrix.tolist()
        }

    @staticmethod
    def box_iou(box1: List[int], box2: List[int]) -> float:
        """Computes IoU between two bounding boxes [x1, y1, x2, y2]."""
        x_left = max(box1[0], box2[0])
        y_top = max(box1[1], box2[1])
        x_right = min(box1[2], box2[2])
        y_bottom = min(box1[3], box2[3])

        if x_right < x_left or y_bottom < y_top:
            return 0.0

        intersection = (x_right - x_left) * (y_bottom - y_top)
        area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
        area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
        union = area1 + area2 - intersection
        return round(float(intersection / max(union, 1e-6)), 4)

    @staticmethod
    def vqa_accuracy(predictions: List[str], ground_truths: List[str]) -> Dict[str, float]:
        """Calculates exact match and token overlap accuracy for VQA answers."""
        if not predictions or len(predictions) != len(ground_truths):
            return {"exact_match": 0.0, "token_f1": 0.0}

        exact_matches = 0
        token_f1s = []

        for pred, gt in zip(predictions, ground_truths):
            p_clean = pred.lower().strip()
            g_clean = gt.lower().strip()

            if p_clean == g_clean:
                exact_matches += 1

            p_toks = set(p_clean.split())
            g_toks = set(g_clean.split())
            common = p_toks.intersection(g_toks)
            if not p_toks or not g_toks:
                token_f1s.append(1.0 if p_toks == g_toks else 0.0)
            else:
                prec = len(common) / len(p_toks)
                rec = len(common) / len(g_toks)
                f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0
                token_f1s.append(f1)

        return {
            "exact_match": round(float(exact_matches / len(predictions)), 4),
            "token_f1": round(float(np.mean(token_f1s)), 4)
        }

    @staticmethod
    def quantification_error(
        predicted_pct: float,
        target_pct: float,
        predicted_area_m2: Optional[float] = None,
        target_area_m2: Optional[float] = None
    ) -> Dict[str, float]:
        """Calculates area quantification error."""
        pct_error = abs(predicted_pct - target_pct)
        res = {"percentage_error": round(float(pct_error), 4)}
        if predicted_area_m2 is not None and target_area_m2 is not None:
            res["area_error_m2"] = round(float(abs(predicted_area_m2 - target_area_m2)), 2)
            rel_error = abs(predicted_area_m2 - target_area_m2) / max(target_area_m2, 1.0)
            res["area_relative_error"] = round(float(rel_error), 4)
        return res
