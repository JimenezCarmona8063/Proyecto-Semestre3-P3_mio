# ====================================================
#  SISTEMA DE GESTIÓN DE BIBLIOTECA DIGITAL - GUI
#  Estructuras de datos + Interfaz gráfica con Tkinter
# ====================================================

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime



# ---------------- ESTRUCTURAS DE DATOS -------------

class Cola:
    def __init__(self):
        self._datos = []

    def encolar(self, elem):
        self._datos.append(elem)

    def desencolar(self):
        if self.esta_vacia():
            return None
        return self._datos.pop(0)

    def esta_vacia(self):
        return len(self._datos) == 0

    def __len__(self):
        return len(self._datos)


class NodoLista:
    def __init__(self, dato):
        self.dato = dato
        self.sig = None


class ListaEnlazada:
    """Lista enlazada simple para historial y préstamos."""

    def __init__(self):
        self.cabeza = None
        self.cola = None

    def agregar(self, dato):
        nuevo = NodoLista(dato)
        if self.cabeza is None:
            self.cabeza = self.cola = nuevo
        else:
            self.cola.sig = nuevo
            self.cola = nuevo

    def __iter__(self):
        actual = self.cabeza
        while actual:
            yield actual.dato
            actual = actual.sig


class ColaPrioridad:
    """
    Cola de prioridad implementada como heap mínimo.
    Guarda tuplas (prioridad, contador, elemento).
    """

    def __init__(self):
        self._heap = []
        self._contador = 0

    def _subir(self, idx):
        while idx > 0:
            padre = (idx - 1) // 2
            if self._heap[idx][0] < self._heap[padre][0]:
                self._heap[idx], self._heap[padre] = self._heap[padre], self._heap[idx]
                idx = padre
            else:
                break

    def _bajar(self, idx):
        n = len(self._heap)
        while True:
            izq = 2 * idx + 1
            der = 2 * idx + 2
            menor = idx
            if izq < n and self._heap[izq][0] < self._heap[menor][0]:
                menor = izq
            if der < n and self._heap[der][0] < self._heap[menor][0]:
                menor = der
            if menor == idx:
                break
            self._heap[idx], self._heap[menor] = self._heap[menor], self._heap[idx]
            idx = menor

    def insertar(self, prioridad, elem):
        self._contador += 1
        self._heap.append((prioridad, self._contador, elem))
        self._subir(len(self._heap) - 1)

    def extraer_min(self):
        if self.esta_vacia():
            return None
        minimo = self._heap[0]
        ultimo = self._heap.pop()
        if self._heap:
            self._heap[0] = ultimo
            self._bajar(0)
        return minimo[2]

    def esta_vacia(self):
        return len(self._heap) == 0

    def elementos(self):
        """Devuelve una lista ordenada de elementos (solo para mostrar)."""
        copia = list(self._heap)
        copia.sort(key=lambda x: x[0])
        return [elem for _, _, elem in copia]


# ---------- Algoritmo sobre cadenas (búsqueda) -----


def contiene_patron(texto, patron):
    """Búsqueda ingenua de subcadenas, case-insensitive."""

    texto = texto.lower()
    patron = patron.lower()
    n = len(texto)
    m = len(patron)
    if m == 0:
        return True
    for i in range(n - m + 1):
        j = 0
        while j < m and texto[i + j] == patron[j]:
            j += 1
        if j == m:
            return True
    return False


# --------------- MODELO DEL DOMINIO -----------------


class Libro:
    def __init__(self, libro_id, titulo, autor, generos, portada_nombre=None):
        self.id = libro_id
        self.titulo = titulo
        self.autor = autor
        self.generos = set(generos)
        self.disponible = True
        self.popularidad = 0
        # nombre del archivo de imagen (por defecto: "ID.png")
        self.portada_nombre = portada_nombre or f"{libro_id}.png"


class Usuario:
    def __init__(self, usuario_id, nombre, generos_preferidos):
        self.id = usuario_id
        self.nombre = nombre
        self.generos_preferidos = set(generos_preferidos)
        self.libros_actuales = set()
        self.historial = ListaEnlazada()


class Prestamo:
    def __init__(self, libro_id, usuario_id, fecha_prestamo, fecha_devolucion):
        self.libro_id = libro_id
        self.usuario_id = usuario_id
        self.fecha_prestamo = fecha_prestamo
        self.fecha_devolucion = fecha_devolucion
        self.activo = True


class Reserva:
    def __init__(self, usuario_id, libro_id, prioridad):
        self.usuario_id = usuario_id
        self.libro_id = libro_id
        self.prioridad = prioridad


# ----------------- ALMACENAMIENTO -------------------

libros = {}
usuarios = {}
prestamos_activos = ListaEnlazada()
reservas = ColaPrioridad()
notificaciones = Cola()


