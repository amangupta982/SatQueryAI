"""
Temporal Co-Registration & Geometric Alignment.
Aligns T2 to T1 to suppress false change detections caused by camera jitter,
platform orbital shifts, or sub-pixel misregistrations.
"""

from typing import Optional, Tuple
import cv2
import numpy as np


class TemporalAligner:
    """
    Performs feature-based (ORB/homography) or intensity-based (ECC)
    co-registration between temporal image pairs.
    """

    def __init__(self, max_features: int = 2000, match_ratio: float = 0.75):
        self.max_features = max_features
        self.match_ratio = match_ratio

    def align(
        self,
        img_t1: np.ndarray,
        img_t2: np.ndarray,
        method: str = "orb"
    ) -> Tuple[np.ndarray, np.ndarray, bool]:
        """
        Align img_t2 to img_t1 coordinate frame.

        Args:
            img_t1: Reference image (H, W, C) or (H, W)
            img_t2: Target image to align to T1
            method: 'orb' (fast feature-based) or 'ecc' (intensity gradient based)

        Returns:
            aligned_t2: T2 warped into T1 coordinate frame
            transform_matrix: 3x3 homography or 2x3 affine matrix
            success: Whether confident alignment was achieved
        """
        # Ensure compatible formats
        if img_t1.shape[:2] != img_t2.shape[:2]:
            # Resize T2 to match T1 dimensions if slightly mismatched
            img_t2 = cv2.resize(img_t2, (img_t1.shape[1], img_t1.shape[0]))

        # Convert to grayscale for keypoint detection
        gray1 = cv2.cvtColor(img_t1, cv2.COLOR_RGB2GRAY) if img_t1.ndim == 3 else img_t1
        gray2 = cv2.cvtColor(img_t2, cv2.COLOR_RGB2GRAY) if img_t2.ndim == 3 else img_t2

        if method == "orb":
            return self._align_orb(gray1, gray2, img_t2)
        else:
            return self._align_ecc(gray1, gray2, img_t2)

    def _align_orb(
        self,
        gray1: np.ndarray,
        gray2: np.ndarray,
        img_t2: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray, bool]:
        orb = cv2.ORB_create(self.max_features)
        kp1, des1 = orb.detectAndCompute(gray1, None)
        kp2, des2 = orb.detectAndCompute(gray2, None)

        if des1 is None or des2 is None or len(kp1) < 4 or len(kp2) < 4:
            return img_t2, np.eye(3), False

        # Match features with BFMatcher
        matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
        matches = matcher.knnMatch(des1, des2, k=2)

        good_matches = []
        for m_pair in matches:
            if len(m_pair) == 2:
                m, n = m_pair
                if m.distance < self.match_ratio * n.distance:
                    good_matches.append(m)

        if len(good_matches) < 8:
            return img_t2, np.eye(3), False

        src_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)

        # Estimate homography with RANSAC
        h_mat, inliers = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

        if h_mat is None:
            return img_t2, np.eye(3), False

        h, w = gray1.shape[:2]
        aligned_t2 = cv2.warpPerspective(img_t2, h_mat, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        return aligned_t2, h_mat, True

    def _align_ecc(
        self,
        gray1: np.ndarray,
        gray2: np.ndarray,
        img_t2: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray, bool]:
        h, w = gray1.shape[:2]
        warp_matrix = np.eye(2, 3, dtype=np.float32)
        criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 50, 1e-4)

        try:
            _, warp_matrix = cv2.findTransformECC(gray1, gray2, warp_matrix, cv2.MOTION_AFFINE, criteria)
            aligned_t2 = cv2.warpAffine(img_t2, warp_matrix, (w, h), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_REFLECT)
            return aligned_t2, warp_matrix, True
        except Exception:
            return img_t2, np.eye(2, 3), False
