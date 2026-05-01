import pytesseract
from PIL import Image

def extrair_texto(caminho):
    try:
        img = Image.open(caminho)
        texto = pytesseract.image_to_string(img, lang="por")
        return texto
    except:
        return ""