import numpy as np
from PIL import Image, ImageDraw, ImageFont


def draw_detections(
    image: Image.Image,
    detections: list,
    target_label: str = "",
    count: int = 0
) -> np.ndarray:
    """
    Premium visualization for satellite grounding detections.
    
    Draws tight bounding boxes with corner accents, scales font based
    on image resolution, and adds a count header legend.
    
    Args:
        image: Original PIL Image.
        detections: List of detection dicts with 'score', 'label', 'box'.
        target_label: The parsed query target for the legend.
        count: Total number of detections for the legend.
        
    Returns:
        np.ndarray: Annotated RGB image array.
    """
    img_w, img_h = image.size
    annotated = image.copy()
    draw = ImageDraw.Draw(annotated)

    # 1. Determine scaled UI sizes based on image dimensions
    min_dim = min(img_w, img_h)
    
    # Scale font size (e.g., size 16 for an 800px image, scaling up/down)
    font_size = max(14, int(16 * (min_dim / 800)))
    
    # Scale line widths
    box_width = max(2, int(3 * (min_dim / 800)))
    accent_width = box_width * 2
    accent_length = max(10, int(20 * (min_dim / 800)))

    # Try loading a readable font
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
        legend_font = ImageFont.truetype("arialbd.ttf", int(font_size * 1.5)) # Bold, larger
    except IOError:
        try:
            font = ImageFont.truetype("DejaVuSans.ttf", font_size)
            legend_font = ImageFont.truetype("DejaVuSans-Bold.ttf", int(font_size * 1.5))
        except IOError:
            font = ImageFont.load_default()
            legend_font = ImageFont.load_default()

    # 2. Curated bright color palette (easy to see on satellite imagery)
    # Magenta, Cyan, Lime Green, Vivid Orange, Hot Pink, Bright Yellow
    COLORS = ["#FF2A85", "#00F0FF", "#39FF14", "#FF7B00", "#FF00E4", "#FFEA00"]

    # 3. Draw Legend Header (if we have target info)
    if count > 0 and target_label:
        header_text = f" DETECTED: {count} {target_label.upper()}(S) "
        
        # Calculate header bounds
        try:
            bbox = legend_font.getbbox(header_text)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
        except AttributeError:
            text_w, text_h = draw.textsize(header_text, font=legend_font)

        pad = int(10 * (min_dim / 800))
        margin = int(20 * (min_dim / 800))
        
        # Draw semi-transparent dark background for legend at top-center
        legend_x = (img_w - text_w) // 2
        legend_y = margin
        
        # Create an overlay for transparency
        overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        
        bg_rect = [
            legend_x - pad * 2, 
            legend_y - pad, 
            legend_x + text_w + pad * 2, 
            legend_y + text_h + pad
        ]
        
        overlay_draw.rectangle(bg_rect, fill=(0, 0, 0, 180)) # 70% opacity black
        annotated = Image.alpha_composite(annotated.convert("RGBA"), overlay).convert("RGB")
        draw = ImageDraw.Draw(annotated)
        
        # Draw legend text in bright yellow/gold
        draw.text((legend_x, legend_y), header_text, fill="#FFD700", font=legend_font)

    # 4. Draw Detections
    for i, det in enumerate(detections):
        box = det["box"]
        xmin, ymin, xmax, ymax = box["xmin"], box["ymin"], box["xmax"], box["ymax"]
        
        # Clamp to image boundaries
        xmin, ymin = max(0, xmin), max(0, ymin)
        xmax, ymax = min(img_w - 1, xmax), min(img_h - 1, ymax)
        
        score = det["score"]
        label = det["label"].upper()
        color = COLORS[i % len(COLORS)]
        det["color"] = color  # Inject for frontend UI
        
        # A. Draw Main Bounding Box (Semi-transparent inner outline)
        overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        
        # Convert hex color to RGBA tuple for the overlay
        color_rgb = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        color_rgba = color_rgb + (150,) # ~60% opacity
        
        overlay_draw.rectangle([xmin, ymin, xmax, ymax], outline=color_rgba, width=box_width)
        annotated = Image.alpha_composite(annotated.convert("RGBA"), overlay).convert("RGB")
        draw = ImageDraw.Draw(annotated)
        
        # B. Draw Corner Accents (Solid color)
        # Top-Left
        draw.line([(xmin, ymin), (xmin + accent_length, ymin)], fill=color, width=accent_width)
        draw.line([(xmin, ymin), (xmin, ymin + accent_length)], fill=color, width=accent_width)
        # Top-Right
        draw.line([(xmax, ymin), (xmax - accent_length, ymin)], fill=color, width=accent_width)
        draw.line([(xmax, ymin), (xmax, ymin + accent_length)], fill=color, width=accent_width)
        # Bottom-Left
        draw.line([(xmin, ymax), (xmin + accent_length, ymax)], fill=color, width=accent_width)
        draw.line([(xmin, ymax), (xmin, ymax - accent_length)], fill=color, width=accent_width)
        # Bottom-Right
        draw.line([(xmax, ymax), (xmax - accent_length, ymax)], fill=color, width=accent_width)
        draw.line([(xmax, ymax), (xmax, ymax - accent_length)], fill=color, width=accent_width)

        # C. Format Label Text
        text = f"{label} #{i+1} — {score*100:.1f}%"
        
        try:
            bbox = font.getbbox(text)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
        except AttributeError:
            text_w, text_h = draw.textsize(text, font=font)
            
        # Draw label background
        pad = int(4 * (min_dim / 800))
        text_y_top = max(0, ymin - text_h - pad * 2)
        
        # If the label would go off the top of the image, put it inside the box at the top
        if text_y_top == 0 and ymin < (text_h + pad * 2):
            text_y_top = ymin + box_width
            
        bg_rect = [xmin, text_y_top, xmin + text_w + pad * 2, text_y_top + text_h + pad * 2]
        
        # Draw solid background for label readability
        draw.rectangle(bg_rect, fill=color)
        
        # Text color: black or white depending on background luminance
        luminance = (0.299 * color_rgb[0] + 0.587 * color_rgb[1] + 0.114 * color_rgb[2]) / 255
        text_color = "black" if luminance > 0.5 else "white"
        
        # Draw text
        draw.text((xmin + pad, text_y_top + pad), text, fill=text_color, font=font)

    return np.array(annotated)
