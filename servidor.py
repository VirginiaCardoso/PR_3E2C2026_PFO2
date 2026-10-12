import sqlite3
import datetime
from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
DB_FILE = 'tareas.db'
#------------------ BASE DE DATOS ---------------------
def inicializar_db():
    conexion = sqlite3.connect(DB_FILE)
    cursor = conexion.cursor()
    
    # Tabla usuarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            contraseña TEXT NOT NULL
        )
    ''')
    # Tabla tareas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tareas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descripcion TEXT NOT NULL,
            fecha TEXT NOT NULL
        )
    ''')
    # si ya no existen cargo un usuario y tare por defecto para las pruebas
    cursor.execute("SELECT * FROM usuarios WHERE usuario = 'admin'")
    if not cursor.fetchone():
        hash_admin = generate_password_hash('1234')
        fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # Insertar usuario admin
        cursor.execute("INSERT INTO usuarios (usuario, contraseña) VALUES ('admin', ?)", (hash_admin,))
        # Insertar tarea por defecto
        cursor.execute("INSERT INTO tareas (descripcion, fecha) VALUES ('Corregir los trabajos', ?)", (fecha_actual,))
        print("[INFO] Usuario 'admin' (clave: 1234) y tarea por defecto creados.")

    conexion.commit()
    conexion.close()
    print("[OK] Base de datos SQLite inicializada correctamente.")

#------------------ API ---------------------
# Fc para registro de usuarios
@app.route('/registro', methods=['POST'])
def registro():
    datos = request.get_json()
    usuario = datos.get('usuario')
    contrasena_plana = datos.get('contraseña')

    if not usuario or not contrasena_plana:
        return jsonify({"error": "Faltan datos"}), 400

    contrasena_hash = generate_password_hash(contrasena_plana)

    try:
        conexion = sqlite3.connect(DB_FILE)
        cursor = conexion.cursor()
        cursor.execute("INSERT INTO usuarios (usuario, contraseña) VALUES (?, ?)", (usuario, contrasena_hash))
        conexion.commit()
        conexion.close()
        return jsonify({"mensaje": f"Usuario '{usuario}' registrado correctamente"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "El usuario ya existe"}), 400

# Fc para logueo
@app.route('/login', methods=['POST'])
def login():
    datos = request.get_json()
    usuario = datos.get('usuario')
    contrasena_plana = datos.get('contraseña')

    conexion = sqlite3.connect(DB_FILE)
    cursor = conexion.cursor()
    cursor.execute("SELECT contraseña FROM usuarios WHERE usuario = ?", (usuario,))
    fila = cursor.fetchone()
    conexion.close()

    if fila and check_password_hash(fila[0], contrasena_plana):
        return jsonify({"mensaje": "Inicio de sesión exitoso. Acceso concedido."}), 200
    else:
        return jsonify({"error": "Usuario o contraseña incorrectos"}), 401

#Fc para agregar nueva tarea
@app.route('/nueva_tarea', methods=['POST'])
def nueva_tarea():
    datos = request.get_json()
    descripcion = datos.get('descripcion')
    
    if not descripcion:
        return jsonify({"error": "La tarea no puede estar vacía"}), 400
        
    fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    conexion = sqlite3.connect(DB_FILE)
    cursor = conexion.cursor()
    cursor.execute("INSERT INTO tareas (descripcion, fecha) VALUES (?, ?)", (descripcion, fecha_actual))
    conexion.commit()
    conexion.close()
    
    return jsonify({"mensaje": "¡Tarea guardada exitosamente en SQLite!"}), 201

# Fc para listar todas las tareas y mostrarlas junto al html de bienvenida
@app.route('/tareas', methods=['GET'])
def tareas():
    conexion = sqlite3.connect(DB_FILE)
    cursor = conexion.cursor()
    cursor.execute("SELECT descripcion, fecha FROM tareas") # obtengo todas las tareas de la base de datos
    lista_tareas = cursor.fetchall()
    conexion.close()

    items_html = ""
    for tarea in lista_tareas:
        items_html += f"<li><strong>{tarea[0]}</strong> <em>(Creada: {tarea[1]})</em></li>" # todo lo que obtuve lo voy a listar en formato html

    if not items_html:
        items_html = "<li>No hay tareas pendientes.</li>"

    # HMTL cartel bienvenida y tareas
    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head><meta charset="UTF-8"><title>Mis Tareas</title></head>
    <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f9f9f9;">
        <h1 style="color: #2c3e50;">¡Bienvenido a la Gestión de Tareas2!</h1>
        <h3 style="color: #2c3e50;"> PF02 - Cardoso Virginia</h3>
        <p>Has ingresado correctamente. Aquí está tu lista de tareas pendientes sacadas de la base de datos:</p>
        <hr>
        <ul>
            {items_html}
        </ul>
    </body>
    </html>
    """
    return html, 200

if __name__ == '__main__':
    inicializar_db()
    print("Servidor corriendo en http://localhost:5000")
    app.run(port=5000, debug=True)