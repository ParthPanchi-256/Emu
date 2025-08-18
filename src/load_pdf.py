from src.log import logger
from pathlib import Path
from typing import Dict, List, Tuple, Any
from PIL import Image
import numpy as np

from src.config import CONFIG

# PyMuPDF for PDF processing
import fitz



def process_pdf(pdf_path: Path) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Process a PDF to extract text chunks and images with captions.
    """
    logger.info(f"Processing PDF: {pdf_path}")

    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        logger.error(f"Error opening PDF: {e}")
        return [], []

    text_chunks = []
    image_data_list = []

    for page_num in range(len(doc)):
        page = doc[page_num]

        # Extract and chunk text
        text = page.get_text()
        for i in range(0, len(text), CONFIG["chunk_size"] - CONFIG["chunk_overlap"]):
            chunk_content = text[i:i + CONFIG["chunk_size"]]
            if chunk_content.strip():
                text_chunks.append({
                    "content": chunk_content,
                    "metadata": {"page": page_num, "source": str(pdf_path), "type": "text"}
                })

        # Extract images with captions
        for img_index, img in enumerate(page.get_images(full=True)):
            try:
                xref = img[0]
                base_image = page.parent.extract_image(xref)
                rect = page.get_image_bbox(img)

                # Try to get nearby text as caption
                caption_text = ""
                words = page.get_text("words")
                relevant_words = [
                    w[4] for w in words if (
                        w[1] > rect.y1 and
                        w[1] < rect.y1 + 100 and
                        w[0] > rect.x0 - 50 and
                        w[2] < rect.x1 + 50
                    )
                ]
                caption_text = " ".join(relevant_words)

                image_data = {
                    "content": base_image["image"],
                    "metadata": {
                        "caption": caption_text.strip(),
                        "figure_num": img_index,
                        "source": str(pdf_path),
                        "page": page_num,
                        "type": "image"
                    }
                }
                image_data_list.append(image_data)
            except Exception as e:
                logger.warning(f"Error extracting image {img_index}: {e}")

    return text_chunks, image_data_list