import tkinter as tk
from tkinter import messagebox
import requests
from Cola import Cola
import threading
import time
import uvicorn

# ---------------------- Cola y API ----------------------
cola_misiones = Cola()
URL_BASE = "http://127.0.0.1:8000"
personaje_actual = None

# ---------------------- API ----------------------
def obtener_personajes():
    try:
        response = requests.get(f"{URL_BASE}/personajes")
        return response.json() if response.status_code == 200 else []
    except:
        return []

def crear_personaje_api(data):
    try:
        response = requests.post(f"{URL_BASE}/personajes", json=data)
        return response.status_code == 200
    except:
        return False

def obtener_misiones():
    try:
        response = requests.get(f"{URL_BASE}/misiones")
        if response.status_code == 200:
            return response.json()
        else:
            print("Error al obtener misiones:", response.status_code)
            return []
    except:
        return []

def crear_mision_api(data):
    try:
        response = requests.post(f"{URL_BASE}/misiones", json=data)
        return response.status_code == 200
    except:
        return False

def completar_mision_api(nombre_personaje):
    try:
        response = requests.post(f"{URL_BASE}/personajes/{nombre_personaje}/completar_mision")
        if response.status_code == 200:
            return response.json()
        else:
            print("Error al completar la misión:", response.status_code)
            return None
    except:
        return None

# ---------------------- Misiones ----------------------
def ver_misiones():
    misiones = obtener_misiones()
    ventana = tk.Toplevel()
    ventana.title("Misiones disponibles")
    ventana.geometry("400x400")

    if not misiones:
        tk.Label(ventana, text="No hay misiones disponibles").pack()
        return

    for m in misiones:
        frame = tk.Frame(ventana, bd=2, relief="groove", padx=5, pady=5)
        frame.pack(fill="x", padx=10, pady=5)
        tk.Label(frame, text=f"Nombre: {m['nombre']}", font=("Arial", 10, "bold")).pack(anchor="w")
        tk.Label(frame, text=f"{m['descripcion']}", wraplength=350).pack(anchor="w")
        tk.Button(frame, text="Aceptar", command=lambda m=m: aceptar_mision(m)).pack(anchor="e")

def aceptar_mision(mision):
    cola_misiones.enqueue(mision)
    messagebox.showinfo("Misión Aceptada", f"Has aceptado la misión: {mision['nombre']}")

def completar_mision():
    if cola_misiones.is_empty():
        messagebox.showinfo("Sin misiones", "No hay misiones por completar.")
        return

    mision = cola_misiones.dequeue()
    resultado = completar_mision_api(personaje_actual)
    if resultado:
        messagebox.showinfo("¡Misión completada!", f"{personaje_actual} completó '{mision['nombre']}'\nNivel: {resultado['nivel']}, XP: {resultado['xp']}")

    else:
        messagebox.showerror("Error", "No se pudo completar la misión.")

def ver_mision_actual():
    if cola_misiones.is_empty():
        messagebox.showinfo("Cola Vacía", "No tienes misiones en espera.")
        return
    
    mision = cola_misiones.first()
    messagebox.showinfo("Siguiente Misión", f"{mision['nombre']}: {mision['descripcion']}")

def crear_mision():
    def guardar():
        data = {
            "nombre": entry_nombre.get(),
            "descripcion": entry_descripcion.get()
        }
        if crear_mision_api(data):
            messagebox.showinfo("Misión Creada", f"La misión '{data['nombre']}' ha sido creada.")
            ventana_crear.destroy()
        else:
            messagebox.showerror("Error", "No se pudo crear la misión.")

    ventana_crear = tk.Toplevel()
    ventana_crear.title("Crear Misión")
    ventana_crear.geometry("300x250")

    tk.Label(ventana_crear, text="Nombre de la Misión:").pack()
    entry_nombre = tk.Entry(ventana_crear)
    entry_nombre.pack()

    tk.Label(ventana_crear, text="Descripción de la Misión:").pack()
    entry_descripcion = tk.Entry(ventana_crear)
    entry_descripcion.pack()

    tk.Button(ventana_crear, text="Guardar", command=guardar).pack(pady=10)

