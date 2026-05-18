# DataCity: Memoria y Archivos como una Metrópolis Cyberpunk

Aplicación web estática para explicar, de forma visual, cómo se ocupa, libera y fragmenta la memoria de una computadora. La RAM o el disco se representa como una ciudad cyberpunk: cada bloque es un lote, cada proceso es un edificio y los huecos libres son zonas baldías.

## Qué demuestra

- **Población Total:** memoria ocupada en MB.
- **Zonas Baldías:** cantidad de huecos libres entre bloques ocupados.
- **Contaminación del Sistema:** porcentaje de fragmentación calculado con base en el mayor bloque libre continuo.
- **Consumo Eléctrico de la Ciudad:** page faults simulados por segundo.
- **Nuevas Construcciones:** tasa simulada de lectura/escritura E/S por segundo.

## Funciones principales

- **Construir proceso:** asigna nuevos bloques de memoria como edificios neón.
- **Demoler zona:** libera un proceso y deja huecos en el mapa.
- **Tormenta E/S:** simula actividad intensa de lectura/escritura y cambios rápidos.
- **Desfragmentar:** compacta todos los bloques ocupados en un solo vecindario y deja un espacio libre continuo.
- **Heatmap y skyline:** muestra la memoria como mapa de calor y como horizonte de ciudad.

## Cómo ejecutarla

Abre `index.html` directamente en tu navegador o levanta un servidor local:

```bash
python3 -m http.server 8000
```

Luego visita `http://localhost:8000`.
