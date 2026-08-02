"""
pdf_utils.py
------------
PDF dosyalarını OCR pipeline'ının işleyebileceği görüntülere (cv2/numpy array)
çevirir. PyMuPDF (fitz) kullanır - Poppler gibi ayrı bir sistem programı
kurulumu gerektirmez.
"""

import cv2
import fitz  # PyMuPDF
import numpy as np


def pdf_to_images(pdf_path: str, dpi: int = 300):
    """PDF'in her sayfasını BGR (OpenCV) formatında bir numpy array olarak döner."""

    doc = fitz.open(pdf_path)
    zoom = dpi / 72  # PDF'ler 72 DPI varsayar; OCR için daha yüksek çözünürlük gerekir.
    matrix = fitz.Matrix(zoom, zoom)

    images = []
    try:
        for page in doc:
            pix = page.get_pixmap(matrix=matrix)
            arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)

            if pix.n == 4:
                arr = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)
            elif pix.n == 3:
                arr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
            elif pix.n == 1:
                arr = cv2.cvtColor(arr, cv2.COLOR_GRAY2BGR)

            images.append(arr)
    finally:
        doc.close()

    if not images:
        raise ValueError(f"PDF'ten hiç sayfa render edilemedi: {pdf_path}")

    return images