def ventana_misiones_opciones():
    ventana = tk.Toplevel()
    ventana.title("Gestionar Misiones")
    ventana.geometry("300x250")
    tk.Button(ventana, text="Ver Misiones", command=ver_misiones).pack(pady=10)
    tk.Button(ventana, text="Crear Misión", command=crear_mision).pack(pady=10)
    tk.Button(ventana, text="Completar Misión Actual", command=completar_mision).pack(pady=10)
    tk.Button(ventana, text="Ver Misión Actual", command=ver_mision_actual).pack(pady=10)

# ---------------------- Personajes ----------------------
def crear_personaje():
    def guardar():
        data = {
            "nombre": entry_nombre.get(),
            "nivel": 1,
            "xp": 0,
            "genero": genero_var.get(),
            "color_piel": color_piel_var.get()
        }
        if crear_personaje_api(data):
            global personaje_actual
            personaje_actual = data["nombre"]
            messagebox.showinfo("Personaje creado", f"{personaje_actual} ha sido creado.")
            ventana_crear.destroy()
            menu_principal()
        else:
            messagebox.showerror("Error", "No se pudo crear el personaje.")

    ventana_crear = tk.Toplevel()
    ventana_crear.title("Crear Personaje")
    ventana_crear.geometry("300x300")

    tk.Label(ventana_crear, text="Nombre:").pack()
    entry_nombre = tk.Entry(ventana_crear)
    entry_nombre.pack()

    tk.Label(ventana_crear, text="Género:").pack()
    genero_var = tk.StringVar(value="Masculino")
    tk.OptionMenu(ventana_crear, genero_var, "Masculino", "Femenino", "Otro").pack()

    tk.Label(ventana_crear, text="Color de piel:").pack()
    color_piel_var = tk.StringVar(value="Claro")
    tk.OptionMenu(ventana_crear, color_piel_var, "Claro", "Oscuro", "Verde", "Azul").pack()

    tk.Button(ventana_crear, text="Guardar", command=guardar).pack(pady=10)

def seleccionar_personaje():
    personajes = obtener_personajes()
    if not personajes:
        messagebox.showinfo("Sin personajes", "No hay personajes creados.")
        return

    ventana = tk.Toplevel()
    ventana.title("Seleccionar Personaje")
    ventana.geometry("300x300")

    for p in personajes:
        frame = tk.Frame(ventana, bd=2, relief="groove", padx=5, pady=5)
        frame.pack(pady=5, fill="x", padx=10)

        info = f"{p['nombre']} - Nivel {p['nivel']} - XP {p['xp']}"
        tk.Label(frame, text=info).pack(anchor="w")

        tk.Button(frame, text="Seleccionar", command=lambda n=p['nombre']: seleccionar_y_abrir_menu(n, ventana)).pack()

def seleccionar_y_abrir_menu(nombre, ventana):
    global personaje_actual
    personaje_actual = nombre
    ventana.destroy()
    messagebox.showinfo("Personaje seleccionado", f"{personaje_actual} ha sido seleccionado.")
    menu_principal()

# ---------------------- Menús ----------------------
def menu_inicio():
    root = tk.Tk()
    root.title("Juego RPG")
    root.geometry("300x250")

    tk.Label(root, text="Bienvenido al RPG", font=("Helvetica", 14)).pack(pady=20)
    tk.Button(root, text="Crear Personaje", width=25, command=crear_personaje).pack(pady=10)
    tk.Button(root, text="Seleccionar Personaje", width=25, command=seleccionar_personaje).pack(pady=10)
    tk.Button(root, text="Salir", width=25, command=root.destroy).pack(pady=10)

    root.mainloop()

def menu_principal():
    ventana = tk.Tk()
    ventana.title("Menú Principal")
    ventana.geometry("300x200")

    tk.Label(ventana, text=f"Hola, {personaje_actual}!", font=("Helvetica", 12)).pack(pady=10)
    tk.Button(ventana, text="Gestionar Misiones", command=ventana_misiones_opciones).pack(pady=10)
    tk.Button(ventana, text="Cerrar sesión", command=ventana.destroy).pack(pady=10)

# ---------------------- FastAPI en segundo plano ----------------------
def iniciar_fastapi():
    def run():
        uvicorn.run("FastApi_Endpoints:app", host="127.0.0.1", port=8000, log_level="info")
    threading.Thread(target=run, daemon=True).start()
    time.sleep(1)

# ---------------------- Main ----------------------
if __name__ == "__main__":
    iniciar_fastapi()
    menu_inicio()
