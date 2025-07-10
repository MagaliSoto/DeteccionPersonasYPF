import time
#from twilio.rest import Client

class GestorAlertas:
    def __init__(self, funcion_descripcion=None, umbral=0.7, timeout=5.0,
                 account_sid="", auth_token="", from_wpp="", to_wpp=""):
        self.funcion_descripcion = funcion_descripcion
        self.umbral = umbral
        self.timeout = timeout
        self.personas_en_area = {}  # id_persona -> timestamp_ultimo_visto

        # Twilio
        #self.twilio_client = Client(account_sid, auth_token)
        self.from_whatsapp = from_wpp
        self.to_whatsapp = to_wpp

    def enviar_wpp(self, mensaje):
        try:
            self.twilio_client.messages.create(
                body=mensaje,
                from_=self.from_whatsapp,
                to=self.to_whatsapp
            )
            print(f"✅ WhatsApp enviado: {mensaje}")
        except Exception as e:
            print(f"❌ Error enviando WhatsApp: {e}")

    def actualizar(self, id_persona, imagen_cuerpo, dentro_del_area):
        ahora = time.time()

        if dentro_del_area:
            if id_persona not in self.personas_en_area:
                mensaje = f"🚶 Persona {id_persona} entró al área."
                #self.enviar_wpp(mensaje)
                self.personas_en_area[id_persona] = ahora
        else:
            if id_persona in self.personas_en_area:
                mensaje = f"👋 Persona {id_persona} salió del área."
                #self.enviar_wpp(mensaje)
                del self.personas_en_area[id_persona]

    def verificar_desapariciones(self):
        ahora = time.time()
        desaparecidos = [
            idp for idp, t in self.personas_en_area.items()
            if ahora - t > self.timeout
        ]
        for idp in desaparecidos:
            mensaje = f"⚠️ Persona {idp} desapareció del área (timeout)."
            #self.enviar_wpp(mensaje)
            del self.personas_en_area[idp]
