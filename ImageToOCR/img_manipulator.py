'''Questo file gestisce la manipolazione della foto per migliorarne la leggibilità.'''
from skimage.filters import threshold_local
import cv2

def enhance_image(path: str) -> str:
    '''Questa funzione permette di migliorare la leggibilità dell'immagine.'''
    if path is None:
        print("Errore, non mi arriva nessuna path.")
        return None
    img = cv2.imread(path)
    # convert the image to grayscale, then threshold it
    # to give it that 'black and white' paper effect
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    threshold = threshold_local(img, 11, offset = 12, method = "gaussian")
    img = (img > threshold).astype("uint8") * 255
    cv2.imwrite('detected/' + path, img)
    return 'detected/' + path