def registrar_historial(usuario_id, descripcion):
    """Agrega una entrada descriptiva al historial de un usuario si existe."""

    usuario = usuarios.get(usuario_id)
    if not usuario:
        return
    usuario.historial.agregar(descripcion)


# ---------------- INTERFAZ GRÁFICA ------------------


class BibliotecaApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Gestión de Biblioteca Digital")
        self.geometry("950x600")

        # referencias a imágenes para que no se borren
        self.imagenes_libros = []
        self.demo_cargado = False
        self.registro_completado = False

        self._crear_layout()
        self.cargar_datos_demo()  # llena con libros reales

    # --- layout principal: menú lateral + área central ---
    def _crear_layout(self):
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=4)
        self.rowconfigure(0, weight=1)

        self.frame_menu = ttk.Frame(self, padding=10)
        self.frame_menu.grid(row=0, column=0, sticky="nsw")

        ttk.Label(self.frame_menu, text="Menú Principal", font=("Arial", 12, "bold")).pack(pady=5)

        self.menu_opciones_secundarias = [
            ("Gestión de Libros", self.mostrar_libros),
            ("Gestión de Usuarios", self.mostrar_usuarios),
            ("Préstamos / Devoluciones", self.mostrar_prestamos),
            ("Historial de Usuarios", self.mostrar_historial),
            ("Notificaciones", self.mostrar_notificaciones),
        ]

        self.frame_menu_botones = ttk.Frame(self.frame_menu)
        self.frame_menu_botones.pack(fill="x")
        self._render_menu_buttons()

        ttk.Button(self.frame_menu, text="Salir", command=self.destroy).pack(fill="x", pady=20)

        # Frame donde se cambian las secciones
        self.frame_contenido = ttk.Frame(self, padding=10)
        self.frame_contenido.grid(row=0, column=1, sticky="nsew")
        self.frame_contenido.rowconfigure(1, weight=1)
        self.frame_contenido.columnconfigure(0, weight=1)

        self.mostrar_inicio_registro()

    def _render_menu_buttons(self):
        """Muestra solo el registro hasta que el usuario cree una cuenta."""

        for widget in self.frame_menu_botones.winfo_children():
            widget.destroy()

        ttk.Button(
            self.frame_menu_botones,
            text="Inicio / Registro",
            command=self.mostrar_inicio_registro,
        ).pack(fill="x", pady=3)

        if self.registro_completado:
            for texto, comando in self.menu_opciones_secundarias:
                ttk.Button(self.frame_menu_botones, text=texto, command=comando).pack(
                    fill="x", pady=3
                )
        else:
            ttk.Label(
                self.frame_menu_botones,
                text="Regístrate para desbloquear las demás secciones.",
                wraplength=180,
                justify="left",
            ).pack(fill="x", pady=10)

    def habilitar_menu_principal(self):
        if self.registro_completado:
            return
        self.registro_completado = True
        self._render_menu_buttons()

    # --------- Datos de demo: libros reales ---------

    def cargar_datos_demo(self):
        """Llena la biblioteca con libros, usuarios y movimientos predefinidos."""

        if self.demo_cargado:
            return
        self.demo_cargado = True

        demo_libros = [
            ("1001", "Cien años de soledad", "Gabriel García Márquez", ["Novela", "Realismo mágico"]),
            ("1002", "1984", "George Orwell", ["Distopía", "Política"]),
            ("1003", "El señor de los anillos", "J.R.R. Tolkien", ["Fantasía", "Aventura"]),
            ("1004", "El principito", "Antoine de Saint-Exupéry", ["Infantil", "Filosofía"]),
            ("1005", "Introducción a Algoritmos", "Thomas H. Cormen", ["Computación", "Algoritmos"]),
            ("1006", "Harry Potter y la piedra filosofal", "J.K. Rowling", ["Fantasía"]),
            ("1007", "Fahrenheit 451", "Ray Bradbury", ["Ciencia ficción"]),
            ("1008", "Orgullo y prejuicio", "Jane Austen", ["Romance"]),
            ("1009", "La sombra del viento", "Carlos Ruiz Zafón", ["Misterio", "Novela"]),
            ("1010", "Sapiens", "Yuval Noah Harari", ["Historia", "Ensayo"]),
            ("1011", "Don Quijote de la Mancha", "Miguel de Cervantes", ["Clásico", "Aventura"]),
            ("1012", "La tregua", "Mario Benedetti", ["Romance", "Drama"]),
            ("1013", "La casa de los espíritus", "Isabel Allende", ["Realismo mágico", "Saga familiar"]),
            ("1014", "Breves respuestas a las grandes preguntas", "Stephen Hawking", ["Divulgación", "Ciencia"]),
            ("1015", "Rayuela", "Julio Cortázar", ["Novela", "Experimental"]),
        ]

        for libro_id, titulo, autor, generos in demo_libros:
            libros[libro_id] = Libro(libro_id, titulo, autor, generos)

        self._generar_catalogo_masivo()

        demo_usuarios = [
            ("U001", "Mariana Torres", ["Novela", "Romance"]),
            ("U002", "Ricardo Patiño", ["Fantasía", "Ciencia ficción"]),
            ("U003", "Daniela López", ["Infantil", "Filosofía"]),
            ("U004", "Sofía Méndez", ["Historia", "Ensayo"]),
            ("U005", "Andrés Herrera", ["Computación", "Algoritmos"]),
        ]

        registro_fecha = "01/09/2023"
        for usuario_id, nombre, generos in demo_usuarios:
            usuario = Usuario(usuario_id, nombre, generos)
            usuario.historial.agregar(f"Registro en la plataforma el {registro_fecha}")
            usuarios[usuario_id] = usuario

        historial_extra = {
            "U001": [
                "Solicitó recomendaciones de realismo mágico",
                "Participó en el club de lectura mensual",
            ],
            "U002": [
                "Descargó guía de estudio sobre distopías",
            ],
            "U004": [
                "Asistió a taller de historia latinoamericana",
            ],
        }
        for usuario_id, eventos in historial_extra.items():
            usuario = usuarios.get(usuario_id)
            if not usuario:
                continue
            for evento in eventos:
                usuario.historial.agregar(evento)

        prestamos_demo = [
            ("1001", "U001", "05/09/2023", "19/09/2023"),
            ("1003", "U002", "10/09/2023", "24/09/2023"),
            ("1004", "U003", "12/09/2023", "26/09/2023"),
        ]

        for libro_id, usuario_id, f_p, f_d in prestamos_demo:
            libro = libros.get(libro_id)
            usuario = usuarios.get(usuario_id)
            if not libro or not usuario:
                continue
            prestamo = Prestamo(libro_id, usuario_id, f_p, f_d)
            prestamos_activos.agregar(prestamo)
            libro.disponible = False
            libro.popularidad += 1
            usuario.libros_actuales.add(libro_id)
            usuario.historial.agregar(f"Préstamo de '{libro.titulo}' el {f_p}")

        reservas_demo = [
            (2, Reserva("U004", "1003", 2)),
            (1, Reserva("U005", "1005", 1)),
        ]
        for prioridad, reserva in reservas_demo:
            reservas.insertar(prioridad, reserva)

        notis_iniciales = [
            "Datos de demostración cargados",
            "Hay nuevos talleres disponibles para usuarios registrados",
            "Recuerda devolver tus préstamos a tiempo",
        ]
        for texto in notis_iniciales:
            notificaciones.encolar(texto)

    def _generar_catalogo_masivo(self):
        """Genera automáticamente más de dos mil libros adicionales."""

        generos_genericos = [
            "Tecnología",
            "Historia",
            "Aventura",
            "Educativo",
            "Biografía",
            "Fantasía",
            "Autoayuda",
            "Ciencia",
        ]
        autores_genericos = [
            "Colección Editorial Aurora",
            "Equipo Documental Horizonte",
            "Investigadores del Cono Sur",
            "Red de Escritores Urbanos",
            "Laboratorio de Narrativas Digitales",
            "Archivo Cultural Andino",
        ]

        total_deseado = 2100  # se suman a los libros base para superar 2000 registros
        creados = 0
        idx = 1
        while creados < total_deseado:
            libro_id = f"DL{idx:04d}"
            if libro_id in libros:
                idx += 1
                continue
            titulo = f"Compendio Digital #{idx:04d}"
            autor = autores_genericos[(idx - 1) % len(autores_genericos)]
            genero = generos_genericos[(idx - 1) % len(generos_genericos)]
            libros[libro_id] = Libro(libro_id, titulo, autor, [genero])
            creados += 1
            idx += 1

    # ---------------- utilidades GUI ----------------

    def limpiar_contenido(self):
        for widget in self.frame_contenido.winfo_children():
            widget.destroy()

    def crear_area_resultados(self, row=1):
        txt = tk.Text(self.frame_contenido, height=18)
        txt.grid(row=row, column=0, sticky="nsew", pady=10)
        txt.config(state="disabled")
        return txt

    def escribir_en_texto(self, widget_text, texto):
        widget_text.config(state="normal")
        widget_text.delete("1.0", tk.END)
        widget_text.insert(tk.END, texto)
        widget_text.config(state="disabled")

    # --------- Secciones de la interfaz ---------

    def mostrar_inicio_registro(self):
        """Pantalla inicial: introduce un menú con formulario de registro."""

        self.limpiar_contenido()
        ttk.Label(
            self.frame_contenido,
            text="MENÚ PRINCIPAL Y REGISTRO",
            font=("Arial", 16, "bold"),
        ).grid(row=0, column=0, sticky="w", pady=10)

        frm = ttk.Frame(self.frame_contenido)
        frm.grid(row=1, column=0, sticky="nwe")

        ttk.Label(frm, text="ID Usuario:").grid(row=0, column=0, sticky="e")
        ttk.Label(frm, text="Nombre completo:").grid(row=1, column=0, sticky="e")
        ttk.Label(frm, text="Géneros preferidos (coma):").grid(row=2, column=0, sticky="e")

        id_entry = ttk.Entry(frm, width=15)
        nombre_entry = ttk.Entry(frm, width=30)
        generos_entry = ttk.Entry(frm, width=40)

        id_entry.grid(row=0, column=1, padx=5, pady=2, sticky="w")
        nombre_entry.grid(row=1, column=1, padx=5, pady=2, sticky="w")
        generos_entry.grid(row=2, column=1, padx=5, pady=2, sticky="w")

        txt = self.crear_area_resultados(row=2)

        def mostrar_info_bienvenida(extra=""):
            texto = (
                "Bienvenido al sistema integral de biblioteca digital.\n\n"
                "Desde este menú puedes registrarte y luego navegar a:\n"
                "- Gestión de Libros (registrar, buscar y eliminar títulos)\n"
                "- Gestión de Usuarios (administrar perfiles completos)\n"
                "- Préstamos / Devoluciones (movimientos con fechas)\n"
                "- Historial (acciones detalladas de cada usuario)\n"
                "- Notificaciones (seguimiento de altas, bajas y movimientos)\n\n"
                f"Usuarios registrados: {len(usuarios)} | Libros cargados: {len(libros)}\n"
            )
            if not self.registro_completado:
                texto += (
                    "\n⚠️ Las demás secciones permanecerán ocultas hasta que completes un registro."
                )
            if extra:
                texto += "\n" + extra
            self.escribir_en_texto(txt, texto)

        def registrar_usuario_inicio():
            usuario_id = id_entry.get().strip()
            if not usuario_id:
                messagebox.showwarning("Error", "El ID de usuario es obligatorio.")
                return
            if usuario_id in usuarios:
                messagebox.showwarning("Error", "Ya existe un usuario con ese ID.")
                return
            nombre = nombre_entry.get().strip()
            if not nombre:
                messagebox.showwarning("Error", "El nombre es obligatorio.")
                return
            generos = [g.strip() for g in generos_entry.get().split(",") if g.strip()]
            nuevo_usuario = Usuario(usuario_id, nombre, generos)
            fecha_registro = datetime.now().strftime("%d/%m/%Y")
            nuevo_usuario.historial.agregar(f"Registro inicial desde el menú principal el {fecha_registro}")
            usuarios[usuario_id] = nuevo_usuario
            notificaciones.encolar(f"Nuevo registro de usuario: {nombre}")
            messagebox.showinfo("Registro", "Usuario creado correctamente.")
            mostrar_info_bienvenida(f"Último registro: {nombre} ({usuario_id})")
            self.habilitar_menu_principal()
            id_entry.delete(0, tk.END)
            nombre_entry.delete(0, tk.END)
            generos_entry.delete(0, tk.END)

        botones = ttk.Frame(frm)
        botones.grid(row=3, column=0, columnspan=2, pady=5)

        ttk.Button(botones, text="Registrar usuario", command=registrar_usuario_inicio).grid(
            row=0, column=0, padx=5
        )
        ttk.Button(
            botones,
            text="Limpiar",
            command=lambda: [id_entry.delete(0, tk.END), nombre_entry.delete(0, tk.END), generos_entry.delete(0, tk.END)],
        ).grid(row=0, column=1, padx=5)

        mostrar_info_bienvenida()

    # ------------------ Libros -------------------

    def mostrar_libros(self):
        self.limpiar_contenido()
        ttk.Label(self.frame_contenido, text="Gestión de Libros", font=("Arial", 14, "bold")).grid(
            row=0, column=0, sticky="w"
        )

        frm = ttk.Frame(self.frame_contenido)
        frm.grid(row=1, column=0, sticky="nwe")

        ttk.Label(frm, text="ID Libro:").grid(row=0, column=0, sticky="e")
        ttk.Label(frm, text="Título:").grid(row=1, column=0, sticky="e")
        ttk.Label(frm, text="Autor:").grid(row=2, column=0, sticky="e")
        ttk.Label(frm, text="Géneros (coma):").grid(row=3, column=0, sticky="e")
        ttk.Label(frm, text="ID Usuario actividad:").grid(row=4, column=0, sticky="e")
        ttk.Label(frm, text="Texto de búsqueda:").grid(row=5, column=0, sticky="e")

        id_entry = ttk.Entry(frm, width=15)
        titulo_entry = ttk.Entry(frm, width=35)
        autor_entry = ttk.Entry(frm, width=25)
        generos_entry = ttk.Entry(frm, width=35)
        usuario_accion_entry = ttk.Entry(frm, width=15)
        busqueda_entry = ttk.Entry(frm, width=35)

        id_entry.grid(row=0, column=1, padx=5, pady=2, sticky="w")
        titulo_entry.grid(row=1, column=1, padx=5, pady=2, sticky="w")
        autor_entry.grid(row=2, column=1, padx=5, pady=2, sticky="w")
        generos_entry.grid(row=3, column=1, padx=5, pady=2, sticky="w")
        usuario_accion_entry.grid(row=4, column=1, padx=5, pady=2, sticky="w")
        busqueda_entry.grid(row=5, column=1, padx=5, pady=2, sticky="w")

        txt = self.crear_area_resultados()

        def registrar():
            libro_id = id_entry.get().strip()
            if not libro_id:
                messagebox.showwarning("Error", "ID obligatorio.")
                return
            if libro_id in libros:
                messagebox.showwarning("Error", "Ya existe un libro con ese ID.")
                return
            titulo = titulo_entry.get().strip()
            autor = autor_entry.get().strip()
            generos = [g.strip() for g in generos_entry.get().split(",") if g.strip()]
            libros[libro_id] = Libro(libro_id, titulo, autor, generos)
            notificaciones.encolar(f"Nuevo libro registrado: {titulo}")
            usuario_hist = usuario_accion_entry.get().strip()
            if usuario_hist:
                registrar_historial(
                    usuario_hist,
                    f"Agregó el libro '{titulo}' (ID {libro_id}) el {datetime.now().strftime('%d/%m/%Y')}",
                )
            messagebox.showinfo("OK", "Libro registrado.")
            self.listar_libros_texto(txt)

        def listar():
            self.listar_libros_texto(txt)

        def buscar():
            patron = busqueda_entry.get().strip()
            resultados = []
            for libro in libros.values():
                texto = f"{libro.titulo} {libro.autor} {' '.join(libro.generos)}"
                if contiene_patron(texto, patron):
                    resultados.append(libro)
            if not resultados:
                self.escribir_en_texto(txt, "No se encontraron libros.")
            else:
                s = "Resultados de búsqueda:\n\n"
                for l in resultados:
                    disp = "Disponible" if l.disponible else "Prestado"
                    s += f"[{l.id}] {l.titulo} - {l.autor} | {disp}\n"
                self.escribir_en_texto(txt, s)
            usuario_hist = usuario_accion_entry.get().strip()
            if usuario_hist and patron:
                registrar_historial(
                    usuario_hist,
                    f"Buscó '{patron}' en la gestión de libros y obtuvo {len(resultados)} resultado(s)",
                )

        def eliminar():
            libro_id = id_entry.get().strip()
            if libro_id in libros:
                eliminado = libros[libro_id]
                del libros[libro_id]
                notificaciones.encolar(f"Libro eliminado: {libro_id}")
                usuario_hist = usuario_accion_entry.get().strip()
                if usuario_hist:
                    registrar_historial(
                        usuario_hist,
                        f"Retiró el libro '{eliminado.titulo}' (ID {libro_id}) del catálogo",
                    )
                messagebox.showinfo("OK", "Libro eliminado.")
                self.listar_libros_texto(txt)
            else:
                messagebox.showwarning("Error", "Libro no encontrado.")

        def ver_galeria():
            self.mostrar_galeria_portadas()

        botones = ttk.Frame(frm)
        botones.grid(row=6, column=0, columnspan=2, pady=5)

        ttk.Button(botones, text="Registrar", command=registrar).grid(row=0, column=0, padx=5)
        ttk.Button(botones, text="Listar todos", command=listar).grid(row=0, column=1, padx=5)
        ttk.Button(botones, text="Buscar libro", command=buscar).grid(row=0, column=2, padx=5)
        ttk.Button(botones, text="Eliminar por ID", command=eliminar).grid(row=0, column=3, padx=5)
        ttk.Button(botones, text="Galería de portadas", command=ver_galeria).grid(row=0, column=4, padx=5)

        self.listar_libros_texto(txt)

    def listar_libros_texto(self, txt):
        if not libros:
            self.escribir_en_texto(txt, "No hay libros registrados.")
            return
        s = "Mapa de Libros:\n\n"
        for l in libros.values():
            disp = "Disponible" if l.disponible else "Prestado"
            s += f"[{l.id}] {l.titulo} - {l.autor}\n"
            s += f"   Géneros: {', '.join(l.generos)} | {disp}\n"
        self.escribir_en_texto(txt, s)

    def mostrar_galeria_portadas(self):
        """Ventana con portadas (imagen + nombre debajo)."""

        win = tk.Toplevel(self)
        win.title("Galería de libros")
        self.imagenes_libros = []  # reset

        cols = 4
        i = 0
        for libro in libros.values():
            fila = i // cols
            col = i % cols
            marco = ttk.Frame(win, padding=5)
            marco.grid(row=fila, column=col)

            # intenta cargar imagen con el nombre indicado
            try:
                img = tk.PhotoImage(file=libro.portada_nombre)
                # si la imagen es grande, se reduce un poco
                img = img.subsample(3, 3)
                self.imagenes_libros.append(img)  # guardar referencia
                lbl_img = ttk.Label(marco, image=img)
            except Exception:
                lbl_img = ttk.Label(marco, text="(sin imagen)", width=15)

            lbl_img.pack()
            ttk.Label(marco, text=f"{libro.titulo}\n({libro.autor})", wraplength=120, justify="center").pack()
            i += 1

    # ------------------ Usuarios -------------------

    def mostrar_usuarios(self):
        self.limpiar_contenido()
        ttk.Label(self.frame_contenido, text="Gestión de Usuarios", font=("Arial", 14, "bold")).grid(
            row=0, column=0, sticky="w"
        )

        frm = ttk.Frame(self.frame_contenido)
        frm.grid(row=1, column=0, sticky="nwe")

        ttk.Label(frm, text="ID Usuario:").grid(row=0, column=0, sticky="e")
        ttk.Label(frm, text="Nombre:").grid(row=1, column=0, sticky="e")
        ttk.Label(frm, text="Géneros preferidos (coma):").grid(row=2, column=0, sticky="e")

        id_entry = ttk.Entry(frm, width=15)
        nombre_entry = ttk.Entry(frm, width=25)
        generos_entry = ttk.Entry(frm, width=35)

        id_entry.grid(row=0, column=1, padx=5, pady=2, sticky="w")
        nombre_entry.grid(row=1, column=1, padx=5, pady=2, sticky="w")
        generos_entry.grid(row=2, column=1, padx=5, pady=2, sticky="w")

        txt = self.crear_area_resultados()

        def registrar():
            usuario_id = id_entry.get().strip()
            if not usuario_id:
                messagebox.showwarning("Error", "ID obligatorio.")
                return
            if usuario_id in usuarios:
                messagebox.showwarning("Error", "Ya existe un usuario con ese ID.")
                return
            nombre = nombre_entry.get().strip()
            generos = [g.strip() for g in generos_entry.get().split(",") if g.strip()]
            usuarios[usuario_id] = Usuario(usuario_id, nombre, generos)
            registrar_historial(usuario_id, f"Usuario registrado el {datetime.now().strftime('%d/%m/%Y')}")
            notificaciones.encolar(f"Nuevo usuario registrado: {nombre}")
            messagebox.showinfo("OK", "Usuario registrado.")
            self.listar_usuarios_texto(txt)

        def listar():
            self.listar_usuarios_texto(txt)

        def buscar():
            patron = nombre_entry.get().strip()
            resultados = []
            for u in usuarios.values():
                texto = f"{u.id} {u.nombre}"
                if contiene_patron(texto, patron):
                    resultados.append(u)
            if not resultados:
                self.escribir_en_texto(txt, "No se encontraron usuarios.")
            else:
                s = "Resultados de búsqueda:\n\n"
                for u in resultados:
                    s += f"[{u.id}] {u.nombre} | Libros actuales: {len(u.libros_actuales)}\n"
                self.escribir_en_texto(txt, s)

        def eliminar():
            usuario_id = id_entry.get().strip()
            if usuario_id in usuarios:
                del usuarios[usuario_id]
                notificaciones.encolar(f"Usuario eliminado: {usuario_id}")
                messagebox.showinfo("OK", "Usuario eliminado.")
                self.listar_usuarios_texto(txt)
            else:
                messagebox.showwarning("Error", "Usuario no encontrado.")

        botones = ttk.Frame(frm)
        botones.grid(row=3, column=0, columnspan=2, pady=5)

        ttk.Button(botones, text="Registrar", command=registrar).grid(row=0, column=0, padx=5)
        ttk.Button(botones, text="Listar todos", command=listar).grid(row=0, column=1, padx=5)
        ttk.Button(botones, text="Buscar", command=buscar).grid(row=0, column=2, padx=5)
        ttk.Button(botones, text="Eliminar por ID", command=eliminar).grid(row=0, column=3, padx=5)

        self.listar_usuarios_texto(txt)

    def listar_usuarios_texto(self, txt):
        if not usuarios:
            self.escribir_en_texto(txt, "No hay usuarios registrados.")
            return
        s = "Mapa de Usuarios:\n\n"
        for u in usuarios.values():
            s += f"[{u.id}] {u.nombre}\n"
            s += f"   Libros actuales: {u.libros_actuales}\n"
            s += f"   Géneros preferidos: {', '.join(u.generos_preferidos)}\n"
        self.escribir_en_texto(txt, s)

    # -------------- Préstamos / Devoluciones --------

    def mostrar_prestamos(self):
        self.limpiar_contenido()
        ttk.Label(self.frame_contenido, text="Préstamos y Devoluciones", font=("Arial", 14, "bold")).grid(
            row=0, column=0, sticky="w"
        )

        frm = ttk.Frame(self.frame_contenido)
        frm.grid(row=1, column=0, sticky="nwe")

        ttk.Label(frm, text="ID Usuario:").grid(row=0, column=0, sticky="e")
        ttk.Label(frm, text="ID Libro:").grid(row=1, column=0, sticky="e")
        ttk.Label(frm, text="F. Préstamo (dd/mm/aaaa):").grid(row=2, column=0, sticky="e")
        ttk.Label(frm, text="F. Devolución (dd/mm/aaaa):").grid(row=3, column=0, sticky="e")

        u_entry = ttk.Entry(frm, width=15)
        l_entry = ttk.Entry(frm, width=15)
        fp_entry = ttk.Entry(frm, width=15)
        fd_entry = ttk.Entry(frm, width=15)

        u_entry.grid(row=0, column=1, padx=5, pady=2, sticky="w")
        l_entry.grid(row=1, column=1, padx=5, pady=2, sticky="w")
        fp_entry.grid(row=2, column=1, padx=5, pady=2, sticky="w")
        fd_entry.grid(row=3, column=1, padx=5, pady=2, sticky="w")

        txt = self.crear_area_resultados()

        def registrar_prestamo():
            usuario_id = u_entry.get().strip()
            libro_id = l_entry.get().strip()
            if usuario_id not in usuarios:
                messagebox.showwarning("Error", "Usuario no encontrado.")
                return
            if libro_id not in libros:
                messagebox.showwarning("Error", "Libro no encontrado.")
                return
            libro = libros[libro_id]
            usuario = usuarios[usuario_id]

            if not libro.disponible:
                # si no está disponible, se crea una reserva en la cola de prioridad
                try:
                    prioridad = int(fp_entry.get() or "10")
                except ValueError:
                    prioridad = 10
                reservas.insertar(prioridad, Reserva(usuario_id, libro_id, prioridad))
                notificaciones.encolar(f"Reserva creada: {usuario.nombre} -> {libro.titulo}")
                messagebox.showinfo("Reserva", "El libro no está disponible. Se creó una reserva.")
                self.mostrar_reservas_texto(txt)
                return

            fecha_p = fp_entry.get().strip() or datetime.now().strftime("%d/%m/%Y")
            fecha_d = fd_entry.get().strip() or fecha_p
            prestamo = Prestamo(libro_id, usuario_id, fecha_p, fecha_d)
            prestamos_activos.agregar(prestamo)
            libro.disponible = False
            libro.popularidad += 1
            usuario.libros_actuales.add(libro_id)
            usuario.historial.agregar(f"Préstamo de '{libro.titulo}' el {fecha_p}")
            notificaciones.encolar(f"Préstamo registrado: {usuario.nombre} tomó '{libro.titulo}'")
            messagebox.showinfo("OK", "Préstamo registrado.")
            self.mostrar_prestamos_texto(txt)

        def devolver():
            usuario_id = u_entry.get().strip()
            libro_id = l_entry.get().strip()
            libro = libros.get(libro_id)
            usuario = usuarios.get(usuario_id)
            if not libro or not usuario:
                messagebox.showwarning("Error", "Libro o usuario no encontrado.")
                return

            encontrado = False
            for p in prestamos_activos:
                if p.activo and p.libro_id == libro_id and p.usuario_id == usuario_id:
                    p.activo = False
                    encontrado = True
                    break
            if not encontrado:
                messagebox.showwarning("Error", "No hay préstamo activo con esos datos.")
                return

            libro.disponible = True
            if libro_id in usuario.libros_actuales:
                usuario.libros_actuales.remove(libro_id)
            fecha_hoy = datetime.now().strftime("%d/%m/%Y")
            usuario.historial.agregar(f"Devolución de '{libro.titulo}' el {fecha_hoy}")
            notificaciones.encolar(f"Devolución registrada: {usuario.nombre} entregó '{libro.titulo}'")

            # atender una reserva si existe
            if not reservas.esta_vacia():
                r = reservas.extraer_min()
                u_res = usuarios.get(r.usuario_id)
                if u_res:
                    notificaciones.encolar(f"Libro '{libro.titulo}' listo para reserva de {u_res.nombre}")
            messagebox.showinfo("OK", "Devolución registrada.")
            self.mostrar_prestamos_texto(txt)

        def ver_prestamos():
            self.mostrar_prestamos_texto(txt)

        def ver_reservas():
            self.mostrar_reservas_texto(txt)

        botones = ttk.Frame(frm)
        botones.grid(row=4, column=0, columnspan=2, pady=5)

        ttk.Button(botones, text="Registrar préstamo", command=registrar_prestamo).grid(row=0, column=0, padx=5)
        ttk.Button(botones, text="Registrar devolución", command=devolver).grid(row=0, column=1, padx=5)
        ttk.Button(botones, text="Ver préstamos activos", command=ver_prestamos).grid(row=0, column=2, padx=5)
        ttk.Button(botones, text="Ver reservas (cola prioridad)", command=ver_reservas).grid(row=0, column=3, padx=5)

        self.mostrar_prestamos_texto(txt)

    def mostrar_prestamos_texto(self, txt):
        vacio = True
        s = "Préstamos activos:\n\n"
        for p in prestamos_activos:
            if not p.activo:
                continue
            vacio = False
            libro = libros.get(p.libro_id)
            usuario = usuarios.get(p.usuario_id)
            titulo = libro.titulo if libro else p.libro_id
            autor = libro.autor if libro else "Autor no registrado"
            nombre_usuario = usuario.nombre if usuario else p.usuario_id
            s += f"Usuario: {nombre_usuario} (ID {p.usuario_id})\n"
            s += f"Libro: {titulo} — {autor}\n"
            s += f"Fechas: Préstamo {p.fecha_prestamo} | Devolución {p.fecha_devolucion}\n"
            s += "-" * 60 + "\n"
        if vacio:
            s = "No hay préstamos activos."
        self.escribir_en_texto(txt, s)

    def mostrar_reservas_texto(self, txt):
        if reservas.esta_vacia():
            self.escribir_en_texto(txt, "No hay reservas en la cola de prioridad.")
            return
        s = "Reservas (cola de prioridad):\n\n"
        for r in reservas.elementos():
            u = usuarios.get(r.usuario_id)
            l = libros.get(r.libro_id)
            s += f"Prioridad {r.prioridad} -> "
            s += f"Usuario: {u.nombre if u else r.usuario_id} | "
            s += f"Libro: {l.titulo if l else r.libro_id}\n"
        self.escribir_en_texto(txt, s)

    # ---------------- Historial -----------------------

    def mostrar_historial(self):
        self.limpiar_contenido()
        ttk.Label(self.frame_contenido, text="Historial de Usuarios", font=("Arial", 14, "bold")).grid(
            row=0, column=0, sticky="w"
        )

        frm = ttk.Frame(self.frame_contenido)
        frm.grid(row=1, column=0, sticky="nwe")

        ttk.Label(frm, text="ID Usuario:").grid(row=0, column=0, sticky="e")
        id_entry = ttk.Entry(frm, width=15)
        id_entry.grid(row=0, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(frm, text="Actividad manual:").grid(row=1, column=0, sticky="e")
        act_entry = ttk.Entry(frm, width=40)
        act_entry.grid(row=1, column=1, padx=5, pady=2, sticky="w")

        txt = self.crear_area_resultados()

        def ver():
            usuario_id = id_entry.get().strip()
            u = usuarios.get(usuario_id)
            if not u:
                messagebox.showwarning("Error", "Usuario no encontrado.")
                return
            s = f"Historial de {u.nombre} (ID {u.id}):\n\n"
            vacio = True
            for ev in u.historial:
                s += "- " + ev + "\n"
                vacio = False
            if vacio:
                s += "No hay actividades registradas."
            self.escribir_en_texto(txt, s)

        def agregar():
            usuario_id = id_entry.get().strip()
            u = usuarios.get(usuario_id)
            if not u:
                messagebox.showwarning("Error", "Usuario no encontrado.")
                return
            actividad = act_entry.get().strip()
            if not actividad:
                messagebox.showwarning("Error", "Escriba una actividad.")
                return
            u.historial.agregar(actividad)
            notificaciones.encolar(f"Actividad añadida al historial de {u.nombre}")
            messagebox.showinfo("OK", "Actividad agregada.")
            ver()

        botones = ttk.Frame(frm)
        botones.grid(row=2, column=0, columnspan=2, pady=5)

        ttk.Button(botones, text="Ver historial", command=ver).grid(row=0, column=0, padx=5)
        ttk.Button(botones, text="Agregar actividad", command=agregar).grid(row=0, column=1, padx=5)

    # ---------------- Notificaciones ------------------

    def mostrar_notificaciones(self):
        self.limpiar_contenido()
        ttk.Label(self.frame_contenido, text="Notificaciones (Cola FIFO)", font=("Arial", 14, "bold")).grid(
            row=0, column=0, sticky="w"
        )

        txt = self.crear_area_resultados()

        if notificaciones.esta_vacia():
            self.escribir_en_texto(txt, "No hay notificaciones.")
        else:
            s = "Notificaciones en orden de llegada:\n\n"
            while not notificaciones.esta_vacia():
                s += "- " + notificaciones.desencolar() + "\n"
            self.escribir_en_texto(txt, s)

# -------------------- MAIN -------------------------


if __name__ == "__main__":
    app = BibliotecaApp()
    app.mainloop()
