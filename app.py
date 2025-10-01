import os
import psycopg
from flask import Flask, request, jsonify
from psycopg.rows import dict_row
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()

CONNINFO = (
    f"host={os.getenv('PG_HOST','127.0.0.1')} "
    f"port={os.getenv('PG_PORT','5432')} "
    f"dbname={os.getenv('PG_DB','try')} "
    f"user={os.getenv('PG_USER','postgres')} "
    f"password={os.getenv('PG_PASSWORD','')}"
)

def get_conn():
    # row_factory=dict_row para obtener dicts en lugar de tuplas
    return psycopg.connect(CONNINFO, row_factory=dict_row)

app = Flask(__name__)

CORS(app)

@app.get("/")
def index():
    return {
        "service": "Students API",
        "endpoints": [
            "/health",
            "/students",
            "/students/<id>"
        ],
        "docs": "Usa Postman o cURL para probar."
    }

@app.get("/health")
def health():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT 1 as ok")
        return {"status": cur.fetchone()["ok"]}

# --------- READ (list) ----------
@app.get("/students")
def list_students():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT id, name, email FROM students ORDER BY id")
        return jsonify(cur.fetchall())

# --------- READ (one) ----------
@app.get("/students/<int:id>")
def get_student(id):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT id, name, email FROM students WHERE id = %s", (id,))
        student = cur.fetchone()
        if not student:
            return {"error": "Student not found"}, 404
        return jsonify(student)

# --------- CREATE ----------
@app.post("/students")
def create_student():
    data = request.get_json(force=True) or {}
    name = data.get("name")
    email = data.get("email")

    if not name or not email:
        return {"error": "name and email are required"}, 400

    with get_conn() as conn, conn.cursor() as cur:
        try:
            cur.execute(
                "INSERT INTO students (name, email) VALUES (%s, %s) RETURNING id, name, email",
                (name, email)
            )
            created = cur.fetchone()
            return jsonify(created), 201
        except psycopg.IntegrityError as e:
            # Por ejemplo, si email es UNIQUE en la tabla
            return {"error": "Integrity error", "detail": str(e)}, 409

# --------- UPDATE (replace) ----------
@app.put("/students/<int:id>")
def update_student(id):
    data = request.get_json(force=True) or {}
    name = data.get("name")
    email = data.get("email")

    if not name or not email:
        return {"error": "name and email are required"}, 400

    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "UPDATE students SET name = %s, email = %s WHERE id = %s RETURNING id, name, email",
            (name, email, id)
        )
        updated = cur.fetchone()
        if not updated:
            return {"error": "Student not found"}, 404
        return jsonify(updated)

# --------- UPDATE (partial) ----------
@app.patch("/students/<int:id>")
def patch_student(id):
    data = request.get_json(force=True) or {}
    fields = []
    values = []

    if "name" in data:
        fields.append("name = %s")
        values.append(data["name"])
    if "email" in data:
        fields.append("email = %s")
        values.append(data["email"])

    if not fields:
        return {"error": "At least one of: name, email"}, 400

    values.append(id)

    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            f"UPDATE students SET {', '.join(fields)} WHERE id = %s RETURNING id, name, email",
            tuple(values)
        )
        updated = cur.fetchone()
        if not updated:
            return {"error": "Student not found"}, 404
        return jsonify(updated)

# --------- DELETE ----------
@app.delete("/students/<int:id>")
def delete_student(id):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("DELETE FROM students WHERE id = %s RETURNING id", (id,))
        deleted = cur.fetchone()
        if not deleted:
            return {"error": "Student not found"}, 404
        return {"status": "deleted", "id": deleted["id"]}

if __name__ == "__main__":
    app.run(debug=True)
