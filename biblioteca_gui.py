# ====================================================
#  SISTEMA DE GESTIÓN DE BIBLIOTECA DIGITAL - GUI
#  Estructuras de datos + Interfaz gráfica con Tkinter
# ====================================================

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime



# ---------------- ESTRUCTURAS DE DATOS -------------


class Node:
    def __init__(self, data):
        self.data = data
        self.next = None


class Queue:
    def __init__(self, data=None):
        self.front = None
        self.rear = None
        self.size = 0

        if data:
            try:
                for d in data:
                    self.enqueue(d)
            except Exception:
                self.enqueue(data)

    def enqueue(self, data):
        new_node = Node(data)
        if self.is_empty():
            self.front = self.rear = new_node
        else:
            self.rear.next = new_node
            self.rear = new_node
        self.size += 1

    def dequeue(self):
        if self.is_empty():
            return None

        data_out = self.front.data
        self.front = self.front.next
        if not self.front:
            self.rear = None

        self.size -= 1
        return data_out

    def peek(self):
        if self.is_empty():
            return None
        return self.front.data

    def length(self):
        return self.size

    def is_empty(self):
        return self.rear is None

    def __repr__(self):
        if self.is_empty():
            return ""
        current = self.front
        values = []
        while current:
            values.append(str(current.data))
            current = current.next
        return ", ".join(values)


class LinkedList:
    def __init__(self):
        self.head = None
        self.tail = None

    def agregar(self, dato):
        new_node = Node(dato)
        if self.head is None:
            self.head = self.tail = new_node
        else:
            self.tail.next = new_node
            self.tail = new_node

    def is_empty(self):
        return self.head is None

    def __iter__(self):
        current = self.head
        while current:
            yield current.data
            current = current.next


class QHeapNode:
    def __init__(self, key, data):
        self.key = key
        self.data = data


class QHeap:
    def __init__(self, is_min_heap=True):
        self.nodes = []
        self.is_min_heap = is_min_heap

    def is_empty(self):
        return len(self.nodes) == 0

    def compare(self, a, b):
        return a < b if self.is_min_heap else a > b

    def _bubble_up(self, index):
        parent = (index - 1) // 2
        while index > 0 and self.compare(self.nodes[index].key, self.nodes[parent].key):
            self.nodes[index], self.nodes[parent] = self.nodes[parent], self.nodes[index]
            index = parent
            parent = (index - 1) // 2

    def _heapify(self, index):
        size = len(self.nodes)
        smallest = index
        left = 2 * index + 1
        right = 2 * index + 2

        if left < size and self.compare(self.nodes[left].key, self.nodes[smallest].key):
            smallest = left
        if right < size and self.compare(self.nodes[right].key, self.nodes[smallest].key):
            smallest = right

        if smallest != index:
            self.nodes[index], self.nodes[smallest] = self.nodes[smallest], self.nodes[index]
            self._heapify(smallest)

    def enqueue(self, key, data):
        new_node = QHeapNode(key, data)
        self.nodes.append(new_node)
        self._bubble_up(len(self.nodes) - 1)

    def dequeue(self):
        if self.is_empty():
            return None

        root = self.nodes[0]
        last = self.nodes.pop()
        if not self.is_empty():
            self.nodes[0] = last
            self._heapify(0)
        return root

    def elements_sorted(self):
        return sorted(self.nodes, key=lambda n: n.key)


class Cola:
    def __init__(self):
        self._cola = Queue()

    def encolar(self, elem):
        self._cola.enqueue(elem)

    def desencolar(self):
        return self._cola.dequeue()

    def esta_vacia(self):
        return self._cola.is_empty()

    def __len__(self):
        return self._cola.length()


class ListaEnlazada(LinkedList):
    """Lista enlazada simple para historial y préstamos."""

    def __init__(self):
        super().__init__()


class ColaPrioridad:
    """Cola de prioridad basada en heap mínimo."""

    def __init__(self):
        self._heap = QHeap(is_min_heap=True)
        self._contador = 0

    def insertar(self, prioridad, elem):
        self._contador += 1
        self._heap.enqueue((prioridad, self._contador), elem)

    def extraer_min(self):
        nodo = self._heap.dequeue()
        if not nodo:
            return None
        return nodo.data

    def esta_vacia(self):
        return self._heap.is_empty()

    def elementos(self):
        return [nodo.data for nodo in self._heap.elements_sorted()]


# =======================================
#     ESTRUCTURA DE DATOS: MAP
# =======================================


class Map:
    def __init__(self):
        self.__items = []

    def put(self, key, value):
        for i, (k, v) in enumerate(self.__items):
            if k == key:
                self.__items[i] = (key, value)
                return
        self.__items.append((key, value))

    def get(self, key):
        for k, v in self.__items:
            if k == key:
                return v
        raise KeyError(f"key {key} not found")

    def remove(self, key):
        for i, (k, v) in enumerate(self.__items):
            if k == key:
                del self.__items[i]
                return
        raise KeyError(f"key {key} not found")

    def __contains__(self, key):
        return any(k == key for k, v in self.__items)

    def __iter__(self):
        for k, v in self.__items:
            yield k, v

    def __len__(self):
        return len(self.__items)

    def clear(self):
        self.__items = []

    def keys(self):
        return [k for k, v in self.__items]

    def values(self):
        return [v for k, v in self.__items]

    def items(self):
        return [(k, v) for k, v in self.__items]

    def __str__(self):
        return "{" + ", ".join(f"{k}: {v}" for k, v in self.__items) + "}"


