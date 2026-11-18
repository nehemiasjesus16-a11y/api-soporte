import os
from flask import Flask, jsonify, request
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

# Conexión a la base de datos (se usará la variable de entorno en producción)
DATABASE_URL = os.environ.get("DATABASE_URL", "tu_connection_string_local")


def get_db_connection():
  return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)


@app.route("/", methods=["GET"])
def home():
  return jsonify({
      "status": "API de Soporte Técnico Activa",
      "autor": "Nehemias",
  })


# Consultar todas las solicitudes
@app.route("/api/solicitudes", methods=["GET"])
def get_solicitudes():
  conn = get_db_connection()
  cur = conn.cursor()
  cur.execute("SELECT * FROM solicitudes ORDER BY fecha DESC;")
  solicitudes = cur.fetchall()
  cur.close()
  conn.close()
  return jsonify(solicitudes)


# Registrar nueva solicitud y generar folio
@app.route("/api/solicitudes", methods=["POST"])
def create_solicitud():
  data = request.json
  nombre = data.get("nombre")
  correo = data.get("correo")
  categoria = data.get("categoria")
  prioridad = data.get("prioridad")
  descripcion = data.get("descripcion")

  if not all([nombre, correo, categoria, prioridad, descripcion]):
    return jsonify({"error": "Faltan campos obligatorios"}), 400

  conn = get_db_connection()
  cur = conn.cursor()

  # Generar folio único basado en el total de registros
  cur.execute("SELECT COUNT(*) FROM solicitudes;")
  count = cur.fetchone()["count"] + 1
  folio = f"REQ-2026-{count:03d}"

  cur.execute(
      """
      INSERT INTO solicitudes (folio, nombre, correo, categoria, prioridad, descripcion)
      VALUES (%s, %s, %s, %s, %s, %s)
      RETURNING id, folio, fecha;
      """,
      (folio, nombre, correo, categoria, prioridad, descripcion),
  )
  nueva = cur.fetchone()
  conn.commit()
  cur.close()
  conn.close()

  return (
      jsonify({
          "message": "Solicitud creada exitosamente",
          "folio": nueva["folio"],
          "id": nueva["id"],
      }),
      201,
  )


if __name__ == "__main__":
  app.run(debug=True, port=5000)