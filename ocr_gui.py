#!/usr/bin/env python3

import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path

import ocrmypdf

LANGUAGES = [
    ("Magyar (Hungarian)", "hun"),
    ("English", "eng"),
    ("Deutsch (German)", "deu"),
    ("Français (French)", "fra"),
    ("Italiano (Italian)", "ita"),
    ("Español (Spanish)", "spa"),
    ("Română (Romanian)", "ron"),
    ("Polski (Polish)", "pol"),
    ("Česky (Czech)", "ces"),
    ("Slovenčina (Slovak)", "slk"),
    ("Hrvatski (Croatian)", "hrv"),
    ("Srpski (Serbian)", "srp"),
]


class OcrApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PDF OCR – Szövegfelismerés")
        self.resizable(False, False)
        self._center(520, 420)
        self.configure(bg="#f5f5f5")

        self._build_ui()

    def _center(self, w, h):
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _build_ui(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TLabel", background="#f5f5f5", font=("Helvetica", 11))
        style.configure("Header.TLabel", background="#f5f5f5", font=("Helvetica", 16, "bold"))
        style.configure("TButton", font=("Helvetica", 11), padding=6)
        style.configure("Run.TButton", font=("Helvetica", 13, "bold"), padding=10)
        style.configure("TCombobox", font=("Helvetica", 11))
        style.configure("TEntry", font=("Helvetica", 11))

        pad = {"padx": 18, "pady": 4}

        ttk.Label(self, text="PDF OCR – Szövegfelismerés", style="Header.TLabel").pack(pady=(18, 2))
        ttk.Label(self, text="Szkennelt PDF fájlok szövegfelismerése (OCR)").pack(pady=(0, 12))

        # --- Input file ---
        frm_in = ttk.Frame(self)
        frm_in.pack(fill="x", **pad)
        ttk.Label(frm_in, text="Bemeneti PDF:").pack(anchor="w")
        row_in = ttk.Frame(frm_in)
        row_in.pack(fill="x", pady=2)
        self.var_input = tk.StringVar()
        ttk.Entry(row_in, textvariable=self.var_input).pack(side="left", fill="x", expand=True)
        ttk.Button(row_in, text="Tallózás…", command=self._browse_input).pack(side="left", padx=(6, 0))

        # --- Output file ---
        frm_out = ttk.Frame(self)
        frm_out.pack(fill="x", **pad)
        ttk.Label(frm_out, text="Kimeneti PDF:").pack(anchor="w")
        row_out = ttk.Frame(frm_out)
        row_out.pack(fill="x", pady=2)
        self.var_output = tk.StringVar()
        ttk.Entry(row_out, textvariable=self.var_output).pack(side="left", fill="x", expand=True)
        ttk.Button(row_out, text="Tallózás…", command=self._browse_output).pack(side="left", padx=(6, 0))

        # --- Language ---
        frm_lang = ttk.Frame(self)
        frm_lang.pack(fill="x", **pad)
        ttk.Label(frm_lang, text="Nyelv:").pack(anchor="w")
        self.var_lang = tk.StringVar(value=LANGUAGES[0][0])
        combo = ttk.Combobox(
            frm_lang,
            textvariable=self.var_lang,
            values=[l[0] for l in LANGUAGES],
            state="readonly",
            width=30,
        )
        combo.pack(anchor="w", pady=2)

        # --- Run button ---
        self.btn_run = ttk.Button(self, text="Indítás", style="Run.TButton", command=self._run)
        self.btn_run.pack(pady=(16, 4))

        # --- Progress ---
        self.progress = ttk.Progressbar(self, mode="indeterminate", length=460)
        self.progress.pack(pady=(2, 4))

        # --- Status ---
        self.var_status = tk.StringVar(value="Válasszon egy PDF fájlt a kezdéshez.")
        ttk.Label(self, textvariable=self.var_status, foreground="#555").pack(pady=(0, 12))

    def _browse_input(self):
        path = filedialog.askopenfilename(
            title="Válassza ki a bemeneti PDF-et",
            filetypes=[("PDF fájlok", "*.pdf"), ("Minden fájl", "*.*")],
        )
        if path:
            self.var_input.set(path)
            if not self.var_output.get():
                base, ext = os.path.splitext(path)
                self.var_output.set(f"{base}_ocr{ext}")

    def _browse_output(self):
        path = filedialog.asksaveasfilename(
            title="Mentés másként",
            defaultextension=".pdf",
            filetypes=[("PDF fájlok", "*.pdf")],
        )
        if path:
            self.var_output.set(path)

    def _selected_lang_code(self):
        display = self.var_lang.get()
        for name, code in LANGUAGES:
            if name == display:
                return code
        return "hun"

    def _run(self):
        input_pdf = self.var_input.get().strip()
        output_pdf = self.var_output.get().strip()

        if not input_pdf:
            messagebox.showwarning("Hiányzó bemenet", "Kérem válasszon bemeneti PDF fájlt.")
            return
        if not os.path.isfile(input_pdf):
            messagebox.showerror("Fájl nem található", f"A fájl nem található:\n{input_pdf}")
            return
        if not output_pdf:
            messagebox.showwarning("Hiányzó kimenet", "Kérem adja meg a kimeneti fájl nevét.")
            return

        lang = self._selected_lang_code()
        self.btn_run.configure(state="disabled")
        self.progress.start(12)
        self.var_status.set("OCR feldolgozás folyamatban… Kérem várjon.")

        thread = threading.Thread(target=self._ocr_worker, args=(input_pdf, output_pdf, lang), daemon=True)
        thread.start()

    def _ocr_worker(self, input_pdf, output_pdf, lang):
        try:
            ocrmypdf.ocr(
                input_pdf,
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

    def _on_success(self, output_pdf):
        self.progress.stop()
        self.btn_run.configure(state="normal")
        self.var_status.set("Kész!")
        messagebox.showinfo("Sikeres", f"Az OCR feldolgozás kész!\n\nKimeneti fájl:\n{output_pdf}")
        self.var_status.set("Válasszon egy PDF fájlt a kezdéshez.")

    def _on_error(self, error_msg):
        self.progress.stop()
        self.btn_run.configure(state="normal")
        self.var_status.set("Hiba történt.")
        messagebox.showerror("Hiba", f"Hiba az OCR feldolgozás során:\n\n{error_msg}")


def main():
    app = OcrApp()
    app.mainloop()


if __name__ == "__main__":
    main()