# =======================================
#     ESTRUCTURA DE DATOS: HASH MAP
# =======================================


class HashMap:
    def __init__(self, capacity=10, items=None):
        self.__capacity = capacity
        self.__size = 0
        self.__buckets = [[] for _ in range(self.__capacity)]

        if items:
            for k, v in items:
                self.put(k, v)

    def __hash(self, key, base=None):
        if base is None:
            base = self.__capacity
        return hash(key) % base

    def put(self, key, value):
        bucket_index = self.__hash(key)
        bucket = self.__buckets[bucket_index]

        for i, (k, v) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                return

        bucket.append((key, value))
        self.__size += 1

        if self.__size > self.__capacity * 0.7:
            self.__resize()

    def __resize(self):
        new_capacity = self.__capacity * 2
        new_buckets = [[] for _ in range(new_capacity)]

        for bucket in self.__buckets:
            for (k, v) in bucket:
                index = hash(k) % new_capacity
                new_buckets[index].append((k, v))

        self.__capacity = new_capacity
        self.__buckets = new_buckets

    def __get(self, key):
        bucket_index = self.__hash(key)
        bucket = self.__buckets[bucket_index]
        for k, v in bucket:
            if k == key:
                return v, True
        return None, False

    def get(self, key):
        v, found = self.__get(key)
        if found:
            return v
        raise KeyError(f"key {key} not found")

    def remove(self, key):
        bucket_index = self.__hash(key)
        bucket = self.__buckets[bucket_index]
        for i, (k, v) in enumerate(bucket):
            if k == key:
                del bucket[i]
                self.__size -= 1
                return
        raise KeyError(f"key {key} not found")

    def __contains__(self, key):
        _, found = self.__get(key)
        return found

    def __iter__(self):
        for bucket in self.__buckets:
            for k, v in bucket:
                yield k, v

    def __len__(self):
        return self.__size

    def keys(self):
        return [k for k, v in self]

    def values(self):
        return [v for k, v in self]

    def items(self):
        return [(k, v) for k, v in self]

    def clear(self):
        self.__capacity = 10
        self.__buckets = [[] for _ in range(self.__capacity)]
        self.__size = 0

    def __str__(self):
        return "{" + ", ".join(f"{k}: {v}" for k, v in self) + "}"


# =======================================
#        ESTRUCTURA DE DATOS: SET
# =======================================


