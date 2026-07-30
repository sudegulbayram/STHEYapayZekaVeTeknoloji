import cv2
import numpy as np

def get_grayscale(image):
    # Resmi siyah-beyaz yapar, OCR (metin okuma) başarısını artırır.
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def remove_noise(image):
    # Leke/gürültü siler. '3' değeri bulanıklık derecesidir, büyütülürse leke gider ama metin de bulanıklaşır.
    return cv2.medianBlur(image, 3)

def thresholding(image):
    # Arka planı bembeyaz, yazıyı simsiyah yapar. '11' blok boyutu, '2' kontrast hassasiyetidir.
    return cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                 cv2.THRESH_BINARY, 11, 2)

def deskew(image):
    # Eğik çekilmiş belge fotoğrafını düzeltir. Eğer açı (-0.5 ile +0.5) dışındaysa döndürme uygular.
    gray = cv2.bitwise_not(image)
    coords = np.column_stack(np.where(gray > 0))
    angle = cv2.minAreaRect(coords)[-1]

    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    if abs(angle) < 0.5:
        return image

    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    
    return rotated

def preprocess_for_ocr(image_path, save_debug=False):
    # Görüntü iyileştirme adımlarını sırayla uygular, save_debug=True verilirse debug için sonucu diske kaydeder.
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Görüntü bulunamadı veya okunamadı: {image_path}")
        
    gray = get_grayscale(img)
    thresh = thresholding(gray)
    deskewed = deskew(thresh)
    
    if save_debug:
        debug_path = image_path.replace(".", "_preprocessed.")
        cv2.imwrite(debug_path, deskewed)
        
    return deskewed

if __name__ == "__main__":
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_img = os.path.join(current_dir, "belirsiz-sureli-is-sozlesmesi-1.png")
    
    if os.path.exists(test_img):
        preprocess_for_ocr(test_img, save_debug=True)
