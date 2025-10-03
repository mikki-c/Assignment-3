# HIT137 Assignment 3 — Tkinter GUI + Hugging Face (Multi‑Input)

This project satisfies the requirement to **allow users to select input data (text, image, audio) from a drop‑down, run it through selected AI models, and display the output**, using **two+ free Hugging Face models from different categories**. It also demonstrates **OOP concepts** (inheritance, polymorphism, encapsulation, overriding, decorators) and splits the code across multiple files.

## Features
- Input Type dropdown: **Text**, **Image**, **Audio**
- Model dropdown updates automatically per input type
- Text analysis with **DistilBERT sentiment**
- Image classification with **ViT base**
- Audio transcription with **Whisper tiny.en**
- Result panel and image preview
- OOP explanations dialog

## Files
- `main.py` — entry point
- `gui.py` — Tkinter interface
- `models.py` — model registry, handlers, manager
- `oop_explanations.py` — OOP explanation text
- `requirements.txt` — dependencies

## How to Run
```bash
# (Optional) create & activate a venv
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Launch the app
python main.py
```

> The first run will download the selected Hugging Face models to your cache (~100–500MB depending on which ones you use).

## Notes
- Audio models (Whisper) may require `ffmpeg` to be installed on your system.
- If GPU is available, `transformers` will use it automatically via PyTorch.
- If your environment cannot install heavy dependencies, you can comment out the audio model in `Registry._MODELS` to keep it light.
