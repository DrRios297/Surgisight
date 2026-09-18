"""
Surgisight - Open-Source AI Surgical Copilot
"Scribe & Record" mode: observes, listens, logs, and drafts an operative note.

EXPERIMENTAL RESEARCH PROTOTYPE. NOT A MEDICAL DEVICE.
Not FDA / EMA / COFEPRIS approved. The surgeon remains fully responsible for
all clinical decisions. See DISCLAIMER in README.md before any clinical use.

License: MIT
"""

import os
import sys
import time
import threading
import subprocess
from datetime import datetime

import cv2
import PIL.Image
import speech_recognition as sr
from google import genai
from ultralytics import YOLO

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # .env support is optional

# ==========================================
# --- USER CONFIGURATION ---
# ==========================================
# 1 = external capture card (Elgato Cam Link), 0 = built-in webcam.
CAMERA_INDEX = int(os.getenv("SURGISIGHT_CAMERA_INDEX", "1"))

# NEVER hard-code your API key here. Put it in a .env file (see .env.example).
API_KEY = os.getenv("GEMINI_API_KEY", "")

MODEL_ID = os.getenv("SURGISIGHT_MODEL", "gemini-3.5-flash")

# "en" or "es". Controls the AI's reply language and the macOS voice.
LANGUAGE = os.getenv("SURGISIGHT_LANGUAGE", "en").lower()

RECORD_VIDEO = os.getenv("SURGISIGHT_RECORD_VIDEO", "true").lower() == "true"
SAVE_TRAINING_DATA = os.getenv("SURGISIGHT_SAVE_TRAINING_DATA", "true").lower() == "true"

REPORTS_FOLDER = os.getenv("SURGISIGHT_REPORTS_FOLDER", "surgical_reports")
TRAINING_DATA_FOLDER = os.getenv("SURGISIGHT_TRAINING_FOLDER", "training_dataset")

YOLO_WEIGHTS = os.getenv("SURGISIGHT_YOLO_WEIGHTS", "yolov8n.pt")
# ==========================================

VOICE = {"en": "Alex", "es": "Paulina"}.get(LANGUAGE, "Alex")
STT_LANG = {"en": "en-US", "es": "es-MX"}.get(LANGUAGE, "en-US")
LANG_NAME = {"en": "English", "es": "Spanish"}.get(LANGUAGE, "English")

WAKE_WORDS = [
    "surgisight", "surge site", "surgery sight", "serge sight", "surgi sight",
    "surgisait", "cirugisight", "finish surgery", "terminar cirugia",
    "terminar cirugía",
]

# --- Startup checks -----------------------------------------------------
if not API_KEY:
    print(
        "\nERROR: No Gemini API key found.\n"
        "  1. Copy .env.example to .env\n"
        "  2. Put your key in it:  GEMINI_API_KEY=AIzaSy...\n"
        "  3. Run again.\n"
        "Get a key at https://aistudio.google.com/\n"
    )
    sys.exit(1)

client = genai.Client(api_key=API_KEY)
yolo_model = YOLO(YOLO_WEIGHTS)

surgery_active = True
surgical_log = []
global_frame = None
frame_lock = threading.Lock()

os.makedirs(REPORTS_FOLDER, exist_ok=True)
if SAVE_TRAINING_DATA:
    os.makedirs(TRAINING_DATA_FOLDER, exist_ok=True)

# Unique subfolder for THIS surgery
date_str = datetime.now().strftime("%Y-%m-%d_%H-%M")
surgery_session_folder = os.path.join(REPORTS_FOLDER, f"Surgery_{date_str}")
os.makedirs(surgery_session_folder, exist_ok=True)


def speak(text):
    """Speak via the macOS 'say' command, without blocking and without shell injection."""
    if sys.platform != "darwin":
        return
    try:
        subprocess.Popen(["say", "-v", VOICE, text],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"[TTS ERROR]: {e}")


def generate_operative_note():
    if not surgical_log:
        print("No dictation was logged. No operative note generated.")
        return

    print("\n" + "=" * 50)
    print("GENERATING OFFICIAL SURGICAL NOTE WITH AI...")
    print("=" * 50)

    log_text = "\n".join(surgical_log)
    prompt_report = (
        "You are an expert ophthalmologist surgeon. Below is the chronological log of a surgery. "
        "The log contains steps dictated by the surgeon and observations made by the AI:\n\n"
        f"{log_text}\n\n"
        "Based on this, draft a formal structured Surgical Operative Note with:\n"
        "- SURGICAL TECHNIQUE / PROCEDURE (Describe the steps clearly based on the log)\n"
        "- INTRAOPERATIVE FINDINGS\n"
        "- COMPLICATIONS / INCIDENTS (or 'None reported')\n"
        f"Use impeccable formal medical language in {LANG_NAME}."
    )

    file_path = os.path.join(surgery_session_folder, f"Surgical_Note_{date_str}.txt")
    try:
        response = client.models.generate_content(model=MODEL_ID, contents=prompt_report)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("=== OPERATIVE NOTE - SURGISIGHT AI (DRAFT) ===\n")
            f.write("AI-generated draft. Must be reviewed, corrected and signed\n")
            f.write("by the responsible surgeon before entering the medical record.\n\n")
            f.write(response.text.strip())
        print(f"\nSUCCESS! Note archived at: {file_path}\n")
        speak("Surgical note generated and saved successfully.")
    except Exception as e:
        # Never lose the raw log because the API failed.
        raw_path = os.path.join(surgery_session_folder, f"Raw_Log_{date_str}.txt")
        with open(raw_path, "w", encoding="utf-8") as f:
            f.write(log_text)
        print(f"Error generating note: {e}")
        print(f"Raw dictation log saved instead at: {raw_path}")


