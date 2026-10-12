import requests

URL_BASE = "http://127.0.0.1:5000"
usuario_actual = None  # Variable local para controlar inicio de sesión

def registrar():
    usuario = input("Nombre de usuario: ")
    contrasena = input("Contraseña: ")
    respuesta = requests.post(f"{URL_BASE}/registro", json={"usuario": usuario, "contraseña": contrasena})
    print(f"\nServidor: {respuesta.json()}\n")

def loguear():
    global usuario_actual 
    usuario = input("Nombre de usuario: ")
    contrasena = input("Contraseña: ")
    respuesta = requests.post(f"{URL_BASE}/login", json={"usuario": usuario, "contraseña": contrasena})
    
    if respuesta.status_code == 200:
        usuario_actual = usuario # Si nos da 200 (ok), guardamosel usuario con el q iniciamos sesion
    
    print(f"\nServidor: {respuesta.json()}\n")

def ver_tareas():
    respuesta = requests.get(f"{URL_BASE}/tareas")
    print("\n--- HTML DE TAREAS ---")
    print(respuesta.text)
    print("----------------------\n")

def agregar_tarea():
    descripcion = input("Escribí tu nueva tarea: ")
    respuesta = requests.post(f"{URL_BASE}/nueva_tarea", json={"descripcion": descripcion})
    print(f"\nServidor: {respuesta.json()}\n")

def menu():
    while True:
        print("\n--- MENÚ PRINCIPAL ---")
        print(f"Estado: {'Logueado como ' + usuario_actual if usuario_actual else 'Desconectado'}")
        print("1. Registrarse")
        print("2. Iniciar sesión")
        print("3. Ver panel de bienvenida")
        print("4. Agregar una nueva tarea")
        print("5. Salir")
        opcion = input("Elegí una opción: ")

        if opcion == "1": 
            registrar()
        elif opcion == "2": 
            loguear()
        elif opcion == "3": 
            if usuario_actual:
                ver_tareas()
            else:
                print("\n[!] ACCESO DENEGADO: Tenés que iniciar sesión primero.\n")
        elif opcion == "4": 
            if usuario_actual:
                agregar_tarea()
            else:
                print("\n[!] ACCESO DENEGADO: Tenés que iniciar sesión primero.\n")
        elif opcion == "5": 
            print("Saliendo...")
            break
        else: 
            print("Opción incorrecta.\n")

if __name__ == "__main__":
    try:
        menu()
    except requests.exceptions.ConnectionError:
        print("\n[Error] Iniciá primero el servidor (servidor.py).")