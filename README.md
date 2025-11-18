# Sistema de Gestión de Biblioteca Digital

Este repositorio contiene una aplicación de escritorio construida con **Tkinter** que implementa un sistema de biblioteca digital con las secciones solicitadas en el enunciado:

- Gestión de libros
- Gestión de usuarios
- Préstamos y devoluciones
- Historial del usuario
- Notificaciones (cola FIFO)
- Consultas de búsqueda (sobre cadenas)

Cada sección demuestra el uso de estructuras de datos personalizadas como listas enlazadas, colas y colas de prioridad.

## Requisitos

- Python 3.10+
- Tkinter (incluido por defecto en las instalaciones estándar de Python en Windows y la mayoría de distribuciones de Linux)

## Ejecución

```bash
python biblioteca_gui.py
```

Esto abrirá la interfaz gráfica descrita en el documento.

## Datos de demostración

Al iniciarse, la aplicación carga automáticamente:

- 15 libros de distintos géneros para que la galería y los listados luzcan completos.
- 5 usuarios con historiales poblados y preferencias de lectura.
- Préstamos activos, reservas en la cola de prioridad y notificaciones iniciales.

Así, cada sección del menú muestra contenido real desde el primer arranque.
