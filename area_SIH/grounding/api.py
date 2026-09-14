from PIL import Image
from grounding.inference import GroundingEngine
from grounding.visualization import draw_detections

def ground_objects(
    image: Image.Image,
    query: str,
    box_threshold: float = 0.20,
    text_threshold: float = 0.20
) -> dict:
    """
    Core API for grounding objects in an image via natural language query.
    
    Args:
        image (PIL.Image): Input image.
        query (str): The natural language query.
        box_threshold (float): Confidence threshold for bounding boxes.
        text_threshold (float): Not actively used by HF pipeline.
        
    Returns:
        dict: Contains query, target_label, count, detections, 
              annotated_image, processing_time, and pipeline_info.
    """
    engine = GroundingEngine.get_instance()
    
    # Run prediction (handles tiling, NMS, etc. internally)
    result = engine.predict(
        image,
        query,
        box_threshold=box_threshold,
        text_threshold=text_threshold
    )
    
    detections = result["detections"]
    target_label = result["target_label"]
    count = result["count"]
    
    # Draw premium detections on image
    annotated_image = draw_detections(
        image, 
        detections, 
        target_label=target_label, 
        count=count
    )
    
    return {
        "query": query,
        "target_label": target_label,
        "count": count,
        "detections": detections,
        "annotated_image": annotated_image,
        "processing_time": result.get("processing_time", 0.0),
        "pipeline_info": result.get("pipeline_info", {})
    }
