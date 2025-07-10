import mysql.connector, dbconfig, time

class DBManager:
    def __init__(self, nombre_tabla, estructura_tabla):
        """
        Inicializa la clase y crea la tabla si no existe.

        Parámetros:
            nombre_tabla (str): Nombre de la tabla.
            estructura_tabla (dict): Diccionario con formato {columna: tipo_sql}
                                     El usuario debe incluir 'ID' y 'Fecha_registro'.
        """
        self.nombre_tabla = nombre_tabla
        self.estructura_tabla = estructura_tabla
        self.crear_tabla(nombre_tabla, estructura_tabla)
    
    def guardar_imagen_cuerpo(self, track_id, ruta_cuerpo):
        """
        Guarda la ruta de la imagen del cuerpo asociada a un ID.
        """
        sql = """
        INSERT INTO registro_personas (ID, Imagen_cuerpo)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE Imagen_cuerpo = VALUES(Imagen_cuerpo);
        """
        self._ejecutar_sql(sql, (track_id, ruta_cuerpo), f"Imagen cuerpo ID {track_id}")

    def guardar_imagen_cara(self, track_id, ruta_cara):
        """
        Guarda la ruta de la imagen de la cara asociada a un ID.
        """
        sql = """
        INSERT INTO registro_personas (ID, Imagen_cara)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE Imagen_cara = VALUES(Imagen_cara);
        """
        self._ejecutar_sql(sql, (track_id, ruta_cara), f"Imagen cara ID {track_id}")


    def crear_tabla(self, nombre_tabla, columnas_dict):
        """
        Crea una tabla en la base de datos con el nombre y columnas proporcionadas.

        Parámetros:
            nombre_tabla (str): Nombre de la tabla a crear.
            columnas_dict (dict): Diccionario con los nombres de columnas como claves y los tipos SQL como valores.
        """
        if not columnas_dict:
            print("[ERROR BD] No se proporcionaron columnas para crear la tabla.")
            return

        # Armar la definición SQL de las columnas
        columnas_sql = []
        for columna, tipo in columnas_dict.items():
            columnas_sql.append(f"`{columna}` {tipo}")

        columnas_def = ", ".join(columnas_sql)
        sql = f"CREATE TABLE IF NOT EXISTS `{nombre_tabla}` ({columnas_def});"

        # Ejecutar la sentencia SQL
        self._ejecutar_sql(sql, (), f"Creación de tabla '{nombre_tabla}'")

    def guardar_descripcion(self, track_id, nueva_desc):
        """
        Guarda la descripción completa en la columna 'descripcion' de la base de datos.
        Si el registro con el mismo ID ya existe, se actualiza.
        
        Requiere que la tabla tenga las columnas: 'ID', 'descripcion', 'Fecha_registro'.
        
        Parámetros:
            track_id (int): Identificador único de la persona u objeto.
            nueva_desc (str): Texto completo de la descripción.
        """
        fecha = time.strftime('%Y-%m-%d %H:%M:%S')
        nueva_desc = nueva_desc.strip()

        sql = f"""
        INSERT INTO {self.nombre_tabla} (ID, descripcion, Fecha_registro)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE
            descripcion = VALUES(descripcion),
            Fecha_registro = VALUES(Fecha_registro);
        """
        valores = (track_id, nueva_desc, fecha)

        self._ejecutar_sql(sql, valores, f"Descripción ID {track_id}")


    def _ejecutar_sql(self, sql, params, log_mensaje):
        """
        Ejecuta una consulta SQL de forma segura y gestiona la conexión a la base de datos.

        Parámetros:
            sql (str): Sentencia SQL a ejecutar.
            params (tuple): Parámetros para la consulta SQL.
            log_mensaje (str): Mensaje descriptivo para registrar en logs o consola.
        """
        try:
            conn = dbconfig.conectar()
            cursor = conn.cursor()
            cursor.execute(sql, params)
            conn.commit()
            #print(f"[BD] Guardado correcto: {log_mensaje}")
        except mysql.connector.Error as err:
            print(f"[ERROR BD] {log_mensaje}: {err}")
        finally:
            # Cierre seguro de la conexión
            if conn.is_connected():
                cursor.close()
                conn.close()
