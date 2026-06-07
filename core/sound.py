import threading
import pyttsx3

_is_speaking = False


def _speak(text, rate=150, volume=0.9):
    """
    Speaks text using Windows text-to-speech engine.
    Runs in background thread so it never blocks UI.
    Prevents duplicate speech with a lock flag.
    """
    global _is_speaking

    if _is_speaking:
        return

    def _run():
        global _is_speaking
        _is_speaking = True
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', rate)
            engine.setProperty('volume', volume)
            voices = engine.getProperty('voices')
            for voice in voices:
                if 'english' in voice.name.lower() or 'david' in voice.name.lower():
                    engine.setProperty('voice', voice.id)
                    break
            engine.say(text)
            engine.runAndWait()
            engine.stop()
        except Exception as e:
            print(f"[Sound] Error: {e}")
        finally:
            _is_speaking = False

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()


def play_success():
    """Says 'Successfully Scanned' once after scan completes."""
    _speak("Successfully Scanned")


def play_scanning():
    """Says 'Scanning' once when scan starts."""
    _speak("Scanning", rate=170)


def play_error():
    """Says 'Scan Failed' once on error."""
    _speak("Scan Failed")