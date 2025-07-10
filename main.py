import cv2, os, time
from queue import Queue
from threading import Thread
from concurrent.futures import ThreadPoolExecutor

from db_manager import DBManager
from utils.gestor_alertas import GestorAlertas
from detectores.detector_personas import DetectorPersonas
from descripciones.gestor_descripciones import GestorDescripciones

# Forzar transporte TCP en FFMPEG (muy útil para RTSP)
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
from_wpp = os.getenv("TWILIO_FROM_WPP")
to_wpp = os.getenv("TWILIO_TO_WPP")

def principal():
    ruta_video = os.getenv("RUTA_VIDEO", "rtsp://admin:2Mini001.@192.168.0.204/cam/realmonitor?channel=1&subtype=0")
    carpeta_salida = "Personas_Detectadas"

    prompt = (
        "Analiza visualmente a la persona en la imagen y genera una descripción detallada, "
        "estructurada en secciones claras. Usa títulos en negrita seguidos de listas con viñetas. "
        "Las secciones deben incluir:\n\n"
        "**Apariencia General**, **Rostro**, **Cabello**, **Ropa**, **Accesorios**, "
        "**Postura**, **Acciones**, **Entorno**, **Otros Detalles**.\n\n"
        "Sé claro y evita repetir lo mismo en varias secciones. Usa un estilo limpio y profesional."
    )

    estructura = {
        "ID": "INT PRIMARY KEY",
        "Imagen_cuerpo": "VARCHAR(50)",
        "Imagen_cara": "VARCHAR(50)",
        "Descripcion": "TEXT",
        "Fecha_registro": "DATETIME"
    }

    ejecutor = ThreadPoolExecutor(max_workers=4)
    db = DBManager("registro_personas", estructura)
    gestor_descripciones = GestorDescripciones(prompt, db)
    gestor_alertas = GestorAlertas(
    )

    detector = DetectorPersonas(
        carpeta_salida,
        gestor_alertas.actualizar,
        db,
        executor=ejecutor
    )

    cola_frames = Queue(maxsize=5)
    cola_resultados = Queue(maxsize=5)

    def trabajador():
        while True:
            item = cola_frames.get()
            if item is None:
                break
            indice, frame = item
            procesado = detector.procesar_frame(frame.copy())
            cola_resultados.put((indice, procesado))
            cola_frames.task_done()

    Thread(target=trabajador, daemon=True).start()

    while True:
        print("Intentando conectar al stream...")
        video = cv2.VideoCapture(ruta_video, cv2.CAP_FFMPEG)
        if not video.isOpened():
            print("Error al abrir el stream. Reintentando en 5 segundos...")
            time.sleep(5)
            continue

        contador_frames = 0
        ultimo_frame_procesado = None

        while video.isOpened():
            ret, frame = video.read()
            if not ret:
                print("Error al leer frame, reiniciando stream...")
                video.release()
                time.sleep(5)
                break                
            
            # Dibujar area
            cv2.rectangle(frame, (860, 550), (1640, 1000), (0, 255, 0), 2)

            if contador_frames % 5 == 0 and not cola_frames.full():
                cola_frames.put((contador_frames, frame.copy()))

            while not cola_resultados.empty():
                _, ultimo_frame_procesado = cola_resultados.get()

            mostrar = ultimo_frame_procesado if ultimo_frame_procesado is not None else frame
            cv2.imshow("Video en Vivo", mostrar)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Cerrando...")
                video.release()
                cv2.destroyAllWindows()
                return

            contador_frames += 1

if __name__ == "__main__":
    principal()
