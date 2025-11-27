# Sistema de Gestión de Biblioteca Digital

Este repositorio contiene una aplicación de escritorio construida con **Tkinter** que implementa un sistema de biblioteca digital con las secciones solicitadas en el enunciado:

- Gestión de libros
- Gestión de usuarios
- Préstamos y devoluciones
- Historial del usuario
- Notificaciones (cola FIFO)
- Búsqueda integrada en la sección de libros (usa coincidencias parciales sobre cadenas)

Cada sección demuestra el uso de estructuras de datos personalizadas como listas enlazadas, colas y colas de prioridad.

## Requisitos

- Python 3.10+
- Tkinter (incluido por defecto en las instalaciones estándar de Python en Windows y la mayoría de distribuciones de Linux)

## Aspecto visual

La interfaz emplea una paleta cálida inspirada en bibliotecas (tonos marfil y verde) con botones de acento, campos suavizados y tablas estilizadas para que la navegación se sienta más cuidada sin alterar el flujo ya implementado.

## Ejecución

```bash
python biblioteca_gui.py
```

Esto abrirá la interfaz gráfica descrita en el documento.

## Datos de demostración

Al iniciarse, la aplicación muestra un **menú principal con formulario de registro**. Hasta que completes ese registro inicial, el menú lateral solo mostrará dicha opción para que sigas el flujo solicitado "paso a paso"; una vez registrado, se habilitan las demás secciones. Además, se cargan automáticamente:

- Un catálogo extendido con hasta **10 000 libros** variados para que las búsquedas siempre arrojen resultados.
- 5 usuarios con historiales poblados y preferencias de lectura.
- Préstamos activos, reservas en la cola de prioridad y notificaciones iniciales.

Así, cada sección del menú muestra contenido real desde el primer arranque y puedes sumar tus propios usuarios desde el inicio sin navegar a otra vista.

## Flujo actual de gestión de libros

- En la **esquina superior derecha** de la vista verás un buscador permanente; escribe el título/autor/género y pulsa *Enter* o el botón "Buscar" para filtrar los miles de registros disponibles (hasta 10 000). 
- El botón "Ver todo" refresca el panel central para mostrar nuevamente el catálogo completo.
- En la parte inferior solo hay dos acciones principales: **Agregar libro** (abre una ventana modal que solicita todos los datos del ejemplar antes de registrarlo) y **Eliminar libro** (usa el ID indicado en el formulario rápido).
- Cada alta o baja se comunica mediante notificaciones y, si proporcionas un ID de usuario, la acción queda registrada en su historial.

## Flujo actual de gestión de usuarios

- La cabecera incluye un buscador en la esquina superior derecha que acepta **ID o nombre** para filtrar usuarios al instante.
- El formulario central permite registrar nuevos usuarios con sus géneros preferidos y botones para listar o lanzar una búsqueda con esos mismos campos.
- La parte inferior muestra un panel dedicado a **eliminar usuarios**: introduce el ID (y opcionalmente el nombre para mayor seguridad) y confirma con el botón correspondiente. Cada eliminación genera una notificación y una entrada en el historial del usuario antes de ser removido.
- El panel de resultados indica, para cada usuario, si actualmente tiene libros prestados ("Sí pidió libros") o si no registra movimientos activos.

## Flujo actual de préstamos y devoluciones

- En la parte superior del módulo se solicita el **ID y el nombre del usuario**, así como el **ID, título y autor del libro** más las fechas de préstamo y devolución. La pantalla valida todos esos datos antes de registrar el movimiento.
- El botón "Registrar préstamo" crea la operación, añade la entrada al historial del usuario, marca el libro como no disponible y genera la notificación correspondiente.
- "Registrar devolución" utiliza los mismos campos para ubicar el préstamo, liberar el ejemplar y registrar la actividad.
- El botón adicional "Quitar registros devueltos" purga la lista para que solo se muestren los préstamos realmente activos, tal como solicitaste.

## Flujo actual de historial de usuarios

- La sección muestra a **todos los usuarios registrados** en una tabla lateral con sus préstamos activos; al seleccionar uno se despliega su perfil con nombre, ID, géneros preferidos y estado de deuda.
- El perfil detalla los **libros que tiene en mano** (si debe algo), las búsquedas registradas, los préstamos activos con fechas y el historial cronológico de acciones (altas, bajas, búsquedas, préstamos y devoluciones).
- Puedes añadir notas manuales al historial desde el mismo panel; cada entrada adicional genera una notificación.