def process_voice_command(audio_bytes, captured_frame):
    global surgery_active
    try:
        img = None
        if captured_frame is not None:
            stamp = time.strftime("%H-%M-%S")
            snapshot_path = os.path.join(surgery_session_folder, f"snapshot_{stamp}.jpg")
            cv2.imwrite(snapshot_path, captured_frame)
            if SAVE_TRAINING_DATA:
                cv2.imwrite(
                    os.path.join(TRAINING_DATA_FOLDER, f"train_{date_str}_{stamp}.jpg"),
                    captured_frame,
                )
            img = PIL.Image.open(snapshot_path)

        prompt = (
            "You are 'Surgisight', an expert surgical AI copilot. You are listening to the "
            "surgeon and looking at the live microscope feed.\n"
            "Rules:\n"
            f"1. If the surgeon is dictating a step or teaching, acknowledge it briefly in {LANG_NAME} "
            "(e.g., 'Noted: Membrane peeling initiated.').\n"
            f"2. If the surgeon asks a question, answer clinically in a maximum of 2 lines in {LANG_NAME}.\n"
            "3. If the surgeon says 'finish surgery', 'end surgery', 'close case' or "
            "'terminar cirugia', reply ONLY with 'TERMINATE'.\n"
            "4. If it's background noise or irrelevant chatter, reply ONLY with 'IGNORE'."
        )

        contents = [prompt, genai.types.Part.from_bytes(data=audio_bytes, mime_type="audio/wav")]
        if img is not None:
            contents.append(img)

        response = client.models.generate_content(model=MODEL_ID, contents=contents)
        text_response = (response.text or "").strip()
        current_time = time.strftime("%H:%M:%S")

        if not text_response or "IGNORE" in text_response.upper():
            return

        if "TERMINATE" in text_response.upper():
            print(f"\n[{current_time}] Closing command detected.")
            speak("Command received. Ending surgery and saving all files.")
            surgery_active = False
            return

        print(f"\n[SURGISIGHT {current_time}]: {text_response}\n")
        speak(text_response)
        surgical_log.append(f"[{current_time}] Surgeon dictation -> Surgisight logged: {text_response}")

    except Exception as e:
        print(f"[VOICE ERROR]: {e}")


def microphone_thread():
    global surgery_active
    r = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        print("\n[CALIBRATING MICROPHONE... please remain silent for 2 seconds]")
        r.adjust_for_ambient_noise(source, duration=2)
        r.energy_threshold += 150
        print("[SURGISIGHT READY]: say 'Surgisight...' to interact.")

    while surgery_active:
        try:
            with mic as source:
                audio = r.listen(source, timeout=1, phrase_time_limit=10)

            audio_bytes = audio.get_wav_data()
            with frame_lock:
                current_f = global_frame.copy() if global_frame is not None else None

            # Cheap local filter: only call Gemini if the wake word was heard.
            try:
                transcript = r.recognize_google(audio, language=STT_LANG).lower()
            except sr.UnknownValueError:
                continue
            except Exception as e:
                print(f"[STT ERROR]: {e}")
                continue

            if any(word in transcript for word in WAKE_WORDS):
                print(f"[WAKE WORD DETECTED]: '{transcript}'")
                threading.Thread(
                    target=process_voice_command,
                    args=(audio_bytes, current_f),
                    daemon=True,
                ).start()

        except sr.WaitTimeoutError:
            continue
        except Exception as e:
            print(f"[MIC ERROR]: {e}")
            time.sleep(0.5)

    print("Microphone thread stopped.")


def main():
    global surgery_active, global_frame

    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print(
            f"\nERROR: could not open camera index {CAMERA_INDEX}.\n"
            "  - Check that the capture card is connected and the microscope is sending image.\n"
            "  - Try another index: SURGISIGHT_CAMERA_INDEX=0 python surgical_copilot.py\n"
            "  - On macOS, allow camera access for Terminal in System Settings > Privacy & Security.\n"
        )
        return

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = 30

    out_video = None
    if RECORD_VIDEO:
        fourcc = cv2.VideoWriter_fourcc(*"avc1")
        video_path = os.path.join(surgery_session_folder, f"Surgery_Video_{date_str}.mp4")
        out_video = cv2.VideoWriter(video_path, fourcc, fps, (frame_width, frame_height))
        if not out_video.isOpened():
            print("WARNING: VideoWriter failed to initialize. Recording disabled.")
            out_video = None
        else:
            print(f"RECORDER ON: saving video to {video_path}")
    else:
        print("RECORDER OFF (SURGISIGHT_RECORD_VIDEO=false)")

    threading.Thread(target=microphone_thread, daemon=True).start()

    print("\n=== SURGISIGHT LIVE (SCRIBE & RECORD MODE) ===")
    print("RESEARCH PROTOTYPE - NOT A MEDICAL DEVICE. Do not use for clinical decisions.")
    print("Finish: say 'Surgisight, finish surgery' or press 'q' on the video window.")
    print("=" * 52 + "\n")

    try:
        while surgery_active:
            ret, frame = cap.read()
            if not ret:
                print("Video stream lost.")
                break

            with frame_lock:
                global_frame = frame.copy()

            if out_video is not None:
                out_video.write(frame)

            results = yolo_model(frame, verbose=False)
            cv2.imshow("Surgisight Monitor", results[0].plot())

            if cv2.waitKey(1) & 0xFF == ord("q"):
                surgery_active = False
                break
    except KeyboardInterrupt:
        surgery_active = False
    finally:
        surgery_active = False
        cap.release()
        if out_video is not None:
            out_video.release()
        cv2.destroyAllWindows()
        generate_operative_note()
        print("System safely shut down.")


if __name__ == "__main__":
    main()
