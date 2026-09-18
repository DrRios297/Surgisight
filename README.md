# Surgisight — An Open-Source AI Surgical Copilot

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Status](https://img.shields.io/badge/status-research%20prototype-orange)
![Platform](https://img.shields.io/badge/platform-macOS%20(Apple%20Silicon)-lightgrey)

**Español: [README.es.md](README.es.md)**

Surgisight turns a standard surgical microscope into a voice-activated scribe.
It watches the live microscope feed, listens to the surgeon's dictation, and at
the end of the case it drafts a structured operative note and saves it next to
the full surgery video.

This is the **"Scribe & Record"** model: it observes and documents. It does not
advise, it does not intervene, and it is not a decision-support system.

> ### ⚠️ Read this first
> Surgisight is an **experimental research prototype**. It is **not** an
> FDA / EMA / COFEPRIS-approved medical device and must not be used to make
> clinical decisions. Every note it produces is a **draft** that the responsible
> surgeon must review, correct and sign. Microscope images and surgeon audio are
> sent to a third-party cloud API (Google Gemini) — see
> [Patient data & privacy](#-patient-data--privacy) before using it on a real case.

---

## ✨ What it does

| Feature | Status |
|---|---|
| **Hands-free voice scribe** — wake word `"Surgisight"`, logs every dictated step without breaking sterility | ✅ Working |
| **Automated operative note** — say *"Surgisight, finish surgery"* and it drafts a structured note | ✅ Working |
| **Full video recording** — the whole case saved as MP4 in a timestamped folder | ✅ Working |
| **Q&A during surgery** — ask a clinical question, get a 2-line answer with the current frame as context | ✅ Working |
| **Learning dataset** — every interaction saves the paired image + text for future fine-tuning | ✅ Working |
| **Real-time instrument & anatomy tracking** — currently runs generic YOLOv8 (COCO) weights, so the overlay is a **technical demo only**; it does not yet recognise surgical instruments or ocular anatomy | 🚧 Roadmap — [help wanted](#-how-to-contribute) |

---

## 🛠 Hardware

- **Computer:** Mac with Apple Silicon (M1–M4). Other platforms may work but the
  text-to-speech feedback is macOS-only.
- **Capture card:** Elgato Cam Link 4K, or any UVC-compliant HDMI capture device.
- **Microscope:** any surgical microscope with a clean HDMI output.
- **Microphone:** the built-in Mac mic is fine in a quiet room. An external mic
  is strongly recommended in a real OR.

---

## ⚙️ Installation (macOS, ~10 minutes)

### 1. Get a Google AI API key

1. Go to [Google AI Studio](https://aistudio.google.com/).
2. Sign in → **Get API key** → create a new project.
3. **Enable billing** on the project to unlock the multimodal models.
   Typical cost is a few cents per case.
4. Copy the key (it looks like `AIzaSy...`).

### 2. Install system dependencies

If you don't have [Homebrew](https://brew.sh), install it first. Then:

```bash
brew install portaudio flac
```

### 3. Set up the project

```bash
git clone https://github.com/USERNAME/surgisight.git
cd surgisight

python3 -m venv venv_copilot
source venv_copilot/bin/activate

pip install -r requirements.txt
```

### 4. Add your API key

```bash
cp .env.example .env
```

Open `.env` in any text editor and paste your key:

```
GEMINI_API_KEY=AIzaSy_your_real_key_here
```

`.env` is git-ignored — your key never leaves your machine.

### 5. Run

Connect the capture card and confirm the microscope is sending a live image, then:

```bash
python surgical_copilot.py
```

On first launch macOS will ask for **camera** and **microphone** permission for
Terminal. Grant both, then run it again.

---

## 🎙 How to use it

| Action | What to say / do |
|---|---|
| **Start** | Just run the script. It auto-calibrates the mic for 2 seconds — stay quiet. |
| **Dictate a step** | *"Surgisight, I am now performing an ILM peel."* |
| **Ask a question** | *"Surgisight, what is the recommended tamponade for this tear?"* |
| **Finish** | *"Surgisight, finish surgery"* — or press `q` on the video window. |

Everything lands in `surgical_reports/Surgery_YYYY-MM-DD_HH-MM/`:
the MP4, the snapshots, and `Surgical_Note_*.txt`.

---

## 🔒 Patient data & privacy

Please read this before using Surgisight on a real patient.

- **Data leaves your machine.** When you speak the wake word, Surgisight uploads
  a short audio clip and one microscope frame to Google's Gemini API, and the
  audio clip to Google's speech recognition service for wake-word filtering.
- **Local files may contain PHI.** `surgical_reports/` and `training_dataset/`
  hold video, stills and notes. `.gitignore` blocks them from Git, but you are
  responsible for storing and disposing of them under your local law
  (HIPAA, GDPR, LFPDPPP, etc.).
- **Get consent and ethics approval.** Recording surgery and sending it to a
  third-party API generally requires informed patient consent and, for research
  use, IRB / ethics committee approval.
- **De-identify.** Keep patient names, MRNs and dates of birth out of your
  dictation. Do not point the microscope at anything identifying.
- **Turn recording off if you don't need it:** set `SURGISIGHT_RECORD_VIDEO=false`
  and `SURGISIGHT_SAVE_TRAINING_DATA=false` in `.env`.

---

## 🧯 Troubleshooting

| Problem | Fix |
|---|---|
| `could not open camera index 1` | Try `SURGISIGHT_CAMERA_INDEX=0` in `.env`. Check the capture card is plugged in and that Terminal has camera permission. |
| `No Gemini API key found` | You skipped step 4. Copy `.env.example` to `.env` and add your key. |
| `pip install pyaudio` fails | Run `brew install portaudio` first, then reinstall. |
| It never hears the wake word | Use an external mic, or say "Surgisight" a little louder and leave a short pause before the sentence. |
| `VideoWriter failed to initialize` | The `avc1` codec is unavailable. Everything else still works; only the MP4 is skipped. |
| It ignores everything | The wake word filter needs internet (it uses Google speech recognition). Check your connection. |

---

## ⚙️ Configuration

All settings live in `.env` (see `.env.example`):

| Variable | Default | Meaning |
|---|---|---|
| `GEMINI_API_KEY` | — | **Required.** Your Google AI key. |
| `SURGISIGHT_CAMERA_INDEX` | `1` | `1` for capture card, `0` for built-in webcam. |
| `SURGISIGHT_MODEL` | `gemini-3.5-flash` | Any current Gemini model ID. |
| `SURGISIGHT_LANGUAGE` | `en` | `en` or `es`. Sets the AI's reply language and the voice. |
| `SURGISIGHT_RECORD_VIDEO` | `true` | Set `false` to disable video recording. |
| `SURGISIGHT_SAVE_TRAINING_DATA` | `true` | Set `false` to stop saving training images. |

---

## 🤝 How to contribute

You do not need to be a programmer to help. The single most valuable
contribution right now is **clinical**.

**If you are a surgeon:**
- Open an [issue](../../issues) describing what you'd want a scribe to capture
  in your subspecialty.
- Tell us where the drafted note is wrong, thin or unsafe — paste a de-identified
  example.
- Propose the instrument and anatomy labels a vitreoretinal detection model
  should use.

**If you are a developer or ML engineer:**
- Train and share YOLO weights for surgical instruments and ocular anatomy
  (the biggest open gap — see the roadmap table above).
- Add a local/offline speech-to-text path so the wake-word filter doesn't need
  the cloud.
- Port the text-to-speech layer beyond macOS.

Fork it, branch it, open a pull request. Discussion in English or Spanish is
equally welcome.

---

## 🗺 Roadmap

- [ ] Vitreoretinal instrument + anatomy detection model (replaces generic YOLOv8)
- [ ] Fully offline mode (local STT + local LLM) for privacy-sensitive sites
- [ ] Structured note export (PDF / HL7 / FHIR)
- [ ] Multi-surgeon voice separation
- [ ] Validation study against surgeon-written operative notes

---

## 📄 License

MIT — see [LICENSE](LICENSE).

Surgisight is an experimental prototype for research and educational purposes.
It is not an FDA / EMA / COFEPRIS-approved medical device. The surgeon remains
fully responsible for all clinical decisions and for the accuracy of any note
entered into the medical record.
