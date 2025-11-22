import logging
from spyne import Application, rpc, ServiceBase, Integer, Unicode, Array, ComplexModel
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from wsgiref.simple_server import make_server
import mysql.connector

# Configuración de la Base de Datos
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',      
    'password': '201940004',      
    'database': 'universidad_veracruzana_db'
}

#XML de respuesta

class Alumno(ComplexModel):
    id = Integer
    matricula = Unicode
    nombre = Unicode
    apellido_paterno = Unicode
    email = Unicode
    estatus = Unicode

#Lógica

class AlumnosService(ServiceBase):
    
    #Crear un nuevo alumno
    @rpc(Unicode, Unicode, Unicode, Unicode, _returns=Unicode)
    def crear_alumno(ctx, matricula, nombre, apellido_paterno, email):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            
            query = """
                INSERT INTO alumnos (matricula, nombre, apellido_paterno, email)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (matricula, nombre, apellido_paterno, email))
            conn.commit()
            return f"Éxito: Alumno {nombre} con matrícula {matricula} registrado correctamente."
            
        except mysql.connector.Error as err:
            return f"Error de BD: {err}"
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()

          #obtener alumnos
    @rpc(_returns=Array(Alumno))
    def obtener_alumnos(ctx):
        resultados = []
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            
            cursor.execute("SELECT id, matricula, nombre, apellido_paterno, email, estatus FROM alumnos")
            rows = cursor.fetchall()
            
            for row in rows:
                #fila de la BD al objeto Spyne
                alumno = Alumno()
                alumno.id = row[0]
                alumno.matricula = row[1]
                alumno.nombre = row[2]
                alumno.apellido_paterno = row[3]
                alumno.email = row[4]
                alumno.estatus = row[5]
                resultados.append(alumno)
                
            return resultados
            
        except Exception as e:
            print(f"Error: {e}")
            return []
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()

#SOAP
application = Application(
    [AlumnosService], 
    tns='universidad.veracruzana.soap', # Target Namespace
    in_protocol=Soap11(validator='lxml'), 
    out_protocol=Soap11()
)

# Envolver la aplicación en WSGI para poder ejecutarla
wsgi_application = WsgiApplication(application)

if __name__ == '__main__':
    
    port = 8000
    print(f"Servidor SOAP iniciado en http://127.0.0.1:{port}")
    print(f"WSDL disponible en http://127.0.0.1:{port}/?wsdl")
    
    server = make_server('127.0.0.1', port, wsgi_application)
    server.serve_forever()