# Se deben instalar previamente (consola) estas cositas:
# pip install mido
# pip install python-rtmidi


import mido
import mido.backends.rtmidi # Asegura que rtmidi sea cargado
import time
import sys
import collections

# --- Definiciones de Acordes (Intervalos desde la fundamental en semitonos) ---
# Usamos frozenset para que puedan ser claves de diccionario si es necesario
CHORD_INTERVALS = {
    # Triadas
    frozenset({0, 4, 7}): "Major",
    frozenset({0, 3, 7}): "Minor",
    frozenset({0, 3, 6}): "Diminished",
    frozenset({0, 4, 8}): "Augmented",
    frozenset({0, 5, 7}): "Sus4",
    frozenset({0, 2, 7}): "Sus2",
    # Séptimas
    frozenset({0, 4, 7, 11}): "Major 7th",
    frozenset({0, 3, 7, 10}): "Minor 7th",
    frozenset({0, 4, 7, 10}): "Dominant 7th",
    frozenset({0, 3, 6, 10}): "Half-Diminished 7th (m7b5)",
    frozenset({0, 3, 6, 9}): "Diminished 7th",
    frozenset({0, 4, 8, 11}): "Augmented Major 7th",
    # Sextas
    frozenset({0, 4, 7, 9}): "Major 6th",
    frozenset({0, 3, 7, 9}): "Minor 6th",
    # Añadidas (Add) - Simplificadas aquí como triada + nota extra
    frozenset({0, 2, 4, 7}): "Major Add9 (no 5th)", # Ejemplo simplificado
    frozenset({0, 3, 7, 14 % 12}): "Minor Add9 (no 5th)", # Ejemplo simplificado
    # Puedes añadir muchos más acordes aquí (9as, 11as, 13as, alteraciones, etc.)
}

# Nombres de las notas (Usamos sostenidos)
NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

