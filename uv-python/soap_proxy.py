"""
Proxy HTTP para el Servicio SOAP de Alumnos
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import re

app = Flask(__name__)
CORS(app)

SOAP_URL = "http://127.0.0.1:8000"
NS = "universidad.veracruzana.soap"


def soap_call(operacion, params):
    params_xml = "".join(f"<tns:{k}>{v if v else ''}</tns:{k}>" for k, v in params.items())
    
    envelope = f'''<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tns="{NS}">
    <soapenv:Body>
        <tns:{operacion}>{params_xml}</tns:{operacion}>
    </soapenv:Body>
</soapenv:Envelope>'''
    
    try:
        res = requests.post(SOAP_URL, data=envelope.encode('utf-8'), 
                          headers={"Content-Type": "text/xml; charset=utf-8"}, timeout=10)
        return res.text, res.status_code
    except:
        return None, 503


def extract(xml, tag):
    match = re.search(f'<[^>]*{tag}[^>]*>([^<]*)<', xml, re.IGNORECASE)
    return match.group(1).strip() if match else None


def parse_mensaje(xml):
    """Parsea respuestas que son strings simples (crear, editar, eliminar)"""
    if not xml:
        return {"exito": "false", "mensaje": "Sin respuesta"}
    
    # Buscar el Result
    match = re.search(r'Result[^>]*>([^<]+)<', xml)
    if match:
        msg = match.group(1)
        exito = "xito" in msg and "Error" not in msg
        return {"exito": "true" if exito else "false", "mensaje": msg}
    return {"exito": "false", "mensaje": "Error en respuesta"}


def parse_alumno(xml):
    """Parsea respuesta de consultar_alumno"""
    if not xml or "nil" in xml.lower():
        return None
    
    return {
        "id": extract(xml, "id"),
        "matricula": extract(xml, "matricula"),
        "nombre": extract(xml, "nombre"),
        "apellido_paterno": extract(xml, "apellido_paterno"),
        "apellido_materno": extract(xml, "apellido_materno"),
        "email": extract(xml, "email"),
        "estatus": extract(xml, "estatus"),
    }


def parse_lista(xml):
    if not xml:
        return []
    
    alumnos = []
    blocks = re.findall(r'<[^>]*Alumno[^>]*>(.*?)</[^>]*Alumno>', xml, re.DOTALL | re.IGNORECASE)
    
    for block in blocks:
        alumnos.append({
            "id": extract(block, "id"),
            "matricula": extract(block, "matricula"),
            "nombre": extract(block, "nombre"),
            "apellido_paterno": extract(block, "apellido_paterno"),
            "apellido_materno": extract(block, "apellido_materno"),
            "email": extract(block, "email"),
            "estatus": extract(block, "estatus"),
        })
    return alumnos


@app.route('/api/alumnos', methods=['GET'])
def listar():
    xml, status = soap_call("obtener_alumnos", {})
    if status == 503:
        return jsonify([]), 503
    return jsonify(parse_lista(xml))


@app.route('/api/alumnos', methods=['POST'])
def crear():
    d = request.get_json()
    xml, status = soap_call("crear_alumno", {
        "matricula": d.get("matricula", ""),
        "nombre": d.get("nombre", ""),
        "apellido_paterno": d.get("apellido_paterno", ""),
        "email": d.get("email", "")
    })
    if status == 503:
        return jsonify({"exito": "false", "mensaje": "SOAP no disponible"}), 503
    r = parse_mensaje(xml)
    return jsonify(r), 201 if r["exito"] == "true" else 400


@app.route('/api/alumnos/<matricula>', methods=['GET'])
def consultar(matricula):
    xml, status = soap_call("consultar_alumno", {"matricula": matricula})
    if status == 503:
        return jsonify({"exito": "false", "mensaje": "SOAP no disponible"}), 503
    
    alumno = parse_alumno(xml)
    if alumno and alumno.get("matricula"):
        return jsonify({"exito": "true", "mensaje": "Alumno encontrado", "alumno": alumno})
    return jsonify({"exito": "false", "mensaje": f"No existe alumno con matrícula: {matricula}"}), 404


@app.route('/api/alumnos/<matricula>', methods=['PUT'])
def editar(matricula):
    d = request.get_json()
    xml, status = soap_call("editar_alumno", {
        "matricula": matricula,
        "nombre": d.get("nombre", ""),
        "apellido_paterno": d.get("apellido_paterno", ""),
        "apellido_materno": d.get("apellido_materno", ""),
        "email": d.get("email", ""),
        "estatus": d.get("estatus", "ACTIVO")
    })
    if status == 503:
        return jsonify({"exito": "false", "mensaje": "SOAP no disponible"}), 503
    r = parse_mensaje(xml)
    return jsonify(r), 200 if r["exito"] == "true" else 400


@app.route('/api/alumnos/<matricula>', methods=['DELETE'])
def eliminar(matricula):
    xml, status = soap_call("eliminar_alumno", {"matricula": matricula})
    if status == 503:
        return jsonify({"exito": "false", "mensaje": "SOAP no disponible"}), 503
    r = parse_mensaje(xml)
    return jsonify(r), 200 if r["exito"] == "true" else 404


if __name__ == '__main__':
    print("=" * 50)
    print("  PROXY HTTP PARA SOAP - Puerto 5000")
    print("=" * 50)
    app.run(host='127.0.0.1', port=5000, debug=True)