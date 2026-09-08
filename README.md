# 🦙 Clipora Clean

Limpiador de pistas y subtitulos de videos.

Parte del ecosistema **Clipora**.

## Caracteristicas

- Elimina pistas de video, audio y subtitulos no deseadas
- Soporte para multiples formatos (MP4, MKV, AVI, MOV, WebM, FLV, WMV)
- Seleccion automatica de pistas en espanol
- Procesamiento por lotes
- Barra de progreso en tiempo real
- Tema oscuro y claro
- Interfaz moderna y minimalista
- Procesamiento 100% local
- Sin dependencia de servidores externos
- Preserva el formato original del contenedor

## Requisitos

- Python 3.12+
- FFmpeg (se instala automaticamente en Windows)

## Instalacion

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/clipora-clean.git
cd clipora-clean

# Crear entorno virtual
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt
```

## Ejecucion

```bash
python app.py
```

## Uso

1. Abre la aplicacion
2. Haz clic en **Abrir videos** para seleccionar archivos
3. En el panel derecho, marca las pistas que quieres conservar
4. (Opcional) Selecciona una carpeta de salida diferente
5. Haz clic en **Procesar lote**
6. Los archivos procesados se guardaran con sufijo `_clean`, conservando el formato original

## Arquitectura

```
clipora-clean/
├── app.py                    # Punto de entrada
├── requirements.txt          # Dependencias
├── src/
│   ├── core/                 # Configuracion y constantes
│   │   ├── config.py         # Rutas del sistema
│   │   ├── constants.py      # Nombre, version, formatos
│   │   └── exceptions.py     # Excepciones custom
│   ├── models/
│   │   └── stream.py         # Modelo de datos Stream
│   ├── services/
│   │   ├── ffmpeg_service.py # Procesamiento de video
│   │   ├── ffprobe_service.py# Analisis de archivos
│   │   └── file_service.py   # Manejo de archivos y ffmpeg
│   ├── ui/
│   │   ├── theme.py          # Sistema de colores Clipora
│   │   ├── components/
│   │   │   ├── header.py     # Barra superior
│   │   │   ├── file_card.py  # Cards de archivos
│   │   │   └── stream_list.py# Lista de pistas
│   │   └── views/
│   │       └── main_view.py  # Vista principal
│   └── utils/
│       ├── logger.py         # Sistema de logging
│       └── file_utils.py     # Utilidades de archivos
├── config/                   # Configuracion del usuario
├── tests/                    # Pruebas unitarias
├── logs/                     # Logs de la aplicacion
└── temp/                     # Archivos temporales
```

## Tecnologias

- **Python 3.12+** - Lenguaje principal
- **Flet 0.86+** - Framework de interfaz grafica
- **FFmpeg** - Procesamiento multimedia

## Paleta de Colores

| Color | Hex |
|-------|-----|
| Clipora Purple | `#6C5CE7` |
| Primary Hover | `#5A4BD1` |
| Secondary | `#8B7CF6` |
| Accent | `#A29BFE` |

## Principios

- **Local-first** - Todo el procesamiento es local
- **Privacy-first** - Sin telemetry ni datos enviados
- **Simple para el usuario** - Potente internamente

## License

MIT License
