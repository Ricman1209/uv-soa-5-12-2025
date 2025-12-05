"""
Servidor SOAP para gestión de Alumnos
Universidad Veracruzana - Plataforma Académica
"""

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

# Modelo de respuesta XML
class Alumno(ComplexModel):
    id = Integer
    matricula = Unicode
    nombre = Unicode
    apellido_paterno = Unicode
    apellido_materno = Unicode
    email = Unicode
    estatus = Unicode


class AlumnosService(ServiceBase):
    
    # ========== CREAR ALUMNO ==========
    @rpc(Unicode, Unicode, Unicode, Unicode, _returns=Unicode)
    def crear_alumno(ctx, matricula, nombre, apellido_paterno, email):
        """Registra un nuevo alumno"""
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
            
        except mysql.connector.IntegrityError:
            return f"Error: La matrícula {matricula} o email ya existe."
        except mysql.connector.Error as err:
            return f"Error de BD: {err}"
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()

    # ========== OBTENER TODOS LOS ALUMNOS ==========
    @rpc(_returns=Array(Alumno))
    def obtener_alumnos(ctx):
        """Obtiene la lista de todos los alumnos"""
        resultados = []
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            
            cursor.execute("SELECT id, matricula, nombre, apellido_paterno, apellido_materno, email, estatus FROM alumnos")
            rows = cursor.fetchall()
            
            for row in rows:
                alumno = Alumno()
                alumno.id = row[0]
                alumno.matricula = row[1]
                alumno.nombre = row[2]
                alumno.apellido_paterno = row[3]
                alumno.apellido_materno = row[4] or ""
                alumno.email = row[5]
                alumno.estatus = row[6]
                resultados.append(alumno)
                
            return resultados
            
        except Exception as e:
            print(f"Error: {e}")
            return []
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()

    # ========== CONSULTAR ALUMNO POR MATRÍCULA ==========
    @rpc(Unicode, _returns=Alumno)
    def consultar_alumno(ctx, matricula):
        """Consulta un alumno por su matrícula"""
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT id, matricula, nombre, apellido_paterno, apellido_materno, email, estatus FROM alumnos WHERE matricula = %s",
                (matricula,)
            )
            row = cursor.fetchone()
            
            if row:
                alumno = Alumno()
                alumno.id = row[0]
                alumno.matricula = row[1]
                alumno.nombre = row[2]
                alumno.apellido_paterno = row[3]
                alumno.apellido_materno = row[4] or ""
                alumno.email = row[5]
                alumno.estatus = row[6]
                return alumno
            return None
            
        except Exception as e:
            print(f"Error: {e}")
            return None
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()

    # ========== EDITAR ALUMNO ==========
    @rpc(Unicode, Unicode, Unicode, Unicode, Unicode, Unicode, _returns=Unicode)
    def editar_alumno(ctx, matricula, nombre, apellido_paterno, apellido_materno, email, estatus):
        """Edita un alumno existente"""
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            
            # Verificar que existe
            cursor.execute("SELECT id FROM alumnos WHERE matricula = %s", (matricula,))
            if not cursor.fetchone():
                return f"Error: No existe alumno con matrícula {matricula}"
            
            query = """
                UPDATE alumnos 
                SET nombre = %s, apellido_paterno = %s, apellido_materno = %s, email = %s, estatus = %s
                WHERE matricula = %s
            """
            cursor.execute(query, (nombre, apellido_paterno, apellido_materno or None, email, estatus, matricula))
            conn.commit()
            
            return f"Éxito: Alumno {matricula} actualizado correctamente."
            
        except mysql.connector.IntegrityError:
            return f"Error: El email ya está en uso."
        except mysql.connector.Error as err:
            return f"Error de BD: {err}"
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()

    # ========== ELIMINAR ALUMNO ==========
    @rpc(Unicode, _returns=Unicode)
    def eliminar_alumno(ctx, matricula):
        """Elimina un alumno por su matrícula"""
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            
            # Verificar que existe
            cursor.execute("SELECT nombre, apellido_paterno FROM alumnos WHERE matricula = %s", (matricula,))
            row = cursor.fetchone()
            
            if not row:
                return f"Error: No existe alumno con matrícula {matricula}"
            
            nombre_completo = f"{row[0]} {row[1]}"
            
            cursor.execute("DELETE FROM alumnos WHERE matricula = %s", (matricula,))
            conn.commit()
            
            return f"Éxito: Alumno {nombre_completo} ({matricula}) eliminado correctamente."
            
        except mysql.connector.Error as err:
            return f"Error de BD: {err}"
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()


# Configuración SOAP
application = Application(
    [AlumnosService], 
    tns='universidad.veracruzana.soap',
    in_protocol=Soap11(validator='lxml'), 
    out_protocol=Soap11()
)

wsgi_application = WsgiApplication(application)

if __name__ == '__main__':
    port = 8000
    print("=" * 55)
    print("  SERVICIO SOAP - GESTIÓN DE ALUMNOS")
    print("=" * 55)
    print(f"  Servidor: http://127.0.0.1:{port}")
    print(f"  WSDL:     http://127.0.0.1:{port}/?wsdl")
    print("\n  Operaciones:")
    print("    - crear_alumno")
    print("    - obtener_alumnos")
    print("    - consultar_alumno")
    print("    - editar_alumno")
    print("    - eliminar_alumno")
    print("=" * 55)
    
    server = make_server('127.0.0.1', port, wsgi_application)
    server.serve_forever()