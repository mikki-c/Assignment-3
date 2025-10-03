import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import threading
from models import (
    Registry,
    InputType,
    ModelCategory,
    ModelManager,
    load_image_from_path,
    read_audio_bytes,
)
from oop_explanations import get_oop_explanations


class AppGUI:
    """
    Top-level GUI class (encapsulation of the UI).

    Demonstrates:
      - Encapsulation: all UI state & behavior inside this class.
      - Composition: Holds a ModelManager instance to run models.
      - Separation of concerns: UI vs model logic.
    """
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("HIT137 - HF Models Tkinter GUI")
        self.root.geometry("980x680")

        # Manager that abstracts model loading/execution
        self.model_manager = ModelManager()

        # --- State ---
        self.input_type_var = tk.StringVar(value=InputType.TEXT.value)
        self.model_var = tk.StringVar()
        self.model_info_var = tk.StringVar(value="Select a model to see info.")
        self.status_var = tk.StringVar(value="Ready.")
        self.text_input = tk.StringVar(value="Type something to analyze sentiment!")
        self.selected_file_path = tk.StringVar(value="")

        # Build UI
        self._build_menu()
        self._build_toolbar()
        self._build_io_frames()
        self._build_output_frames()
        self._populate_models_dropdown()

    def run(self):
        self.root.mainloop()

    # ----------------- UI Builders -----------------
    def _build_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="OOP Explanations", command=self._show_oop_dialog)
        help_menu.add_command(label="About", command=self._show_about)
        menubar.add_cascade(label="Help", menu=help_menu)

    def _build_toolbar(self):
        frm = ttk.Frame(self.root, padding=8)
        frm.pack(fill="x")

        ttk.Label(frm, text="Input Type:").pack(side="left")
        cmb = ttk.Combobox(frm, textvariable=self.input_type_var, width=18, state="readonly")
        cmb["values"] = [x.value for x in InputType]
        cmb.pack(side="left", padx=6)
        cmb.bind("<<ComboboxSelected>>", lambda e: self._on_input_type_change())

        ttk.Label(frm, text="Model:").pack(side="left", padx=(16, 0))
        self.model_combo = ttk.Combobox(frm, textvariable=self.model_var, width=40, state="readonly")
        self.model_combo.pack(side="left", padx=6)
        self.model_combo.bind("<<ComboboxSelected>>", lambda e: self._on_model_change())

        self.run_btn = ttk.Button(frm, text="Run Model", command=self._run_clicked)
        self.run_btn.pack(side="right")

        ttk.Label(frm, textvariable=self.status_var).pack(side="right", padx=12)

    def _build_io_frames(self):
        container = ttk.Frame(self.root, padding=8)
        container.pack(fill="x")

        # Left: Input panel (text or file picker)
        self.input_frame = ttk.LabelFrame(container, text="Input", padding=8)
        self.input_frame.pack(fill="x")

        # For text
        self.text_entry = ttk.Entry(self.input_frame, textvariable=self.text_input)
        self.text_entry.pack(fill="x")

        # For file selection (image/audio)
        self.file_row = ttk.Frame(self.input_frame)
        self.file_row.pack(fill="x", pady=6)
        ttk.Label(self.file_row, text="File:").pack(side="left")
        self.file_entry = ttk.Entry(self.file_row, textvariable=self.selected_file_path)
        self.file_entry.pack(side="left", fill="x", expand=True, padx=6)
        ttk.Button(self.file_row, text="Browse...", command=self._browse_file).pack(side="left")

        self._update_input_widgets_visibility()

    def _build_output_frames(self):
        container = ttk.Frame(self.root, padding=8)
        container.pack(fill="both", expand=True)

        # Left: Results (textual)
        left = ttk.Frame(container)
        left.pack(side="left", fill="both", expand=True)

        self.results_frame = ttk.LabelFrame(left, text="Model Output", padding=8)
        self.results_frame.pack(fill="both", expand=True)

        self.output_text = tk.Text(self.results_frame, wrap="word", height=14)
        self.output_text.pack(fill="both", expand=True)

        # Right: Image preview (for image input)
        right = ttk.Frame(container)
        right.pack(side="left", fill="both", expand=False)

        self.preview_frame = ttk.LabelFrame(right, text="Preview (Image)", padding=8)
        self.preview_frame.pack(fill="both", expand=True)
        self.preview_label = ttk.Label(self.preview_frame)
        self.preview_label.pack()

        # Bottom: Model info
        info_frame = ttk.LabelFrame(self.root, text="Model Information", padding=8)
        info_frame.pack(fill="x")
        self.model_info_label = ttk.Label(info_frame, textvariable=self.model_info_var, wraplength=900, justify="left")
        self.model_info_label.pack(fill="x")

    def _populate_models_dropdown(self):
        itype = InputType(self.input_type_var.get())
        models = Registry.models_for(itype)
        self.model_combo["values"] = [m.human_name for m in models]
        if models:
            self.model_var.set(models[0].human_name)
            self._on_model_change()
        else:
            self.model_var.set("")
            self.model_info_var.set("No models for this input type.")

    # ----------------- UI Logic -----------------
    def _on_input_type_change(self):
        self._update_input_widgets_visibility()
        self._populate_models_dropdown()
        self._clear_outputs()

    def _on_model_change(self):
        # Update model info
        model = Registry.find_by_human_name(self.model_var.get())
        if model:
            self.model_info_var.set(model.description)
        else:
            self.model_info_var.set("Select a model to see info.")

    def _update_input_widgets_visibility(self):
        itype = InputType(self.input_type_var.get())
        if itype == InputType.TEXT:
            self.text_entry.pack(fill="x")
            self.file_row.pack_forget()
        else:
            self.file_row.pack(fill="x", pady=6)
            self.text_entry.pack_forget()

    def _browse_file(self):
        itype = InputType(self.input_type_var.get())
        if itype == InputType.IMAGE:
            path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif"), ("All files", "*.*")])
        elif itype == InputType.AUDIO:
            path = filedialog.askopenfilename(filetypes=[("Audio files", "*.wav *.mp3 *.flac *.m4a *.ogg"), ("All files", "*.*")])
        else:
            path = filedialog.askopenfilename()
        if path:
            self.selected_file_path.set(path)
            # Show preview for images
            if itype == InputType.IMAGE:
                img = load_image_from_path(path).resize((320, 320))
                self._set_preview(img)
            else:
                self._set_preview(None)

    def _set_preview(self, pil_img):
        if pil_img is None:
            self.preview_label.configure(image="")
            self.preview_label.image = None
            return
        tkimg = ImageTk.PhotoImage(pil_img)
        self.preview_label.configure(image=tkimg)
        self.preview_label.image = tkimg

    def _clear_outputs(self):
        self.output_text.delete("1.0", "end")
        self._set_preview(None)

    def _run_clicked(self):
        model_meta = Registry.find_by_human_name(self.model_var.get())
        if not model_meta:
            messagebox.showerror("No model", "Please select a model.")
            return

        itype = InputType(self.input_type_var.get())
        if itype == InputType.TEXT:
            data = self.text_input.get().strip()
            if not data:
                messagebox.showwarning("Input needed", "Please type some text.")
                return
        else:
            path = self.selected_file_path.get()
            if not path:
                messagebox.showwarning("Input needed", "Please choose a file.")
                return
            data = path

        self.status_var.set("Running...")

        # Run model in a background thread to keep UI responsive
        def worker():
            try:
                output = self.model_manager.run(model_meta, itype, data)
                self._display_output(output)
                self.status_var.set("Done.")
            except Exception as e:
                self.status_var.set("Error.")
                messagebox.showerror("Model Error", str(e))

        threading.Thread(target=worker, daemon=True).start()

    def _display_output(self, output):
        # Show text output
        self.output_text.delete("1.0", "end")
        self.output_text.insert("1.0", output)

    # ----------------- Dialogs -----------------
    def _show_oop_dialog(self):
        txt = get_oop_explanations()
        messagebox.showinfo("OOP Explanations", txt)

    def _show_about(self):
        messagebox.showinfo(
            "About",
            "HIT137 Assignment 3 - Tkinter + Hugging Face\n"
            "Demonstrates multiple OOP concepts and multi-format inputs."
        )
