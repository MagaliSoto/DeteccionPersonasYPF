import cv2, os, datetime, base64, mediapipe as mp
from insightface.app import FaceAnalysis
from PIL import Image, ImageDraw, ImageFont

# Inicialización del modelo de rostros
face_model = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
face_model.prepare(ctx_id=0)

# Inicialización de MediaPipe para posturas
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=True)

def mejorar_imagen(img):
    """
    Convierte la imagen a RGB si es necesario.

    Parámetros:
        img (np.array): Imagen en formato BGR o RGB.

    Retorna:
        np.array: Imagen en formato RGB.
    """
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB) if len(img.shape) == 3 else img

def obtener_orientacion(img):
    """
    Determina la orientación corporal a partir de una imagen.

    Retorna:
        str: 'frente', 'perfil', 'espaldas' o 'desconocido'.
    """
    resultado = pose.process(img)
    if not resultado.pose_landmarks:
        return "desconocido"

    lms = resultado.pose_landmarks.landmark
    nariz = lms[mp_pose.PoseLandmark.NOSE]
    hombro_izq = lms[mp_pose.PoseLandmark.LEFT_SHOULDER]
    hombro_der = lms[mp_pose.PoseLandmark.RIGHT_SHOULDER]

    centro_hombros = (hombro_izq.x + hombro_der.x) / 2

    if nariz.visibility < 0.2:
        return "espaldas"
    elif abs(nariz.x - centro_hombros) > 0.1:
        return "perfil"
    return "frente"

def detectar_rostro_si_frente(img):
    """
    Detecta el rostro solo si la persona está de frente o de perfil.

    Retorna:
        (tuple | None, str): Coordenadas del rostro y orientación detectada.
    """
    img_rgb = mejorar_imagen(img)
    orientacion = obtener_orientacion(img_rgb)

    if orientacion == "espaldas":
        return None, "espaldas"

    rostros = face_model.get(img_rgb)
    if not rostros:
        return None, orientacion

    rostro = rostros[0]
    x1, y1, x2, y2 = map(int, rostro.bbox)
    return (x1, y1, x2, y2), orientacion

def guardar_imagen(imagen, id_interno, carpeta_salida, tipo):
    """
    Guarda una imagen (Cuerpo o Cara) en la carpeta correspondiente con un nombre único.

    Parámetros:
        imagen (ndarray): Imagen a guardar.
        id_interno (str): ID único de la persona.
        carpeta_salida (str): Carpeta raíz donde guardar imágenes.
        tipo (str): 'Cuerpo' o 'Caras'. Define la subcarpeta y nombre del archivo.

    Retorna:
        str | None: Ruta del archivo guardado o None si hubo error.
    """
    if imagen is None or imagen.size == 0:
        print(f"[ADVERTENCIA] Imagen vacía para ID {id_interno}")
        return None

    # Carpeta: personas/persona_X/Cuerpo o Caras
    carpeta_persona = os.path.join(carpeta_salida, f"persona_{id_interno}", tipo)
    os.makedirs(carpeta_persona, exist_ok=True)

    # Nombre único con timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")
    nombre_archivo = f"{tipo}_{id_interno}_{timestamp}.jpg"
    ruta_completa = os.path.join(carpeta_persona, nombre_archivo)

    # Guardar imagen localmente
    if not cv2.imwrite(ruta_completa, imagen):
        print(f"[ERROR] No se pudo guardar la imagen para ID {id_interno}")
        return None

    print(f"[INFO] Imagen guardada: {ruta_completa}")

    return ruta_completa

def encode_image(image_path):
    """
    Encodes an image file into a base64 string.
    Args:
        image_path (str): The path to the image file.

    This function opens the specified image file, reads its content, and encodes it into a base64 string.
    The base64 encoding is used to send images over HTTP as text.
    """

    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def crear_collage_con_titulos(img_path1, img_path2, titulo1="imgOriginal", titulo2="imgComparacion"):
    """
    Crea un collage horizontal de dos imágenes con títulos encima y lo devuelve como objeto PIL.Image.
    """
    img1 = Image.open(img_path1).convert("RGB")
    img2 = Image.open(img_path2).convert("RGB")

    # Igualar alturas
    if img1.height != img2.height:
        common_height = min(img1.height, img2.height)
        img1 = img1.resize((int(img1.width * common_height / img1.height), common_height))
        img2 = img2.resize((int(img2.width * common_height / img2.height), common_height))

    # Fuente
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()

    title_height = 30
    collage_width = img1.width + img2.width
    collage_height = img1.height + title_height

    collage = Image.new("RGB", (collage_width, collage_height), "white")
    draw = ImageDraw.Draw(collage)

    draw.text((img1.width // 2 - len(titulo1)*6, 5), titulo1, fill="black", font=font)
    draw.text((img1.width + img2.width // 2 - len(titulo2)*6, 5), titulo2, fill="black", font=font)

    collage.paste(img1, (0, title_height))
    collage.paste(img2, (img1.width, title_height))

    return collage