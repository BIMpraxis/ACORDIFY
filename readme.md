# Acordify - Identificador de Acordes y Escalas MIDI en Tiempo Real

**Repositorio:** [https://github.com/BIMpraxis/ACORDIFY](https://github.com/BIMpraxis/ACORDIFY)

Un script de Python (`acordify.py`) que escucha la entrada de un teclado MIDI conectado y muestra en tiempo real el nombre del acorde que se está tocando. Las futuras versiones incluirán identificación de escalas y una interfaz gráfica para visualización.

[![Estado del Repositorio](https://img.shields.io/badge/estado-en%20desarrollo-yellowgreen)](https://github.com/BIMpraxis/ACORDIFY)
[![Python Version](https://img.shields.io/badge/python-3.6%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Descripción

Acordify captura eventos MIDI (Note On / Note Off) de un dispositivo MIDI seleccionado por el usuario. Mantiene un registro de las notas activas y utiliza un diccionario de intervalos musicales para identificar el acorde formado por esas notas. Es capaz de reconocer triadas básicas, algunos acordes de séptima e inversiones (mostrando la nota del bajo con notación de barra, ej. C Major / E).

El objetivo a largo plazo es expandir esta funcionalidad para incluir la identificación de escalas musicales y presentar la información de forma visual en una interfaz gráfica de usuario (GUI) limpia, similar a aplicaciones como ChordieApp.

## Características Actuales

*   Detecta dispositivos de entrada MIDI conectados al sistema.
*   Permite al usuario seleccionar el dispositivo MIDI a utilizar.
*   Muestra las notas MIDI activas (con nombre y octava) en la consola.
*   Identifica acordes comunes en tiempo real (Mayores, menores, disminuidos, aumentados, sus4, sus2, séptimas principales, inversiones básicas).
*   Actualiza la pantalla de la consola solo cuando cambia el acorde identificado.
*   Basado puramente en consola (interfaz de línea de comandos).

## Requisitos

*   **Python:** Versión 3.6 o superior.
*   **Bibliotecas Python:**
    *   `mido`: Para la interfaz MIDI.
    *   `python-rtmidi`: Backend para `mido` (requiere compilación).
*   **Dependencias del Sistema (para `python-rtmidi`):**
    *   **Windows:** **Build Tools for Visual Studio** con la carga de trabajo **"Desarrollo para el escritorio con C++"** instalada. Puedes descargarlas [aquí](https://visualstudio.microsoft.com/es/downloads/#build-tools-for-visual-studio-2022). ¡Este paso es crucial en Windows!
    *   **Linux (Debian/Ubuntu):** `sudo apt install libasound2-dev build-essential` y asegúrate de que tu usuario pertenezca al grupo `audio` (`sudo usermod -aG audio $USER`, luego cierra sesión y vuelve a entrar).
    *   **Linux (Fedora):** `sudo dnf install alsa-lib-devel gcc-c++` y pertenencia al grupo `audio`.
    *   **macOS:** Generalmente funciona si tienes las **Xcode Command Line Tools** instaladas (`xcode-select --install`).
*   **Hardware:** Un teclado MIDI o controlador conectado a tu computadora y reconocido por el sistema operativo.

## Instalación

1.  **Clona el repositorio:**
    ```bash
    git clone https://github.com/BIMpraxis/ACORDIFY.git
    cd ACORDIFY
    ```
    *(Recuerda que necesitarás acceso si el repositorio es privado)*

2.  **Asegúrate de tener las dependencias del sistema instaladas** (ver sección "Requisitos") antes de continuar.

3.  **Instala las bibliotecas de Python:**
    ```bash
    pip install mido python-rtmidi
    ```
    *Nota:* Si tienes problemas al instalar `python-rtmidi`, verifica que las dependencias del sistema (compilador C++) estén correctamente instaladas y accesibles desde tu terminal.

## Uso (Versión Actual de Consola)

1.  **Conecta tu teclado MIDI** a la computadora y asegúrate de que esté encendido.
2.  **Abre una terminal** o símbolo del sistema.
3.  **Navega hasta la carpeta** donde se encuentra el script `acordify.py` (la raíz del repositorio clonado).
    ```bash
    cd ruta/a/ACORDIFY
    ```
4.  **Ejecuta el script:**
    ```bash
    python acordify.py
    ```
5.  El script listará los puertos MIDI de entrada disponibles. **Escribe el número** correspondiente a tu teclado MIDI y presiona `Enter`.
6.  El script comenzará a escuchar. **Toca notas o acordes** en tu teclado MIDI.
7.  La terminal mostrará las notas activas y el acorde identificado:
    ```
    Notas activas: C4, E4, G4 -> Acorde: C Major
    ```
    O para una inversión:
    ```
    Notas activas: E3, G4, C5 -> Acorde: C Major / E
    ```
8.  Para detener el script, presiona `Ctrl + C` en la terminal.

## Cómo Funciona (Brevemente)

1.  **Captura MIDI:** Usa `mido` para recibir mensajes `note_on` y `note_off`.
2.  **Estado de Notas:** Mantiene un conjunto (`set`) con los números de las notas MIDI actualmente presionadas.
3.  **Análisis de Acordes:**
    *   Cuando el conjunto de notas cambia, obtiene las clases de altura únicas (0-11).
    *   Itera sobre cada nota como una posible fundamental (raíz).
    *   Calcula los intervalos (en semitonos) de las otras notas respecto a esa posible raíz.
    *   Compara el conjunto de intervalos con un diccionario de acordes predefinidos (`CHORD_INTERVALS`).
    *   Si hay coincidencia, determina el tipo de acorde.
    *   Comprueba si la nota MIDI más baja tocada es la raíz; si no, añade la notación de inversión (`/ Bajonota`).
4.  **Salida:** Muestra el resultado en la consola.

## Limitaciones Actuales y Mejoras Futuras Planeadas

### Limitaciones Actuales
*   **Interfaz de Consola:** La salida es únicamente texto en la terminal.
*   **Diccionario de Acordes Limitado:** Solo reconoce un conjunto básico de acordes.
*   **Identificación Única:** Solo identifica acordes, no escalas.
*   **Ambigüedad:** La lógica para resolver acordes ambiguos es simple.
*   **Contexto Musical:** No considera tonalidad, progresiones o ritmo.

### Mejoras Futuras Planeadas
*   ✅ **Interfaz Gráfica (GUI):** Desarrollar una interfaz visual (posiblemente con Gradio u otro framework) para una experiencia más intuitiva.
*   ✅ **Visualización en Pentagrama:** Mostrar las notas activas en un pentagrama estándar (claves de Sol y Fa).
*   ✅ **Visualización en Teclado:** Mostrar las notas activas resaltadas en un teclado de piano virtual.
*   ✅ **Identificación de Escalas:** Añadir lógica para reconocer escalas comunes (pentatónicas, mayores, menores, modos, etc.) basadas en las notas tocadas.
*   **Expansión del Diccionario de Acordes:** Incluir acordes más complejos (9as, 11as, 13as, alterados).
*   **Configuración de Tonalidad (Key):** Permitir establecer una tonalidad para un análisis armónico más contextual.
*   **Mejora en la Resolución de Ambigüedades:** Implementar algoritmos más sofisticados para elegir la interpretación más probable del acorde/escala.

## Licencia

Este proyecto se distribuye bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.

## Contribuciones

Aunque el repositorio es actualmente privado, las sugerencias e ideas son bienvenidas. Una vez público, los informes de errores (issues) y contribuciones (pull requests) serán considerados.