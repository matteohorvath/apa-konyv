#!/usr/bin/env python3

import os
import tempfile
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path

import ocrmypdf
from PIL import Image

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".tiff", ".tif", ".bmp", ".gif", ".webp"}

LANGUAGES = [
    ("Magyar (Hungarian)", "hun", "HU"),
    ("English", "eng", "EN"),
    ("Deutsch (German)", "deu", "DE"),
    ("Français (French)", "fra", "FR"),
    ("Italiano (Italian)", "ita", "IT"),
    ("Español (Spanish)", "spa", "ES"),
    ("Română (Romanian)", "ron", "RO"),
    ("Polski (Polish)", "pol", "PL"),
    ("Česky (Czech)", "ces", "CZ"),
    ("Slovenčina (Slovak)", "slk", "SK"),
    ("Hrvatski (Croatian)", "hrv", "HR"),
    ("Srpski (Serbian)", "srp", "SR"),
]

BG = "#1e1e2e"
CARD = "#2a2a3d"
CARD_BORDER = "#363650"
FG = "#e0e0ef"
FG_DIM = "#8888a8"
ACCENT = "#7c6ff7"
ACCENT_HOVER = "#9589ff"
ACCENT_FG = "#ffffff"
ENTRY_BG = "#33334a"
ENTRY_FG = "#e0e0ef"
ENTRY_BORDER = "#4a4a6a"
PREVIEW_FG = "#a89cff"
SUCCESS = "#6bcf7f"
ERROR = "#f27a7a"
FONT = "Helvetica"


class OcrApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("OCR")
        self.resizable(False, False)
        self.configure(bg=BG)
        self._build_ui()
        self.update_idletasks()
        self._center()

    def _center(self):
        self.update_idletasks()
        w = self.winfo_reqwidth()
        h = self.winfo_reqheight()
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"+{x}+{y}")

    # ── UI construction ──────────────────────────────────────────────

    def _build_ui(self):
        outer = tk.Frame(self, bg=BG)
        outer.pack(padx=28, pady=24)

        # Header
        tk.Label(
            outer, text="OCR", font=(FONT, 22, "bold"),
            bg=BG, fg=FG,
        ).pack(anchor="w")
        tk.Label(
            outer, text="Szkennelt PDF / kép fájlok szövegfelismerése",
            font=(FONT, 11), bg=BG, fg=FG_DIM,
        ).pack(anchor="w", pady=(0, 16))

        # Card
        card = tk.Frame(outer, bg=CARD, highlightbackground=CARD_BORDER, highlightthickness=1)
        card.pack(fill="x")
        inner = tk.Frame(card, bg=CARD)
        inner.pack(padx=20, pady=18, fill="x")

        self._make_file_row(inner, "Bemeneti fájl", self._browse_input, is_input=True)
        self._make_separator(inner)
        self._make_folder_row(inner, "Kimeneti mappa", self._browse_output_dir)
        self._make_separator(inner)
        self._make_lang_row(inner)
        self._make_separator(inner)
        self._make_preview_row(inner)

        # Run button
        self.btn_run = tk.Button(
            outer, text="Indítás", font=(FONT, 13, "bold"),
            bg=ACCENT, fg=ACCENT_FG, activebackground=ACCENT_HOVER,
            activeforeground=ACCENT_FG, relief="flat", cursor="hand2",
            bd=0, padx=32, pady=10, command=self._run,
        )
        self.btn_run.pack(fill="x", pady=(16, 0), ipady=2)
        self.btn_run.bind("<Enter>", lambda e: self.btn_run.configure(bg=ACCENT_HOVER))
        self.btn_run.bind("<Leave>", lambda e: self.btn_run.configure(bg=ACCENT))

        # Progress bar
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(
            "Custom.Horizontal.TProgressbar",
            troughcolor=CARD, background=ACCENT,
            bordercolor=BG, lightcolor=ACCENT, darkcolor=ACCENT,
        )
        self.progress = ttk.Progressbar(
            outer, mode="indeterminate", length=100,
            style="Custom.Horizontal.TProgressbar",
        )
        self.progress.pack(fill="x", pady=(10, 0))

        # Status
        self.var_status = tk.StringVar(value="Válasszon egy PDF vagy kép fájlt a kezdéshez.")
        self.lbl_status = tk.Label(
            outer, textvariable=self.var_status,
            font=(FONT, 10), bg=BG, fg=FG_DIM, anchor="w",
        )
        self.lbl_status.pack(fill="x", pady=(6, 0))

    def _make_separator(self, parent):
        tk.Frame(parent, bg=CARD_BORDER, height=1).pack(fill="x", pady=10)

    def _make_label(self, parent, text):
        tk.Label(
            parent, text=text, font=(FONT, 10, "bold"),
            bg=CARD, fg=FG_DIM,
        ).pack(anchor="w")

    def _make_entry(self, parent, var):
        e = tk.Entry(
            parent, textvariable=var, font=(FONT, 11),
            bg=ENTRY_BG, fg=ENTRY_FG, insertbackground=ENTRY_FG,
            relief="flat", bd=0, highlightthickness=1,
            highlightbackground=ENTRY_BORDER, highlightcolor=ACCENT,
        )
        return e

    def _make_browse_btn(self, parent, command):
        btn = tk.Button(
            parent, text="Tallózás…", font=(FONT, 10),
            bg=ENTRY_BG, fg=FG, activebackground=ENTRY_BORDER,
            activeforeground=FG, relief="flat", bd=0,
            cursor="hand2", padx=12, pady=4, command=command,
        )
        btn.bind("<Enter>", lambda e, b=btn: b.configure(bg=ENTRY_BORDER))
        btn.bind("<Leave>", lambda e, b=btn: b.configure(bg=ENTRY_BG))
        return btn

    def _make_file_row(self, parent, label, command, is_input=False):
        self._make_label(parent, label)
        row = tk.Frame(parent, bg=CARD)
        row.pack(fill="x", pady=(4, 0))
        if is_input:
            self.var_input = tk.StringVar()
            entry = self._make_entry(row, self.var_input)
        else:
            entry = self._make_entry(row, tk.StringVar())
        entry.pack(side="left", fill="x", expand=True, ipady=5)
        self._make_browse_btn(row, command).pack(side="left", padx=(8, 0), ipady=2)

    def _make_folder_row(self, parent, label, command):
        self._make_label(parent, label)
        row = tk.Frame(parent, bg=CARD)
        row.pack(fill="x", pady=(4, 0))
        self.var_output_dir = tk.StringVar()
        self._make_entry(row, self.var_output_dir).pack(side="left", fill="x", expand=True, ipady=5)
        self._make_browse_btn(row, command).pack(side="left", padx=(8, 0), ipady=2)

    def _make_lang_row(self, parent):
        self._make_label(parent, "Nyelv")
        self.var_lang = tk.StringVar(value=LANGUAGES[0][0])

        style = ttk.Style()
        style.configure(
            "Custom.TCombobox",
            fieldbackground=ENTRY_BG, background=ENTRY_BG,
            foreground=ENTRY_FG, arrowcolor=FG_DIM,
            borderwidth=0, relief="flat",
        )
        style.map(
            "Custom.TCombobox",
            fieldbackground=[("readonly", ENTRY_BG)],
            foreground=[("readonly", ENTRY_FG)],
            selectbackground=[("readonly", ENTRY_BG)],
            selectforeground=[("readonly", ENTRY_FG)],
        )

        combo = ttk.Combobox(
            parent, textvariable=self.var_lang,
            values=[l[0] for l in LANGUAGES],
            state="readonly", style="Custom.TCombobox",
            font=(FONT, 11),
        )
        combo.pack(fill="x", pady=(4, 0), ipady=4)
        combo.bind("<<ComboboxSelected>>", lambda _: self._update_output_preview())

        self.option_add("*TCombobox*Listbox.background", ENTRY_BG)
        self.option_add("*TCombobox*Listbox.foreground", ENTRY_FG)
        self.option_add("*TCombobox*Listbox.selectBackground", ACCENT)
        self.option_add("*TCombobox*Listbox.selectForeground", ACCENT_FG)
        self.option_add("*TCombobox*Listbox.font", (FONT, 11))

    def _make_preview_row(self, parent):
        self._make_label(parent, "Kimeneti fájl")
        self.var_output_preview = tk.StringVar(value="—")
        tk.Label(
            parent, textvariable=self.var_output_preview,
            font=(FONT, 11), bg=CARD, fg=PREVIEW_FG, anchor="w",
            wraplength=420, justify="left",
        ).pack(anchor="w", pady=(4, 0))

    # ── Actions ──────────────────────────────────────────────────────

    def _browse_input(self):
        path = filedialog.askopenfilename(
            title="Válassza ki a bemeneti fájlt",
            filetypes=[
                ("Támogatott fájlok", "*.pdf *.jpg *.jpeg *.png *.tiff *.tif *.bmp *.gif *.webp"),
                ("PDF fájlok", "*.pdf"),
                ("Képfájlok", "*.jpg *.jpeg *.png *.tiff *.tif *.bmp *.gif *.webp"),
                ("Minden fájl", "*.*"),
            ],
        )
        if path:
            self.var_input.set(path)
            if not self.var_output_dir.get():
                self.var_output_dir.set(os.path.dirname(path))
            self._update_output_preview()

    def _browse_output_dir(self):
        path = filedialog.askdirectory(title="Válassza ki a kimeneti mappát")
        if path:
            self.var_output_dir.set(path)
            self._update_output_preview()

    def _selected_lang(self):
        display = self.var_lang.get()
        for name, code, suffix in LANGUAGES:
            if name == display:
                return code, suffix
        return "hun", "HU"

    def _build_output_path(self):
        input_pdf = self.var_input.get().strip()
        output_dir = self.var_output_dir.get().strip()
        if not input_pdf or not output_dir:
            return ""
        _, suffix = self._selected_lang()
        stem = Path(input_pdf).stem
        return os.path.join(output_dir, f"{stem}_{suffix}.pdf")

    def _update_output_preview(self):
        output_path = self._build_output_path()
        self.var_output_preview.set(output_path if output_path else "—")

    def _set_status(self, text, color=None):
        self.var_status.set(text)
        self.lbl_status.configure(fg=color or FG_DIM)

    @staticmethod
    def _is_image(path):
        return Path(path).suffix.lower() in IMAGE_EXTENSIONS

    def _run(self):
        input_file = self.var_input.get().strip()
        output_dir = self.var_output_dir.get().strip()

        if not input_file:
            messagebox.showwarning("Hiányzó bemenet", "Kérem válasszon bemeneti fájlt.")
            return
        if not os.path.isfile(input_file):
            messagebox.showerror("Fájl nem található", f"A fájl nem található:\n{input_file}")
            return
        if not output_dir:
            messagebox.showwarning("Hiányzó kimenet", "Kérem válasszon kimeneti mappát.")
            return
        if not os.path.isdir(output_dir):
            messagebox.showerror("Mappa nem található", f"A mappa nem található:\n{output_dir}")
            return

        output_pdf = self._build_output_path()
        lang, _ = self._selected_lang()
        self.btn_run.configure(state="disabled", bg=ENTRY_BORDER)
        self.progress.start(12)
        self._set_status("OCR feldolgozás folyamatban… Kérem várjon.", ACCENT)

        thread = threading.Thread(target=self._ocr_worker, args=(input_file, output_pdf, lang), daemon=True)
        thread.start()

    @staticmethod
    def _image_to_temp_pdf(image_path):
        img = Image.open(image_path)
        if img.mode in ("RGBA", "LA", "P"):
            img = img.convert("RGB")
        tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        img.save(tmp.name, "PDF", resolution=300)
        img.close()
        return tmp.name

    def _ocr_worker(self, input_file, output_pdf, lang):
        tmp_pdf = None
        try:
            if self._is_image(input_file):
                tmp_pdf = self._image_to_temp_pdf(input_file)
                ocr_input = tmp_pdf
            else:
                ocr_input = input_file

            ocrmypdf.ocr(
                ocr_input,
                output_pdf,
                language=lang,
                jobs=4,
                deskew=True,
                optimize=1,
                output_type="pdf",
            )
            self.after(0, self._on_success, output_pdf)
        except Exception as exc:
            self.after(0, self._on_error, str(exc))
        finally:
            if tmp_pdf and os.path.exists(tmp_pdf):
                os.unlink(tmp_pdf)

    def _on_success(self, output_pdf):
        self.progress.stop()
        self.btn_run.configure(state="normal", bg=ACCENT)
        self._set_status("Kész!", SUCCESS)
        messagebox.showinfo("Sikeres", f"Az OCR feldolgozás kész!\n\nKimeneti fájl:\n{output_pdf}")
        self._set_status("Válasszon egy PDF vagy kép fájlt a kezdéshez.")

    def _on_error(self, error_msg):
        self.progress.stop()
        self.btn_run.configure(state="normal", bg=ACCENT)
        self._set_status("Hiba történt.", ERROR)
        messagebox.showerror("Hiba", f"Hiba az OCR feldolgozás során:\n\n{error_msg}")


def main():
    app = OcrApp()
    app.mainloop()


if __name__ == "__main__":
    main()