def midi_to_note_name(midi_note):
    """Convierte un número de nota MIDI a su nombre (ej. C4)."""
    if not (0 <= midi_note <= 127):
        return "Invalid"
    note_index = midi_note % 12
    octave = (midi_note // 12) - 1 # C4 es MIDI 60
    return f"{NOTE_NAMES[note_index]}{octave}"

def pitch_class_to_name(pitch_class):
    """Convierte una clase de altura (0-11) a su nombre (ej. C, C#)."""
    return NOTE_NAMES[pitch_class % 12]

def identify_chord(notes):
    """
    Intenta identificar el acorde formado por un conjunto de números de nota MIDI.
    Devuelve el nombre del acorde (ej. "C Major", "G Minor/Bb") o None.
    """
    if not notes or len(notes) < 2: # Necesitamos al menos 2 notas para un intervalo/acorde básico
        return None

    # Ordena las notas por altura MIDI (más baja primero)
    sorted_notes = sorted(list(notes))
    bass_note_midi = sorted_notes[0]

    # Obtiene las clases de altura únicas (0-11)
    pitch_classes = sorted(list(set(note % 12 for note in notes)))

    if len(pitch_classes) < 2: # No se puede determinar un acorde con una sola clase de altura
         if len(notes) >=2: # Si hay octavas
            return f"{pitch_class_to_name(pitch_classes[0])} Octaves"
         else:
            return pitch_class_to_name(pitch_classes[0]) # Devuelve nota única


    # --- Lógica de Identificación ---
    # Itera a través de cada nota como posible fundamental (raíz)
    possible_chords = []
    for i, potential_root_pc in enumerate(pitch_classes):
        # Calcula los intervalos relativos a esta posible raíz
        intervals = frozenset((pc - potential_root_pc + 12) % 12 for pc in pitch_classes)

        # Busca si este conjunto de intervalos coincide con un acorde conocido
        if intervals in CHORD_INTERVALS:
            chord_type = CHORD_INTERVALS[intervals]
            root_name = pitch_class_to_name(potential_root_pc)
            bass_note_name = pitch_class_to_name(bass_note_midi % 12)

            # Construye el nombre del acorde
            chord_name = f"{root_name} {chord_type}"

            # Añade la notación de inversión si la nota del bajo no es la raíz
            if bass_note_name != root_name:
                chord_name += f" / {bass_note_name}"

            # Podríamos añadir una puntuación basada en la simplicidad, posición, etc.
            # Por ahora, solo guardamos todas las coincidencias válidas.
            possible_chords.append({"name": chord_name, "root": potential_root_pc, "intervals": intervals})

    # --- Selección del Mejor Acorde (Estrategia Simple) ---
    if not possible_chords:
        if len(pitch_classes) == 2:
             # Manejo simple de intervalos (diadas)
             interval = (pitch_classes[1] - pitch_classes[0] + 12) % 12
             # Podrías mapear intervalos a nombres (ej. 7 = Perfect 5th)
             return f"{pitch_class_to_name(pitch_classes[0])} + {pitch_class_to_name(pitch_classes[1])} (interval: {interval})"
        return "Unknown Chord" # No se encontró ninguna coincidencia

    # Estrategia simple: preferir el acorde cuya raíz es la nota más baja tocada.
    # Si no, simplemente devuelve el primero encontrado (que depende del orden de pitch_classes).
    # Una estrategia más avanzada consideraría la simplicidad del acorde, etc.
    bass_note_pc = bass_note_midi % 12
    for chord in possible_chords:
        if chord["root"] == bass_note_pc:
            return chord["name"]

    # Si la nota más baja no es la raíz de ninguno de los acordes encontrados,
    # simplemente devuelve el primer acorde encontrado en la iteración.
    # Esto a menudo corresponde a la inversión más simple.
    return possible_chords[0]["name"]


# --- Bucle Principal de Entrada MIDI ---
def main():
    active_notes = set()
    last_chord_name = None

    try:
        # Listar puertos MIDI de entrada disponibles
        input_ports = mido.get_input_names()
        print("Puertos MIDI de entrada disponibles:")
        if not input_ports:
            print("No se encontraron puertos MIDI de entrada. Asegúrate de que tu dispositivo esté conectado y reconocido.")
            sys.exit(1)

        for i, port_name in enumerate(input_ports):
            print(f"{i}: {port_name}")

        # Pedir al usuario que elija un puerto
        port_index = -1
        while port_index < 0 or port_index >= len(input_ports):
            try:
                choice = input(f"Elige el número del puerto MIDI (0-{len(input_ports)-1}): ")
                port_index = int(choice)
            except ValueError:
                print("Entrada inválida. Por favor ingresa un número.")
            except IndexError:
                 print(f"Número fuera de rango. Por favor ingresa un número entre 0 y {len(input_ports)-1}.")


        port_name = input_ports[port_index]
        print(f"Abriendo puerto: {port_name}")

        with mido.open_input(port_name) as port:
            print("Escuchando mensajes MIDI... Presiona Ctrl+C para salir.")
            while True:
                message_processed = False
                for msg in port.iter_pending(): # Procesa todos los mensajes pendientes sin bloquear
                    if msg.type == 'note_on' and msg.velocity > 0:
                        active_notes.add(msg.note)
                        message_processed = True
                    elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                        active_notes.discard(msg.note) # Usa discard para evitar errores si la nota no estaba
                        message_processed = True

                # Solo identifica el acorde si el conjunto de notas cambió
                if message_processed:
                    current_chord_name = identify_chord(active_notes)

                    # Imprime solo si el acorde identificado ha cambiado
                    if current_chord_name != last_chord_name:
                        active_note_names = sorted([midi_to_note_name(n) for n in active_notes])
                        print(f"Notas activas: {', '.join(active_note_names) or 'Ninguna'} -> Acorde: {current_chord_name or '---'}", end='\r')
                        # Usar \r permite sobrescribir la línea anterior en muchas terminales
                        # Si no funciona bien, usa print normal sin end='\r'
                        last_chord_name = current_chord_name

                # Pequeña pausa para no sobrecargar la CPU en el bucle
                # time.sleep(0.01) # Descomenta si es necesario, iter_pending es no bloqueante

    except KeyboardInterrupt:
        print("\nSaliendo...")
    except Exception as e:
        print(f"\nOcurrió un error: {e}")
        print("Asegúrate de que el backend MIDI (como rtmidi) esté instalado y funcionando.")
        print("Puede que necesites cerrar otras aplicaciones que estén usando el puerto MIDI.")
    finally:
         print("\nPrograma terminado.") # Asegura una línea nueva al final

if __name__ == "__main__":
    main()
