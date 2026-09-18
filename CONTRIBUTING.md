# Contributing to Surgisight / Cómo colaborar

**English below · Español abajo**

Surgisight is built by surgeons and engineers together. You do not need to write
code to make it better.

---

## English

### Ways to help

**Clinical (highest value right now)**
- Open an issue describing what a scribe should capture in your subspecialty.
- Report where the AI-drafted note is wrong, incomplete or unsafe. Paste a
  **de-identified** example.
- Propose the instrument / anatomy label set for a vitreoretinal detection model.
- Share de-identified microscope footage you have consent and ethics approval to
  share (open an issue first — do not attach patient data to a public issue).

**Technical**
- Train and publish YOLO weights for surgical instruments and ocular anatomy.
- Add offline speech-to-text so wake-word detection doesn't need the cloud.
- Port the text-to-speech layer beyond macOS (Linux / Windows).
- Improve the operative-note prompt for other subspecialties.

### Ground rules

1. **Never commit patient data.** No video, stills, notes, names, MRNs or dates
   of birth — in code, issues or pull requests. `.gitignore` blocks the output
   folders; please don't work around it.
2. **Never commit secrets.** API keys go in `.env`, which is git-ignored.
3. **No clinical claims without evidence.** This is a prototype. If you add a
   feature, describe what it actually does, not what it might one day do.
4. Be respectful. Assume good faith. English and Spanish are both fine.

### Pull requests

Fork → branch → commit → open a PR describing the clinical or technical problem
you are solving. Small PRs get merged faster.

---

## Español

### Formas de ayudar

**Clínicas (lo más valioso ahora mismo)**
- Abra un issue describiendo qué debería capturar un escriba en su subespecialidad.
- Reporte dónde la nota generada por la IA es incorrecta, incompleta o insegura.
  Pegue un ejemplo **desidentificado**.
- Proponga el conjunto de etiquetas de instrumental / anatomía para un modelo de
  detección vitreorretiniano.
- Comparta video de microscopio desidentificado que tenga consentimiento y
  aprobación ética para compartir (abra primero un issue — no adjunte datos de
  pacientes en un issue público).

**Técnicas**
- Entrene y publique pesos YOLO para instrumental quirúrgico y anatomía ocular.
- Agregue reconocimiento de voz offline para que la palabra clave no dependa de
  la nube.
- Lleve la capa de voz más allá de macOS (Linux / Windows).
- Mejore el prompt de la nota operatoria para otras subespecialidades.

### Reglas básicas

1. **Nunca suba datos de pacientes.** Ni video, imágenes, notas, nombres,
   expedientes ni fechas de nacimiento — en código, issues o pull requests.
   `.gitignore` bloquea las carpetas de salida; por favor no lo evada.
2. **Nunca suba secretos.** Las API keys van en `.env`, que está en `.gitignore`.
3. **Sin afirmaciones clínicas sin evidencia.** Esto es un prototipo. Si agrega
   una función, describa lo que realmente hace, no lo que podría llegar a hacer.
4. Trato respetuoso, buena fe. Español e inglés son igual de bienvenidos.

### Pull requests

Fork → rama → commit → abra un PR describiendo el problema clínico o técnico que
resuelve. Los PR pequeños se integran más rápido.
