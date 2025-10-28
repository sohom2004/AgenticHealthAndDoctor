"""
OCR-related tools for document processing
"""
import os
import ast
from pdf2image import convert_from_path
import easyocr
from config.settings import TEMP_DIR, OCR_LANGUAGES, OCR_GPU


def get_file_type(doc_path: str) -> str:
    """
    Detects if a given file path is a PDF or an image
    
    Args:
        doc_path: Path to the file
        
    Returns:
        "pdf" or "image"
    """
    if not os.path.exists(doc_path):
        raise FileNotFoundError(f"File Not Found: {doc_path}")
    
    if doc_path.lower().endswith(".pdf"):
        return "pdf"
    elif doc_path.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".tiff")):
        return "image"
    else:
        raise ValueError("Unsupported File Type. Must be pdf or image.")


def convert_to_jpg(pdf_path: str) -> list:
    """
    Converts PDF files to images for performing OCR
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        List of image file paths
    """
    pages = convert_from_path(pdf_path)
    pg_arr = []
    
    for i, page in enumerate(pages):
        path = TEMP_DIR / f"temp_page_{i}.png"
        page.save(str(path), "PNG")
        pg_arr.append(str(path))
    
    print(f"Extracted {len(pg_arr)} pages from PDF")
    return pg_arr


def get_ocr(imgs) -> dict:
    """
    Performs OCR on images using EasyOCR
    
    Args:
        imgs: List of image paths or single image path
        
    Returns:
        Dictionary with 'content' and 'confidence'
    """
    if isinstance(imgs, str):
        try:
            imgs = ast.literal_eval(imgs)
        except Exception:
            imgs = [imgs]
    
    if not isinstance(imgs, list):
        imgs = [imgs]
    
    reader = easyocr.Reader(OCR_LANGUAGES, gpu=OCR_GPU)
    all_text = []
    all_score = []
    
    for img_path in imgs:
        result = reader.readtext(img_path, detail=1)
        for (_, text, score) in result:
            all_text.append(text)
            all_score.append(score)
    
    page_content = "\n".join(all_text)
    avg_confidence = sum(all_score) / len(all_score) if all_score else 0.0
    
    return {
        "content": page_content,
        "confidence": avg_confidence
    }


def cleanup_temp_files():
    """
    Cleans up temporary image files
    """
    for file in TEMP_DIR.glob("temp_page_*.png"):
        try:
            file.unlink()
        except Exception as e:
            print(f"Error deleting {file}: {e}")