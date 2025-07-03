import cv2, requests
from utils import imagenes_utils as iu
from utils import gemini_utils as gu

class GestorDescripciones:
    def __init__(self, prompt, database):
        self.prompt = prompt

        # Instancia del manejador de base de datos
        self.db = database

    def describir_con_gemini(self, imagen, id_persona):
        """
        Genera una descripción de una persona usando el modelo Gemini de Google.
        """
        try:
            # Analizar imagen con Gemini y guardar el resultado
            descripcion = gu.analizar_img_con_gemini(imagen, self.prompt)

            self.db.guardar_descripcion(id_persona, descripcion)
            
        except Exception as e:
            print(f"[ERROR] Gemini: ID {id_persona} - {e}")

    def describir_con_coglvm(self, imagen_path, id_persona, prompt="Describí detalladamente la vestimenta de la persona."):
        """
        Genera una descripción de una persona usando el modelo CogVLM a través de una API tipo OpenAI.
        Recibe la ruta de una imagen y envía una solicitud al servidor local.

        Args:
            imagen_path (str): Ruta a la imagen en disco.
            id_persona (str | int): ID único de la persona para guardar la descripción.
            prompt (str): Texto de entrada para guiar la descripción.
        """
        try:
            # Codificar la imagen en base64 usando imagenes_utils
            img_base64 = iu.encode_image(imagen_path)
            img_url = f"data:image/jpeg;base64,{img_base64}"

            # Armar mensajes para la API de chat
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt,
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": img_url
                            },
                        },
                    ],
                }
            ]

            # Enviar la solicitud al servidor local de CogVLM
            response = requests.post(
                "https://buck-tough-louse.ngrok-free.app/v1/chat/completions",
                json={
                    "model": "cogvlm-chat-17b",
                    "messages": messages,
                    "stream": False,
                    "max_tokens": 1024,
                    "temperature": 0.8,
                    "top_p": 0.8,
                },
                timeout=200,
            )

            # Procesar respuesta
            if response.status_code == 200:
                decoded = response.json()
                descripcion = decoded.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
                self.db.guardar_descripcion(id_persona, descripcion)
            else:
                print(f"[ERROR] CogVLM: respuesta {response.status_code}")
        except Exception as e:
            print(f"[ERROR] CogVLM: ID {id_persona} - {e}")

    def describir_con_vila(self, imagen, id_persona, prompt):
        try:
            _, img_encoded = cv2.imencode(".jpg", cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB))
            files = {
                'file': ('persona.jpg', img_encoded.tobytes(), 'image/jpeg'),
            }
            data = {
                'prompt': prompt
            }

            r = requests.post("http://18.228.157.19:7000/describe_image_file/", files=files, data=data, timeout=60)

            if r.status_code == 200:
                self.db.guardar_descripcion(r.text, id_persona)
            else:
                print(f"[ERROR] VILA: respuesta {r.status_code}")
        except Exception as e:
            print(f"[ERROR] VILA: ID {id_persona} - {e}")