class Set:
    def __init__(self):
        self.__capacity = 10
        self.__size = 0
        self.__buckets = [[] for _ in range(self.__capacity)]

    def __hash(self, element, base=None):
        if base is None:
            base = self.__capacity
        return hash(element) % base

    def add(self, element):
        bucket_index = self.__hash(element)
        bucket = self.__buckets[bucket_index]

        if element not in bucket:
            bucket.append(element)
            self.__size += 1

        if self.__size > self.__capacity * 0.7:
            self.__resize()

    def __resize(self):
        new_capacity = self.__capacity * 2
        new_buckets = [[] for _ in range(new_capacity)]

        for bucket in self.__buckets:
            for element in bucket:
                index = hash(element) % new_capacity
                new_buckets[index].append(element)

        self.__capacity = new_capacity
        self.__buckets = new_buckets

    def remove(self, element):
        bucket_index = self.__hash(element)
        bucket = self.__buckets[bucket_index]

        if element not in bucket:
            raise KeyError(f"{element}")

        bucket.remove(element)
        self.__size -= 1

    def discard(self, element):
        bucket_index = self.__hash(element)
        bucket = self.__buckets[bucket_index]

        if element in bucket:
            bucket.remove(element)
            self.__size -= 1

    def is_empty(self):
        return self.__size == 0

    def __contains__(self, element):
        bucket_index = self.__hash(element)
        return element in self.__buckets[bucket_index]

    def __iter__(self):
        for bucket in self.__buckets:
            for e in bucket:
                yield e

    def clear(self):
        self.__init__()

    def union(self, s2):
        new_set = Set()
        for e in self:
            new_set.add(e)
        for e in s2:
            new_set.add(e)
        return new_set

    def intersection(self, s2):
        new_set = Set()
        for e in self:
            if e in s2:
                new_set.add(e)
        return new_set

    def __str__(self):
        return "{" + ", ".join(str(e) for e in self) + "}"


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

        self._configurar_estilos()
        self._crear_layout()
        self.cargar_datos_demo()  # llena con libros reales

    def _configurar_estilos(self):
        """Define una paleta y estilos coherentes para toda la interfaz."""

        palette = {
            "bg": "#f4f1ea",
            "panel": "#ffffff",
            "accent": "#5c7c6f",
            "accent_dark": "#39594c",
            "text": "#2f2a28",
            "muted": "#6d625c",
            "border": "#d6cec6",
            "input": "#fdfbf7",
        }

        self.configure(bg=palette["bg"])
        default_font = ("Segoe UI", 10)
        self.option_add("*Font", default_font)

        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure(
            "TFrame",
            background=palette["bg"],
            relief="flat",
        )
        style.configure(
            "TLabel",
            background=palette["bg"],
            foreground=palette["text"],
        )
        style.configure(
            "Titulo.TLabel",
            background=palette["bg"],
            foreground=palette["accent_dark"],
            font=("Georgia", 16, "bold"),
        )
        style.configure(
            "Subtitulo.TLabel",
            background=palette["bg"],
            foreground=palette["muted"],
            font=("Segoe UI", 10, "italic"),
        )
        style.configure(
            "TButton",
            background=palette["accent"],
            foreground="#ffffff",
            borderwidth=0,
            padding=(12, 7),
            focusthickness=3,
            focuscolor=palette["border"],
        )
        style.map(
            "TButton",
            background=[("active", palette["accent_dark"])],
            foreground=[("active", "#ffffff")],
        )
        style.configure(
            "TEntry",
            fieldbackground=palette["input"],
            background=palette["input"],
            foreground=palette["text"],
            bordercolor=palette["border"],
            padding=6,
        )
        style.map(
            "TEntry",
            fieldbackground=[("disabled", palette["bg"])],
            foreground=[("disabled", palette["muted"])],
        )
        style.configure(
            "Treeview",
            background=palette["panel"],
            fieldbackground=palette["panel"],
            foreground=palette["text"],
            bordercolor=palette["border"],
            rowheight=24,
        )
        style.configure(
            "Treeview.Heading",
            background=palette["accent"],
            foreground="#ffffff",
            relief="flat",
            font=("Segoe UI", 10, "bold"),
        )
        style.map(
            "Treeview",
            background=[("selected", palette["accent"])],
            foreground=[("selected", "#ffffff")],
        )

        style.configure(
            "TNotebook",
            background=palette["bg"],
            bordercolor=palette["bg"],
        )
        style.configure(
            "TNotebook.Tab",
            background=palette["panel"],
            foreground=palette["muted"],
            padding=(10, 6),
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", palette["accent"]), ("active", palette["accent_dark"])],
            foreground=[("selected", "#ffffff"), ("active", "#ffffff")],
        )

        # Acolchonado general para que los frames no se peguen a los bordes
        style.configure("Card.TFrame", background=palette["panel"], relief="flat", borderwidth=1)
        self.option_add("*TFrame.padding", 6)


    # --- layout principal: menú lateral + área central ---
    def _crear_layout(self):
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=4)
        self.rowconfigure(0, weight=1)

        self.frame_menu = ttk.Frame(self, padding=10, style="Card.TFrame")
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
        self.frame_contenido = ttk.Frame(self, padding=14, style="Card.TFrame")
        self.frame_contenido.grid(row=0, column=1, sticky="nsew")
        self.frame_contenido.rowconfigure(1, weight=1)
        self.frame_contenido.columnconfigure(0, weight=1)

        self.mostrar_inicio_registro()

    def _render_menu_buttons(self):
        """Muestra solo el registro hasta que el usuario cree una cuenta."""

        for widget in self.frame_menu_botones.winfo_children():
            widget.destroy()

        if self.registro_completado:
            for texto, comando in self.menu_opciones_secundarias:
                ttk.Button(self.frame_menu_botones, text=texto, command=comando).pack(
                    fill="x", pady=3
                )
        else:
            ttk.Button(
                self.frame_menu_botones,
                text="Inicio / Registro",
                command=self.mostrar_inicio_registro,
            ).pack(fill="x", pady=3)

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
        txt = tk.Text(
            self.frame_contenido,
            height=18,
            bg="#fdfbf7",
            fg="#2f2a28",
            wrap="word",
            relief="flat",
            bd=8,
            font=("Segoe UI", 10),
            highlightthickness=0,
        )
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

        barra_busqueda = ttk.Frame(self.frame_contenido)
        barra_busqueda.grid(row=1, column=0, sticky="ew", pady=(0, 5))
        barra_busqueda.columnconfigure(0, weight=1)

        ttk.Label(barra_busqueda, text="Buscar libro:").grid(row=0, column=1, sticky="e", padx=5)
        busqueda_entry = ttk.Entry(barra_busqueda, width=35)
        busqueda_entry.grid(row=0, column=2, padx=5, pady=2, sticky="e")
        btn_buscar = ttk.Button(barra_busqueda, text="Buscar")
        btn_buscar.grid(row=0, column=3, padx=5)
        btn_ver_todo = ttk.Button(barra_busqueda, text="Ver todo")
        btn_ver_todo.grid(row=0, column=4, padx=5)

        formulario = ttk.LabelFrame(self.frame_contenido, text="Acciones rápidas")
        formulario.grid(row=2, column=0, sticky="nwe", pady=5)
        formulario.columnconfigure(1, weight=1)

        ttk.Label(formulario, text="ID para eliminar:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
        id_eliminar_entry = ttk.Entry(formulario, width=20)
        id_eliminar_entry.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        ttk.Label(formulario, text="ID Usuario (historial opcional):").grid(
            row=1, column=0, sticky="e", padx=5, pady=2
        )
        usuario_accion_entry = ttk.Entry(formulario, width=20)
        usuario_accion_entry.grid(row=1, column=1, sticky="w", padx=5, pady=2)

        txt = self.crear_area_resultados(row=3)

        def limpiar_campos():
            for widget in (busqueda_entry, id_eliminar_entry, usuario_accion_entry):
                widget.delete(0, tk.END)
            self.listar_libros_texto(txt)

        def ejecutar_busqueda():
            patron = busqueda_entry.get().strip()
            if not patron:
                self.listar_libros_texto(txt)
                return
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
            if usuario_hist:
                registrar_historial(
                    usuario_hist,
                    f"Buscó '{patron or 'todo el catálogo'}' desde la gestión de libros",
                )

        def abrir_modal_agregar():
            modal = tk.Toplevel(self)
            modal.title("Agregar libro al catálogo")
            modal.transient(self)
            modal.grab_set()

            ttk.Label(modal, text="ID Libro:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
            ttk.Label(modal, text="Título:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
            ttk.Label(modal, text="Autor:").grid(row=2, column=0, sticky="e", padx=5, pady=2)
            ttk.Label(modal, text="Géneros (coma):").grid(row=3, column=0, sticky="e", padx=5, pady=2)
            ttk.Label(modal, text="Archivo de portada (opcional):").grid(
                row=4, column=0, sticky="e", padx=5, pady=2
            )
            ttk.Label(modal, text="ID Usuario (historial opcional):").grid(
                row=5, column=0, sticky="e", padx=5, pady=2
            )

            modal_id_entry = ttk.Entry(modal, width=25)
            modal_titulo_entry = ttk.Entry(modal, width=40)
            modal_autor_entry = ttk.Entry(modal, width=30)
            modal_generos_entry = ttk.Entry(modal, width=40)
            modal_portada_entry = ttk.Entry(modal, width=30)
            modal_usuario_entry = ttk.Entry(modal, width=25)

            modal_id_entry.grid(row=0, column=1, padx=5, pady=2)
            modal_titulo_entry.grid(row=1, column=1, padx=5, pady=2)
            modal_autor_entry.grid(row=2, column=1, padx=5, pady=2)
            modal_generos_entry.grid(row=3, column=1, padx=5, pady=2)
            modal_portada_entry.grid(row=4, column=1, padx=5, pady=2)
            modal_usuario_entry.grid(row=5, column=1, padx=5, pady=2)

            def registrar_desde_modal():
                libro_id = modal_id_entry.get().strip()
                if not libro_id:
                    messagebox.showwarning("Error", "El ID del libro es obligatorio.")
                    return
                if libro_id in libros:
                    messagebox.showwarning("Error", "Ya existe un libro con ese ID.")
                    return
                titulo = modal_titulo_entry.get().strip()
                autor = modal_autor_entry.get().strip()
                generos = [g.strip() for g in modal_generos_entry.get().split(",") if g.strip()]
                portada = modal_portada_entry.get().strip() or None
                if not titulo or not autor or not generos:
                    messagebox.showwarning(
                        "Error", "Título, autor y al menos un género son obligatorios."
                    )
                    return
                libros[libro_id] = Libro(libro_id, titulo, autor, generos, portada)
                notificaciones.encolar(f"Nuevo libro registrado: {titulo}")
                usuario_hist = modal_usuario_entry.get().strip()
                if usuario_hist:
                    registrar_historial(
                        usuario_hist,
                        f"Agregó el libro '{titulo}' (ID {libro_id}) el {datetime.now().strftime('%d/%m/%Y')}",
                    )
                messagebox.showinfo("Registro", "Libro agregado correctamente.")
                modal.destroy()
                self.listar_libros_texto(txt)

            botones_modal = ttk.Frame(modal)
            botones_modal.grid(row=6, column=0, columnspan=2, pady=10)
            ttk.Button(botones_modal, text="Guardar", command=registrar_desde_modal).grid(
                row=0, column=0, padx=5
            )
            ttk.Button(botones_modal, text="Cancelar", command=modal.destroy).grid(
                row=0, column=1, padx=5
            )

        def eliminar_libro():
            libro_id = id_eliminar_entry.get().strip()
            if not libro_id:
                messagebox.showwarning("Error", "Indique el ID del libro a eliminar.")
                return
            if libro_id not in libros:
                messagebox.showwarning("Error", "Libro no encontrado.")
                return
            eliminado = libros.pop(libro_id)
            notificaciones.encolar(f"Libro eliminado: {eliminado.titulo}")
            usuario_hist = usuario_accion_entry.get().strip()
            if usuario_hist:
                registrar_historial(
                    usuario_hist,
                    f"Retiró el libro '{eliminado.titulo}' (ID {libro_id}) del catálogo",
                )
            messagebox.showinfo("Gestión", "Libro eliminado correctamente.")
            self.listar_libros_texto(txt)

        botones = ttk.Frame(self.frame_contenido)
        botones.grid(row=4, column=0, pady=5)
        ttk.Button(botones, text="Agregar libro", command=abrir_modal_agregar).grid(
            row=0, column=0, padx=10
        )
        ttk.Button(botones, text="Eliminar libro", command=eliminar_libro).grid(
            row=0, column=1, padx=10
        )
        ttk.Button(botones, text="Limpiar", command=limpiar_campos).grid(
            row=0, column=2, padx=10
        )

        busqueda_entry.bind("<Return>", lambda _event: ejecutar_busqueda())
        btn_buscar.config(command=ejecutar_busqueda)
        btn_ver_todo.config(command=lambda: self.listar_libros_texto(txt))
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

        cabecera = ttk.Frame(self.frame_contenido)
        cabecera.grid(row=0, column=0, sticky="ew")
        cabecera.columnconfigure(0, weight=1)

        ttk.Label(
            cabecera,
            text="Gestión de Usuarios",
            font=("Arial", 14, "bold"),
        ).grid(row=0, column=0, sticky="w")

        ttk.Label(cabecera, text="Buscar (ID o nombre):").grid(row=0, column=1, sticky="e")
        busqueda_entry = ttk.Entry(cabecera, width=28)
        busqueda_entry.grid(row=0, column=2, padx=5, pady=2, sticky="e")
        ttk.Button(
            cabecera,
            text="Buscar",
            command=lambda: ejecutar_busqueda(busqueda_entry.get().strip()),
        ).grid(row=0, column=3, padx=5)

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

        botones = ttk.Frame(frm)
        botones.grid(row=3, column=0, columnspan=2, pady=5)

        txt = self.crear_area_resultados(row=3)

        def limpiar_campos():
            for widget in (
                busqueda_entry,
                id_entry,
                nombre_entry,
                generos_entry,
                elim_id_entry,
                elim_nombre_entry,
            ):
                widget.delete(0, tk.END)
            self.listar_usuarios_texto(txt)

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
            registrar_historial(
                usuario_id,
                f"Usuario registrado el {datetime.now().strftime('%d/%m/%Y')}"
            )
            notificaciones.encolar(f"Nuevo usuario registrado: {nombre}")
            messagebox.showinfo("OK", "Usuario registrado.")
            self.listar_usuarios_texto(txt)

        def listar():
            self.listar_usuarios_texto(txt)

        def ejecutar_busqueda(patron):
            patron = patron or busqueda_entry.get().strip()
            if not patron:
                self.listar_usuarios_texto(txt)
                return
            resultados = []
            for u in usuarios.values():
                texto = f"{u.id} {u.nombre}"
                if contiene_patron(texto, patron):
                    resultados.append(u)
            if not resultados:
                self.escribir_en_texto(txt, "No se encontraron usuarios.")
                return
            s = "Resultados de búsqueda:\n\n"
            for u in resultados:
                estado = "Sí pidió libros" if u.libros_actuales else "Sin préstamos activos"
                s += (
                    f"[{u.id}] {u.nombre}\n"
                    f"   Estado: {estado} (total {len(u.libros_actuales)})\n"
                )
            self.escribir_en_texto(txt, s)

        ttk.Button(botones, text="Registrar", command=registrar).grid(row=0, column=0, padx=5)
        ttk.Button(botones, text="Listar todos", command=listar).grid(row=0, column=1, padx=5)
        ttk.Button(
            botones,
            text="Buscar con el formulario",
            command=lambda: ejecutar_busqueda(nombre_entry.get().strip()),
        ).grid(row=0, column=2, padx=5)
        ttk.Button(botones, text="Limpiar", command=limpiar_campos).grid(row=0, column=3, padx=5)

        marco_eliminar = ttk.LabelFrame(self.frame_contenido, text="Eliminar usuario")
        marco_eliminar.grid(row=2, column=0, sticky="ew", padx=2, pady=(5, 0))
        ttk.Label(marco_eliminar, text="ID:").grid(row=0, column=0, sticky="e")
        elim_id_entry = ttk.Entry(marco_eliminar, width=15)
        elim_id_entry.grid(row=0, column=1, padx=5, pady=2, sticky="w")
        ttk.Label(marco_eliminar, text="Nombre:").grid(row=1, column=0, sticky="e")
        elim_nombre_entry = ttk.Entry(marco_eliminar, width=30)
        elim_nombre_entry.grid(row=1, column=1, padx=5, pady=2, sticky="w")

        def eliminar():
            usuario_id = elim_id_entry.get().strip() or id_entry.get().strip()
            if not usuario_id:
                messagebox.showwarning("Error", "Indica el ID del usuario a eliminar.")
                return
            usuario = usuarios.get(usuario_id)
            if not usuario:
                messagebox.showwarning("Error", "Usuario no encontrado.")
                return
            nombre_ref = elim_nombre_entry.get().strip()
            if nombre_ref and nombre_ref.lower() != usuario.nombre.lower():
                if not messagebox.askyesno(
                    "Confirmar",
                    "El nombre no coincide con el registro actual. ¿Deseas continuar?",
                ):
                    return
            registrar_historial(usuario_id, "Cuenta eliminada por el administrador")
            del usuarios[usuario_id]
            notificaciones.encolar(
                f"Usuario eliminado: {usuario.nombre} (ID {usuario_id})"
            )
            messagebox.showinfo("OK", "Usuario eliminado.")
            self.listar_usuarios_texto(txt)

        ttk.Button(marco_eliminar, text="Eliminar usuario", command=eliminar).grid(
            row=2, column=0, columnspan=2, pady=5
        )

        self.listar_usuarios_texto(txt)

    def listar_usuarios_texto(self, txt):
        if not usuarios:
            self.escribir_en_texto(txt, "No hay usuarios registrados.")
            return
        s = "Mapa de Usuarios:\n\n"
        for u in usuarios.values():
            s += f"[{u.id}] {u.nombre}\n"
            if u.libros_actuales:
                ids = ", ".join(sorted(u.libros_actuales))
                estado = f"Sí pidió libros (IDs: {ids})"
            else:
                estado = "Sin préstamos activos"
            s += f"   Estado de préstamos: {estado}\n"
            s += f"   Géneros preferidos: {', '.join(u.generos_preferidos)}\n"
        self.escribir_en_texto(txt, s)

    # -------------- Préstamos / Devoluciones --------

    def mostrar_prestamos(self):
        self.limpiar_contenido()
        ttk.Label(
            self.frame_contenido,
            text="Préstamos y Devoluciones",
            font=("Arial", 14, "bold"),
        ).grid(row=0, column=0, sticky="w")

        frm = ttk.Frame(self.frame_contenido)
        frm.grid(row=1, column=0, sticky="nwe")

        ttk.Label(frm, text="ID Usuario:").grid(row=0, column=0, sticky="e")
        ttk.Label(frm, text="Nombre del usuario:").grid(row=0, column=2, sticky="e")
        ttk.Label(frm, text="ID Libro:").grid(row=1, column=0, sticky="e")
        ttk.Label(frm, text="Título del libro:").grid(row=1, column=2, sticky="e")
        ttk.Label(frm, text="Autor del libro:").grid(row=2, column=0, sticky="e")
        ttk.Label(frm, text="F. Préstamo (dd/mm/aaaa):").grid(row=2, column=2, sticky="e")
        ttk.Label(frm, text="F. Devolución (dd/mm/aaaa):").grid(row=3, column=2, sticky="e")

        u_entry = ttk.Entry(frm, width=18)
        nombre_entry = ttk.Entry(frm, width=25)
        l_entry = ttk.Entry(frm, width=18)
        titulo_entry = ttk.Entry(frm, width=30)
        autor_entry = ttk.Entry(frm, width=25)
        fp_entry = ttk.Entry(frm, width=18)
        fd_entry = ttk.Entry(frm, width=18)

        u_entry.grid(row=0, column=1, padx=5, pady=2, sticky="w")
        nombre_entry.grid(row=0, column=3, padx=5, pady=2, sticky="w")
        l_entry.grid(row=1, column=1, padx=5, pady=2, sticky="w")
        titulo_entry.grid(row=1, column=3, padx=5, pady=2, sticky="w")
        autor_entry.grid(row=2, column=1, padx=5, pady=2, sticky="w")
        fp_entry.grid(row=2, column=3, padx=5, pady=2, sticky="w")
        fd_entry.grid(row=3, column=3, padx=5, pady=2, sticky="w")

        txt = self.crear_area_resultados(row=2)

        def limpiar_campos():
            for widget in (
                u_entry,
                nombre_entry,
                l_entry,
                titulo_entry,
                autor_entry,
                fp_entry,
                fd_entry,
            ):
                widget.delete(0, tk.END)

        def registrar_prestamo():
            usuario_id = u_entry.get().strip()
            nombre_usuario = nombre_entry.get().strip()
            libro_id = l_entry.get().strip()
            titulo_reportado = titulo_entry.get().strip()
            autor_reportado = autor_entry.get().strip()
            fecha_p = fp_entry.get().strip()
            fecha_d = fd_entry.get().strip()
            if not nombre_usuario:
                messagebox.showwarning("Datos incompletos", "Escribe el nombre del usuario que solicita el libro.")
                return
            if not titulo_reportado or not autor_reportado:
                messagebox.showwarning("Datos incompletos", "Indica el título y el autor del libro.")
                return
            if not fecha_p or not fecha_d:
                messagebox.showwarning("Datos incompletos", "Captura las fechas de préstamo y devolución.")
                return
            if usuario_id not in usuarios:
                messagebox.showwarning("Error", "Usuario no encontrado.")
                return
            if libro_id not in libros:
                messagebox.showwarning("Error", "Libro no encontrado.")
                return

            usuario = usuarios[usuario_id]
            libro = libros[libro_id]

            if nombre_usuario and nombre_usuario.lower() != usuario.nombre.lower():
                messagebox.showwarning(
                    "Advertencia",
                    "El nombre proporcionado no coincide con el usuario registrado.",
                )
                return
            if titulo_reportado and titulo_reportado.lower() != libro.titulo.lower():
                messagebox.showwarning(
                    "Advertencia",
                    "El título proporcionado no coincide con el libro registrado.",
                )
                return
            if autor_reportado and autor_reportado.lower() != libro.autor.lower():
                messagebox.showwarning(
                    "Advertencia",
                    "El autor proporcionado no coincide con el libro registrado.",
                )
                return

            if not libro.disponible:
                prioridad = 5
                reservas.insertar(prioridad, Reserva(usuario_id, libro_id, prioridad))
                notificaciones.encolar(
                    f"Reserva creada: {usuario.nombre} -> {libro.titulo}"
                )
                messagebox.showinfo(
                    "Reserva",
                    "El libro no está disponible. Se creó una reserva.",
                )
                self.mostrar_reservas_texto(txt)
                return

            prestamo = Prestamo(libro_id, usuario_id, fecha_p, fecha_d)
            prestamos_activos.agregar(prestamo)
            libro.disponible = False
            libro.popularidad += 1
            usuario.libros_actuales.add(libro_id)
            usuario.historial.agregar(
                f"Préstamo de '{libro.titulo}' (autor: {libro.autor}) el {fecha_p}"
            )
            notificaciones.encolar(
                f"Préstamo registrado: {usuario.nombre} tomó '{libro.titulo}'"
            )
            messagebox.showinfo("OK", "Préstamo registrado.")
            limpiar_campos()
            self.mostrar_prestamos_texto(txt)

        def devolver():
            usuario_id = u_entry.get().strip()
            nombre_usuario = nombre_entry.get().strip()
            libro_id = l_entry.get().strip()
            if usuario_id not in usuarios or libro_id not in libros:
                messagebox.showwarning(
                    "Error",
                    "Debe indicar un usuario y un libro válidos para registrar la devolución.",
                )
                return
            usuario = usuarios[usuario_id]
            libro = libros[libro_id]
            if nombre_usuario and nombre_usuario.lower() != usuario.nombre.lower():
                messagebox.showwarning(
                    "Advertencia",
                    "El nombre proporcionado no coincide con el usuario registrado.",
                )
                return

            encontrado = False
            for p in prestamos_activos:
                if p.activo and p.libro_id == libro_id and p.usuario_id == usuario_id:
                    p.activo = False
                    encontrado = True
                    break
            if not encontrado:
                messagebox.showwarning(
                    "Error",
                    "No hay préstamo activo con esos datos.",
                )
                return

            libro.disponible = True
            if libro_id in usuario.libros_actuales:
                usuario.libros_actuales.remove(libro_id)
            fecha_hoy = datetime.now().strftime("%d/%m/%Y")
            usuario.historial.agregar(
                f"Devolución de '{libro.titulo}' el {fecha_hoy}"
            )
            notificaciones.encolar(
                f"Devolución registrada: {usuario.nombre} entregó '{libro.titulo}'"
            )

            if not reservas.esta_vacia():
                r = reservas.extraer_min()
                u_res = usuarios.get(r.usuario_id)
                if u_res:
                    notificaciones.encolar(
                        f"Libro '{libro.titulo}' listo para reserva de {u_res.nombre}"
                    )
            messagebox.showinfo("OK", "Devolución registrada.")
            limpiar_campos()
            self.mostrar_prestamos_texto(txt)

        def ver_prestamos():
            self.mostrar_prestamos_texto(txt)

        def ver_reservas():
            self.mostrar_reservas_texto(txt)

        def limpiar_registros_devueltos():
            activos = []
            total = 0
            for p in prestamos_activos:
                total += 1
                if p.activo:
                    activos.append(p)
            if total == len(activos):
                messagebox.showinfo(
                    "Sin cambios",
                    "No hay registros devueltos por limpiar.",
                )
                return
            prestamos_activos.head = None
            prestamos_activos.tail = None
            for p in activos:
                prestamos_activos.agregar(p)
            messagebox.showinfo(
                "Limpieza completada",
                "Se quitaron los préstamos ya devueltos de la lista.",
            )
            self.mostrar_prestamos_texto(txt)

        botones = ttk.Frame(frm)
        botones.grid(row=4, column=0, columnspan=4, pady=5)

        ttk.Button(botones, text="Registrar préstamo", command=registrar_prestamo).grid(
            row=0, column=0, padx=5
        )
        ttk.Button(botones, text="Registrar devolución", command=devolver).grid(
            row=0, column=1, padx=5
        )
        ttk.Button(botones, text="Ver préstamos activos", command=ver_prestamos).grid(
            row=0, column=2, padx=5
        )
        ttk.Button(botones, text="Ver reservas (cola prioridad)", command=ver_reservas).grid(
            row=0, column=3, padx=5
        )
        ttk.Button(
            botones,
            text="Quitar registros devueltos",
            command=limpiar_registros_devueltos,
        ).grid(row=0, column=4, padx=5)
        ttk.Button(botones, text="Limpiar", command=limpiar_campos).grid(row=0, column=5, padx=5)

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

        contenedor = ttk.Frame(self.frame_contenido)
        contenedor.grid(row=1, column=0, sticky="nsew")
        contenedor.columnconfigure(1, weight=1)
        contenedor.rowconfigure(0, weight=1)

        marco_lista = ttk.LabelFrame(contenedor, text="Usuarios registrados")
        marco_lista.grid(row=0, column=0, sticky="nsw", padx=(0, 10))

        columnas = ("id", "nombre", "prestamos")
        tabla = ttk.Treeview(marco_lista, columns=columnas, show="headings", height=15)
        tabla.heading("id", text="ID")
        tabla.heading("nombre", text="Nombre")
        tabla.heading("prestamos", text="Préstamos activos")
        tabla.column("id", width=80, anchor="center")
        tabla.column("nombre", width=160)
        tabla.column("prestamos", width=120, anchor="center")

        scroll = ttk.Scrollbar(marco_lista, orient="vertical", command=tabla.yview)
        tabla.configure(yscroll=scroll.set)
        tabla.grid(row=0, column=0, sticky="nsew")
        scroll.grid(row=0, column=1, sticky="ns")
        marco_lista.rowconfigure(0, weight=1)
        marco_lista.columnconfigure(0, weight=1)

        panel_detalle = ttk.LabelFrame(contenedor, text="Perfil del usuario")
        panel_detalle.grid(row=0, column=1, sticky="nsew")
        panel_detalle.columnconfigure(1, weight=1)
        panel_detalle.rowconfigure(2, weight=1)

        ttk.Label(panel_detalle, text="ID seleccionado:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
        id_entry = ttk.Entry(panel_detalle, width=18)
        id_entry.grid(row=0, column=1, sticky="w", padx=5, pady=2)

        ttk.Label(panel_detalle, text="Actividad manual:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        act_entry = ttk.Entry(panel_detalle, width=60)
        act_entry.grid(row=1, column=1, sticky="w", padx=5, pady=2)

        txt = tk.Text(panel_detalle, height=18, wrap="word")
        txt.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=5, pady=(8, 4))
        txt.config(state="disabled")

        def escribir_detalle(texto):
            txt.config(state="normal")
            txt.delete("1.0", tk.END)
            txt.insert(tk.END, texto)
            txt.config(state="disabled")

        def resumen_prestamos(usuario_obj):
            activos = []
            for prestamo in prestamos_activos:
                if prestamo.activo and prestamo.usuario_id == usuario_obj.id:
                    libro = libros.get(prestamo.libro_id)
                    titulo = libro.titulo if libro else prestamo.libro_id
                    activos.append(
                        f"- {titulo} | {prestamo.fecha_prestamo} → {prestamo.fecha_devolucion}"
                    )
            return activos

        def render_perfil(usuario_obj):
            if not usuario_obj:
                escribir_detalle("Seleccione un usuario para ver su perfil.")
                return

            id_entry.delete(0, tk.END)
            id_entry.insert(0, usuario_obj.id)

            historial_items = list(usuario_obj.historial)
            busquedas = [ev for ev in historial_items if "busc" in ev.lower()]
            prestamos_usuario = resumen_prestamos(usuario_obj)

            encabezado = [
                f"Nombre: {usuario_obj.nombre}",
                f"ID: {usuario_obj.id}",
                f"Géneros preferidos: {', '.join(sorted(usuario_obj.generos_preferidos)) or '—'}",
            ]

            estado_prestamo = (
                f"Tiene {len(prestamos_usuario)} préstamo(s) activo(s)." if prestamos_usuario else "No debe libros."
            )

            cuerpo = "\n".join(encabezado)
            cuerpo += "\n\nEstado de préstamos: " + estado_prestamo
            cuerpo += "\nLibros en mano: " + (", ".join(usuario_obj.libros_actuales) if usuario_obj.libros_actuales else "Ninguno")
            cuerpo += "\nConsultas registradas: " + (str(len(busquedas)) if busquedas else "0")

            if prestamos_usuario:
                cuerpo += "\n\nPréstamos activos:\n" + "\n".join(prestamos_usuario)

            cuerpo += "\n\nHistorial detallado:\n"
            if historial_items:
                cuerpo += "\n".join(f"- {ev}" for ev in historial_items)
            else:
                cuerpo += "No hay actividades registradas."

            escribir_detalle(cuerpo)

        def cargar_lista():
            tabla.delete(*tabla.get_children())
            for usuario_obj in sorted(usuarios.values(), key=lambda u: u.nombre.lower()):
                activos = len([p for p in prestamos_activos if p.activo and p.usuario_id == usuario_obj.id])
                tabla.insert("", "end", values=(usuario_obj.id, usuario_obj.nombre, activos))

            if usuarios:
                primero = tabla.get_children()
                if primero:
                    tabla.selection_set(primero[0])
                    render_perfil(usuarios.get(tabla.item(primero[0], "values")[0]))
            else:
                escribir_detalle("No hay usuarios registrados todavía.")

        def on_select(_event=None):
            seleccionado = tabla.selection()
            if not seleccionado:
                return
            valores = tabla.item(seleccionado[0], "values")
            usuario_obj = usuarios.get(valores[0])
            render_perfil(usuario_obj)

        def agregar_actividad():
            usuario_id = id_entry.get().strip()
            usuario_obj = usuarios.get(usuario_id)
            if not usuario_obj:
                messagebox.showwarning("Error", "Usuario no encontrado.")
                return
            actividad = act_entry.get().strip()
            if not actividad:
                messagebox.showwarning("Error", "Escriba una actividad.")
                return
            usuario_obj.historial.agregar(actividad)
            notificaciones.encolar(f"Actividad añadida al historial de {usuario_obj.nombre}")
            messagebox.showinfo("OK", "Actividad agregada.")
            act_entry.delete(0, tk.END)
            cargar_lista()
            render_perfil(usuario_obj)

        botones = ttk.Frame(panel_detalle)
        botones.grid(row=3, column=0, columnspan=2, pady=6)
        ttk.Button(botones, text="Agregar actividad", command=agregar_actividad).grid(row=0, column=0, padx=5)

        tabla.bind("<<TreeviewSelect>>", on_select)
        cargar_lista()

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
