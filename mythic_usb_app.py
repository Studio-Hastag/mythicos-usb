#!/usr/bin/env python3
"""Interface graphique MythicOS USB Creator."""

from __future__ import annotations

import subprocess
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

APP_TITLE = "MythicOS USB Creator"
CLI_PATH = Path(__file__).resolve().with_name("mythic_usb_creator.py")


class MythicUsbApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("760x520")
        self.minsize(700, 450)

        self.iso_var = tk.StringVar()
        self.device_var = tk.StringVar()
        self.simulate_var = tk.BooleanVar(value=True)
        self.auto_yes_var = tk.BooleanVar(value=False)

        self._build_ui()

    def _build_ui(self) -> None:
        frame = ttk.Frame(self, padding=16)
        frame.pack(fill=tk.BOTH, expand=True)

        title = ttk.Label(frame, text=APP_TITLE, font=("TkDefaultFont", 16, "bold"))
        title.pack(anchor="w", pady=(0, 12))

        iso_frame = ttk.LabelFrame(frame, text="Image ISO")
        iso_frame.pack(fill=tk.X, pady=6)
        ttk.Entry(iso_frame, textvariable=self.iso_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8, pady=8)
        ttk.Button(iso_frame, text="Parcourir", command=self._browse_iso).pack(side=tk.RIGHT, padx=8, pady=8)

        dev_frame = ttk.LabelFrame(frame, text="Périphérique USB")
        dev_frame.pack(fill=tk.X, pady=6)
        self.device_combo = ttk.Combobox(dev_frame, textvariable=self.device_var, state="readonly")
        self.device_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8, pady=8)
        ttk.Button(dev_frame, text="Actualiser", command=self.refresh_devices).pack(side=tk.RIGHT, padx=8, pady=8)

        options = ttk.Frame(frame)
        options.pack(fill=tk.X, pady=6)
        ttk.Checkbutton(options, text="Simulation (pas d'écriture disque)", variable=self.simulate_var).pack(anchor="w")
        ttk.Checkbutton(options, text="Confirmer automatiquement (--yes)", variable=self.auto_yes_var).pack(anchor="w")

        actions = ttk.Frame(frame)
        actions.pack(fill=tk.X, pady=(8, 4))
        ttk.Button(actions, text="Vérifier ISO", command=self.verify_iso).pack(side=tk.LEFT)
        ttk.Button(actions, text="Écrire vers USB", command=self.write_iso).pack(side=tk.LEFT, padx=(8, 0))

        log_frame = ttk.LabelFrame(frame, text="Journal")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=8)
        self.log_text = tk.Text(log_frame, wrap="word", height=14)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.refresh_devices()

    def _browse_iso(self) -> None:
        filename = filedialog.askopenfilename(
            title="Sélectionner une ISO MythicOS",
            filetypes=[("ISO files", "*.iso"), ("All files", "*.*")],
        )
        if filename:
            self.iso_var.set(filename)

    def _append_log(self, text: str) -> None:
        self.log_text.insert(tk.END, text + "\n")
        self.log_text.see(tk.END)

    def _run_cli(self, args: list[str], success_message: str | None = None) -> None:
        def task() -> None:
            cmd = ["python3", str(CLI_PATH), *args]
            self.after(0, lambda: self._append_log(f"$ {' '.join(cmd)}"))
            proc = subprocess.run(cmd, capture_output=True, text=True)
            out = proc.stdout.strip()
            err = proc.stderr.strip()
            if out:
                self.after(0, lambda: self._append_log(out))
            if err:
                self.after(0, lambda: self._append_log(err))

            if proc.returncode == 0 and success_message:
                self.after(0, lambda: messagebox.showinfo(APP_TITLE, success_message))
            elif proc.returncode != 0:
                self.after(0, lambda: messagebox.showerror(APP_TITLE, "Opération échouée. Voir le journal."))

        threading.Thread(target=task, daemon=True).start()

    def refresh_devices(self) -> None:
        cmd = ["python3", str(CLI_PATH), "devices"]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        entries: list[str] = []
        for line in proc.stdout.splitlines():
            if line.startswith("- /dev/"):
                entries.append(line.split(" ")[1])
        self.device_combo["values"] = entries
        if entries:
            self.device_var.set(entries[0])

    def verify_iso(self) -> None:
        iso = self.iso_var.get().strip()
        if not iso:
            messagebox.showwarning(APP_TITLE, "Sélectionne une ISO d'abord.")
            return
        self._run_cli(["verify", iso], success_message="ISO valide.")

    def write_iso(self) -> None:
        iso = self.iso_var.get().strip()
        device = self.device_var.get().strip()

        if not iso or not device:
            messagebox.showwarning(APP_TITLE, "Sélectionne une ISO et un périphérique USB.")
            return

        if not messagebox.askyesno(
            APP_TITLE,
            f"Toutes les données de {device} seront effacées. Continuer ?",
        ):
            return

        args = ["write", iso, device]
        if self.simulate_var.get():
            args.append("--simulate")
        if self.auto_yes_var.get() or self.simulate_var.get():
            args.append("--yes")

        self._run_cli(args, success_message="Écriture terminée.")


def main() -> int:
    app = MythicUsbApp()
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
