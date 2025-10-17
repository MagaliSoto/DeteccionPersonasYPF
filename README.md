# 🚨 Demo RED YPF 2025

**Detección inteligente de ingreso y egreso de personas con control visual asistido por IA**

---

## 🧠 Descripción general

Esta demo fue desarrollada para la **Expo RED YPF 2025** con el objetivo de mostrar cómo la inteligencia artificial puede contribuir a la **seguridad operativa en entornos industriales**.

El sistema analiza en tiempo real la transmisión de una cámara **RTSP** y detecta la presencia de personas dentro de un área delimitada.
Mediante una integración con modelos de **visión artificial (YOLO)** y análisis con **Gemini AI**, el sistema identifica si las personas que ingresan o salen del área **llevan puesto un chaleco naranja** — simulando un control automático de acceso con verificación visual de elementos de seguridad.

Cuando se confirma la presencia (o ausencia) del chaleco, se envía una **alerta inmediata por Telegram**, notificando el evento de ingreso o salida.

---

## ⚙️ Flujo general del sistema

1. **Captura en tiempo real:**
   Se lee el stream desde una cámara RTSP configurada en el sistema.

2. **Detección de personas:**
   Un modelo **YOLOv11** especializado detecta personas en la escena y calcula sus coordenadas.

3. **Control de área:**
   Se determina si la persona entra o sale del área definida (editable en el código).

4. **Verificación visual del chaleco:**
   La imagen del cuerpo detectado se envía a **Gemini** para confirmar si la persona **usa un chaleco naranja**.

5. **Registro y alerta:**

   * Se guarda la información en una base de datos MySQL.
   * Se envía una **notificación automática por Telegram** con la evidencia visual.

---

## 🧩 Componentes principales

| Componente                | Descripción                                                      |
| ------------------------- | ---------------------------------------------------------------- |
| **YOLOv11 (ultralytics)** | Detección de personas en la imagen.                              |
| **Gemini AI (Google)**    | Análisis visual para confirmar la presencia del chaleco naranja. |
| **MySQL**                 | Almacenamiento de registros con imagen, descripción y fecha.     |
| **Telegram Bot**          | Envío de alertas instantáneas ante detección de ingreso/salida.  |
| **OpenCV**                | Lectura de cámara RTSP y procesamiento de frames en tiempo real. |

---

## 🗄️ Estructura de la base de datos

La tabla se crea automáticamente desde el script principal (`main.py`) con la siguiente estructura:

| Campo            | Tipo            | Descripción                                    |
| ---------------- | --------------- | ---------------------------------------------- |
| `ID`             | INT PRIMARY KEY | Identificador único.                           |
| `Imagen_cuerpo`  | VARCHAR(50)     | Ruta de la imagen del cuerpo detectado.        |
| `Imagen_cara`    | VARCHAR(50)     | Ruta de la imagen facial asociada (si aplica). |
| `Descripcion`    | TEXT            | Resultado del análisis con Gemini.             |
| `Fecha_registro` | DATETIME        | Fecha y hora del evento.                       |

---

## 🔧 Configuración del entorno

### 1. Requisitos

* Python 3.9+
* Dependencias (instalación automática):

  ```bash
  pip install -r requirements.txt
  ```

### 2. Variables de entorno

Crear un archivo `.env` en la raíz del proyecto con las siguientes claves (ajustar valores según tu entorno):

```env
# API de Gemini
GEMINI_API_KEY=tu_api_key_de_gemini

# Base de datos MySQL
MYSQL_ROOT_PASSWORD=tu_password
MYSQL_DATABASE=seguridad

# Configuración de Twilio (solo si se desea usar WhatsApp)
TWILIO_ACCOUNT_SID=tu_sid
TWILIO_AUTH_TOKEN=tu_token
TWILIO_FROM_WPP=whatsapp:+14155238886
TWILIO_TO_WPP=whatsapp:+549XXXXXXXXX
```

> 💬 Actualmente la demo usa **Telegram** para alertas, pero la lógica conserva compatibilidad con **Twilio/WhatsApp** si se desea reactivar en el futuro.

---

## 📍 Área de detección

Las coordenadas del área de control se pueden modificar directamente desde el archivo **`main.py`**.
Allí se define la región en la que el sistema considera una persona **“dentro del área”** o **“fuera del área”**.

Ejemplo:

```python
if 860 <= cx <= 1640 and 550 <= cy <= 1000:
    # Persona dentro del área
```

---

## 🚀 Ejecución

Una vez configurado el entorno, simplemente ejecutar:

```bash
python main.py
```

El sistema iniciará la lectura de la cámara RTSP, analizará las detecciones y comenzará a registrar y alertar los eventos.

---

## 👩‍💻 Autora

**Magali Soto**
Desarrolladora de software e integración de sistemas de visión artificial.

---

## 💡 Notas finales

Esta demo fue diseñada con fines de **exhibición tecnológica** para la Expo RED YPF 2025, mostrando el potencial de la inteligencia artificial aplicada a la **seguridad industrial** y la **automatización del control de acceso**.

El sistema es modular, adaptable y puede integrarse fácilmente con cámaras IP, sistemas de registro o plataformas de control de acceso existentes.

---
