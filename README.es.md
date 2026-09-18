# Surgisight — Copiloto Quirúrgico de IA de Código Abierto

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Status](https://img.shields.io/badge/estado-prototipo%20de%20investigaci%C3%B3n-orange)
![Platform](https://img.shields.io/badge/plataforma-macOS%20(Apple%20Silicon)-lightgrey)

**English: [README.md](README.md)**

Surgisight convierte un microscopio quirúrgico estándar en un escriba activado
por voz. Observa la imagen en vivo del microscopio, escucha el dictado del
cirujano y, al terminar el caso, redacta un borrador de nota operatoria
estructurada y lo guarda junto al video completo de la cirugía.

Este es el modelo **"Scribe & Record"** (observar y documentar). No aconseja,
no interviene y no es un sistema de apoyo a la decisión clínica.

> ### ⚠️ Léase primero
> Surgisight es un **prototipo experimental de investigación**. **No** es un
> dispositivo médico aprobado por FDA / EMA / COFEPRIS y no debe usarse para
> tomar decisiones clínicas. Toda nota que produce es un **borrador** que el
> cirujano responsable debe revisar, corregir y firmar. Las imágenes del
> microscopio y el audio del cirujano se envían a una API en la nube de un
> tercero (Google Gemini) — lea
> [Datos del paciente y privacidad](#-datos-del-paciente-y-privacidad) antes de
> usarlo en un caso real.

---

## ✨ Qué hace

| Función | Estado |
|---|---|
| **Escriba por voz, sin manos** — palabra clave `"Surgisight"`, registra cada paso dictado sin romper la esterilidad | ✅ Funcional |
| **Nota operatoria automática** — diga *"Surgisight, terminar cirugía"* y redacta la nota estructurada | ✅ Funcional |
| **Grabación completa del video** — todo el caso en MP4, en una carpeta con fecha y hora | ✅ Funcional |
| **Preguntas durante la cirugía** — pregunte algo clínico y recibe una respuesta de 2 líneas usando la imagen actual como contexto | ✅ Funcional |
| **Dataset de aprendizaje** — cada interacción guarda el par imagen + texto para afinar modelos propios más adelante | ✅ Funcional |
| **Seguimiento de instrumentos y anatomía en tiempo real** — actualmente corre pesos genéricos de YOLOv8 (COCO), así que el overlay es **solo una demostración técnica**; todavía no reconoce instrumental quirúrgico ni anatomía ocular | 🚧 En hoja de ruta — [se busca ayuda](#-cómo-colaborar) |

---

## 🛠 Hardware

- **Computadora:** Mac con Apple Silicon (M1–M4). Otras plataformas pueden
  funcionar, pero la retroalimentación por voz solo existe en macOS.
- **Capturadora:** Elgato Cam Link 4K, o cualquier capturadora HDMI compatible
  con UVC.
- **Microscopio:** cualquier microscopio quirúrgico con salida HDMI limpia.
- **Micrófono:** el integrado de la Mac funciona en un cuarto silencioso. En un
  quirófano real se recomienda mucho un micrófono externo.

---

## ⚙️ Instalación (macOS, ~10 minutos)

### 1. Obtenga una API key de Google AI

1. Entre a [Google AI Studio](https://aistudio.google.com/).
2. Inicie sesión → **Get API key** → cree un proyecto nuevo.
3. **Active la facturación** del proyecto para desbloquear los modelos
   multimodales. El costo típico es de unos centavos por caso.
4. Copie la llave (se ve como `AIzaSy...`).

### 2. Instale las dependencias del sistema

Si no tiene [Homebrew](https://brew.sh), instálelo primero. Después:

```bash
brew install portaudio flac
```

### 3. Prepare el proyecto

```bash
git clone https://github.com/USUARIO/surgisight.git
cd surgisight

python3 -m venv venv_copilot
source venv_copilot/bin/activate

pip install -r requirements.txt
```

### 4. Agregue su API key

```bash
cp .env.example .env
```

Abra `.env` en cualquier editor de texto y pegue su llave:

```
GEMINI_API_KEY=AIzaSy_su_llave_real_aqui
```

`.env` está en `.gitignore` — su llave nunca sale de su computadora.

### 5. Ejecute

Conecte la capturadora, confirme que el microscopio está enviando imagen en
vivo y luego:

```bash
python surgical_copilot.py
```

La primera vez, macOS pedirá permiso de **cámara** y **micrófono** para
Terminal. Concédalos y vuelva a ejecutar.

---

## 🎙 Cómo usarlo

| Acción | Qué decir / hacer |
|---|---|
| **Iniciar** | Solo ejecute el script. Calibra el micrófono 2 segundos — guarde silencio. |
| **Dictar un paso** | *"Surgisight, estoy realizando el pelado de la MLI."* |
| **Preguntar** | *"Surgisight, ¿cuál es el taponamiento recomendado para este desgarro?"* |
| **Terminar** | *"Surgisight, terminar cirugía"* — o presione `q` en la ventana de video. |

Todo queda en `surgical_reports/Surgery_AAAA-MM-DD_HH-MM/`: el MP4, las
capturas y `Surgical_Note_*.txt`.

Para que el sistema responda en español, ponga `SURGISIGHT_LANGUAGE=es` en su
archivo `.env`.

---

## 🔒 Datos del paciente y privacidad

Por favor lea esto antes de usar Surgisight con un paciente real.

- **Los datos salen de su computadora.** Al decir la palabra clave, Surgisight
  sube un fragmento corto de audio y un cuadro del microscopio a la API de
  Gemini de Google, y el audio al servicio de reconocimiento de voz de Google
  para filtrar la palabra clave.
- **Los archivos locales pueden contener datos del paciente.**
  `surgical_reports/` y `training_dataset/` guardan video, imágenes y notas.
  `.gitignore` los bloquea de Git, pero usted es responsable de almacenarlos y
  eliminarlos conforme a su legislación local (LFPDPPP, HIPAA, GDPR, etc.).
- **Obtenga consentimiento y aprobación ética.** Grabar cirugía y enviarla a una
  API de terceros normalmente requiere consentimiento informado del paciente y,
  para uso en investigación, aprobación del comité de ética.
- **Desidentifique.** Mantenga nombres, números de expediente y fechas de
  nacimiento fuera del dictado. No enfoque el microscopio hacia nada que
  identifique al paciente.
- **Apague la grabación si no la necesita:** ponga
  `SURGISIGHT_RECORD_VIDEO=false` y `SURGISIGHT_SAVE_TRAINING_DATA=false` en `.env`.

---

## 🧯 Solución de problemas

| Problema | Solución |
|---|---|
| `could not open camera index 1` | Pruebe `SURGISIGHT_CAMERA_INDEX=0` en `.env`. Verifique que la capturadora esté conectada y que Terminal tenga permiso de cámara. |
| `No Gemini API key found` | Se saltó el paso 4. Copie `.env.example` a `.env` y agregue su llave. |
| Falla `pip install pyaudio` | Ejecute primero `brew install portaudio` y reinstale. |
| Nunca escucha la palabra clave | Use micrófono externo, o diga "Surgisight" un poco más fuerte y deje una pausa breve antes de la frase. |
| `VideoWriter failed to initialize` | El códec `avc1` no está disponible. Todo lo demás sigue funcionando; solo se omite el MP4. |
| Ignora todo | El filtro de palabra clave necesita internet (usa el reconocimiento de voz de Google). Revise su conexión. |

---

## ⚙️ Configuración

Todos los ajustes viven en `.env` (vea `.env.example`):

| Variable | Default | Significado |
|---|---|---|
| `GEMINI_API_KEY` | — | **Obligatoria.** Su llave de Google AI. |
| `SURGISIGHT_CAMERA_INDEX` | `1` | `1` para capturadora, `0` para webcam integrada. |
| `SURGISIGHT_MODEL` | `gemini-3.5-flash` | Cualquier ID de modelo Gemini vigente. |
| `SURGISIGHT_LANGUAGE` | `en` | `en` o `es`. Define el idioma de respuesta y la voz. |
| `SURGISIGHT_RECORD_VIDEO` | `true` | `false` para desactivar la grabación de video. |
| `SURGISIGHT_SAVE_TRAINING_DATA` | `true` | `false` para dejar de guardar imágenes de entrenamiento. |

---

## 🤝 Cómo colaborar

No hace falta ser programador para ayudar. La contribución más valiosa en este
momento es **clínica**.

**Si usted es cirujano:**
- Abra un [issue](../../issues) describiendo qué debería capturar un escriba en
  su subespecialidad.
- Díganos dónde la nota generada resulta incorrecta, pobre o insegura — pegue un
  ejemplo desidentificado.
- Proponga las etiquetas de instrumental y anatomía que debería usar un modelo
  de detección vitreorretiniano.

**Si usted es desarrollador o ingeniero de ML:**
- Entrene y comparta pesos YOLO para instrumental quirúrgico y anatomía ocular
  (el mayor hueco abierto — vea la hoja de ruta arriba).
- Agregue reconocimiento de voz local/offline para que el filtro de palabra clave
  no dependa de la nube.
- Lleve la capa de voz más allá de macOS.

Haga fork, cree una rama y abra un pull request. Se recibe igual de bien la
discusión en español o en inglés.

---

## 🗺 Hoja de ruta

- [ ] Modelo de detección de instrumental y anatomía vitreorretiniana (reemplaza al YOLOv8 genérico)
- [ ] Modo totalmente offline (STT local + LLM local) para sedes sensibles a la privacidad
- [ ] Exportación estructurada de la nota (PDF / HL7 / FHIR)
- [ ] Separación de voces entre varios cirujanos
- [ ] Estudio de validación contra notas operatorias escritas por el cirujano

---

## 📄 Licencia

MIT — vea [LICENSE](LICENSE).

Surgisight es un prototipo experimental con fines de investigación y educación.
No es un dispositivo médico aprobado por FDA / EMA / COFEPRIS. El cirujano
conserva la responsabilidad total sobre todas las decisiones clínicas y sobre la
exactitud de cualquier nota que se integre al expediente médico.
