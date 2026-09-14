from app.schemas.image import ImageModality, ModalityDetectionResult

class ModalityDetectionService:
    @staticmethod
    def detect_modality(metadata: dict, filename: str) -> ModalityDetectionResult:
        """
        Uses heuristics based on raster metadata and filename to infer the image modality.
        Does not guarantee perfect accuracy since no ML is used here.
        """
        filename_lower = filename.lower()
        raster_meta = metadata.get("raster_metadata", {})
        bands = metadata.get("bands", 0)

        # Helper to check if a string contains any of the keywords
        def contains_any(text, keywords):
            text_lower = text.lower()
            return any(k.lower() in text_lower for k in keywords)

        # 1. Check for SAR
        sar_keywords = ["s1", "sar", "sentinel-1", "sentinel1", "radar"]
        polarizations = ["vv", "vh", "hh", "hv"]
        
        # Check filename
        if contains_any(filename_lower, sar_keywords):
            return ModalityDetectionResult(
                modality=ImageModality.SAR,
                confidence=None,
                reason="Filename contains SAR or Sentinel-1 indicators."
            )
            
        # Check metadata values for polarization
        # Sometimes band descriptions or tags contain 'VV', 'VH'
        for k, v in raster_meta.items():
            if isinstance(v, str) and contains_any(v, polarizations):
                return ModalityDetectionResult(
                    modality=ImageModality.SAR,
                    confidence=None,
                    reason=f"Raster metadata '{k}' contains polarization indicators."
                )

        # 2. Check for Multispectral
        ms_keywords = ["s2", "sentinel-2", "sentinel2", "l8", "landsat", "multispectral"]
        if contains_any(filename_lower, ms_keywords):
            return ModalityDetectionResult(
                modality=ImageModality.MULTISPECTRAL,
                confidence=None,
                reason="Filename contains Multispectral/Sentinel-2/Landsat indicators."
            )
            
        if bands > 4:
            return ModalityDetectionResult(
                modality=ImageModality.MULTISPECTRAL,
                confidence=None,
                reason=f"Image has {bands} bands, which typically indicates a multispectral image."
            )

        # 3. Check for Optical (RGB / RGBA)
        if bands in (3, 4):
            return ModalityDetectionResult(
                modality=ImageModality.OPTICAL,
                confidence=None,
                reason=f"Image has {bands} bands, strongly suggesting standard RGB/RGBA optical imagery."
            )

        # 4. Unknown
        return ModalityDetectionResult(
            modality=ImageModality.UNKNOWN,
            confidence=None,
            reason="Could not match any heuristics for SAR, Multispectral, or Optical."
        )
