import random
from flask import Flask, render_template, request, session, jsonify
from conexion import db, init_db

app = Flask(__name__)
app.secret_key = "cambia-esta-clave"

FECHA = "to_char(fecha, 'YYYY-MM-DD HH24:MI:SS') AS fecha"


def numero_de(req):
    try:
        return int((req.get_json() or {}).get("numero"))
    except (TypeError, ValueError):
        return None


@app.route("/")
def index():
    return render_template("index.html")


# ---------- Menú 1: Par / Impar ----------
@app.route("/api/par_impar", methods=["GET", "POST"])
def api_par_impar():
    mensaje = None
    with db() as con:
        if request.method == "POST":
            n = numero_de(request)
            if n is None:
                return jsonify(error="Ingresa un número entero válido"), 400
            tipo = "par" if n % 2 == 0 else "impar"
            con.execute("INSERT INTO par_impar (numero, tipo) VALUES (%s, %s)", (n, tipo))
            mensaje = f"El número {n} es {tipo}"
        filas = con.execute(
            f"SELECT id, numero, tipo, {FECHA} FROM par_impar ORDER BY id DESC"
        ).fetchall()
    return jsonify(mensaje=mensaje, filas=filas)


# ---------- Menú 2: Multiplicador ----------
@app.route("/api/multiplicador", methods=["POST"])
def api_multiplicador():
    n = numero_de(request)
    if n is None:
        return jsonify(error="Ingresa un número entero válido"), 400
    with db() as con:
        con.execute("INSERT INTO multiplicador (numero) VALUES (%s)", (n,))
    return jsonify(tabla=[f"{n} x {i} = {n * i}" for i in range(1, 11)])


# ---------- Menú 3: Número secreto ----------
def estado_secreto():
    if "secreto" not in session:
        session["secreto"] = random.randint(1, 100)
        session["intentos"] = []
    return session["intentos"]


def top_ranking():
    with db() as con:
        return con.execute(
            "SELECT nombre, total_intentos, numeros_intentados FROM ranking "
            "ORDER BY total_intentos ASC, id ASC LIMIT 10"
        ).fetchall()


@app.route("/api/secreto/estado")
def api_secreto_estado():
    return jsonify(intentos=estado_secreto(), top=top_ranking())


@app.route("/api/secreto/intentar", methods=["POST"])
def api_secreto_intentar():
    n = numero_de(request)
    intentos = estado_secreto()
    if n is None:
        return jsonify(error="Ingresa un número válido"), 400
    intentos = intentos + [n]
    session["intentos"] = intentos
    if n < session["secreto"]:
        mensaje, gano = "El número secreto es MAYOR", False
    elif n > session["secreto"]:
        mensaje, gano = "El número secreto es MENOR", False
    else:
        mensaje, gano = f"¡Correcto! Lo lograste en {len(intentos)} intentos", True
    return jsonify(mensaje=mensaje, gano=gano, intentos=intentos)


@app.route("/api/secreto/guardar", methods=["POST"])
def api_secreto_guardar():
    nombre = ((request.get_json() or {}).get("nombre") or "").strip()[:60] or "Anónimo"
    intentos = session.get("intentos", [])
    if intentos and intentos[-1] == session.get("secreto"):
        with db() as con:
            con.execute(
                "INSERT INTO ranking (nombre, total_intentos, numeros_intentados) "
                "VALUES (%s, %s, %s)",
                (nombre, len(intentos), ", ".join(map(str, intentos))),
            )
    session.pop("secreto", None)
    session.pop("intentos", None)
    return jsonify(top=top_ranking())


@app.route("/api/secreto/nuevo", methods=["POST"])
def api_secreto_nuevo():
    session.pop("secreto", None)
    session.pop("intentos", None)
    estado_secreto()
    return jsonify(top=top_ranking())


if __name__ == "__main__":
    init_db()
    app.run(debug=True)