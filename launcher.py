#!/usr/bin/env python3
import os
import sys

# ─── WINDOWS TASKBAR ICON FIX ────────────────────────────────────────────────
if sys.platform == "win32":
    import ctypes
    # Use a unique AppUserModelID for your application:
    myappid = "ca.mcmasterbaja.stravaparser"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
# ─────────────────────────────────────────────────────────────────────────────

import webbrowser
import tkinter as tk
from tkinter import filedialog, messagebox
from main import process  # assumes main.py is in the same folder

class FitProcessorGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FIT → CSV & Map Generator")
        self.resizable(False, False)

        # Robust icon loading (window + taskbar/dock)
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(__file__)

        ico_path = os.path.join(base_path, "favicon.ico")
        png_path = os.path.join(base_path, "favicon.png")

        # 1) Try .ico for classic window icon
        if os.path.exists(ico_path):
            try:
                self.iconbitmap(ico_path)
            except Exception:
                pass

        # 2) Try .png for taskbar/dock & cross-platform icon
        if os.path.exists(png_path):
            try:
                img = tk.PhotoImage(file=png_path)
                self.iconphoto(True, img)
                self._icon_img = img  # keep reference alive
            except Exception:
                pass

        self.fit_path = ""
        self.out_dir  = ""
        self.max_speed = tk.DoubleVar(value=100.0)

        # Top description
        tk.Label(self,
                 text="Convert a .fit GPS file into:\n"
                      " • a timestamped CSV\n"
                      " • two interactive HTML maps (street & satellite)",
                 justify="left").grid(row=0, column=0, columnspan=2,
                                      padx=8, pady=(8,16), sticky="w")

        # FIT file chooser
        tk.Button(self, text="Select FIT File…", command=self.choose_fit)\
          .grid(row=1, column=0, padx=8, pady=4, sticky="ew")
        tk.Label(self, text="No file selected", anchor="w")\
          .grid(row=1, column=1, padx=8, sticky="w")

        # Output folder chooser
        tk.Button(self, text="Select Output Folder…", command=self.choose_folder)\
          .grid(row=2, column=0, padx=8, pady=4, sticky="ew")
        tk.Label(self, text="No folder selected", anchor="w")\
          .grid(row=2, column=1, padx=8, sticky="w")

        # Max speed entry + description
        tk.Label(self, text="Max Speed (km/h):").grid(row=3, column=0,
                                                      padx=8, pady=(12,4),
                                                      sticky="e")
        tk.Entry(self, textvariable=self.max_speed, width=10)\
          .grid(row=3, column=1, padx=8, pady=(12,4), sticky="w")
        tk.Label(self,
                 text="Exclude speeds > Max or < 0\nfrom the color-scale range\n"
                      " (points still plotted).",
                 justify="left", font=("TkDefaultFont", 8))\
          .grid(row=4, column=0, columnspan=2,
                padx=8, sticky="w")

        # Run button
        tk.Button(self, text="Run", command=self.run)\
          .grid(row=5, column=0, columnspan=2,
                padx=8, pady=(16,8), sticky="ew")

    def choose_fit(self):
        path = filedialog.askopenfilename(
            title="Select your FIT file",
            filetypes=[("FIT files", "*.fit"), ("All files", "*.*")]
        )
        if path:
            self.fit_path = path
            self.grid_slaves(row=1, column=1)[0].config(text=os.path.basename(path))

    def choose_folder(self):
        path = filedialog.askdirectory(title="Select output folder")
        if path:
            self.out_dir = path
            self.grid_slaves(row=2, column=1)[0].config(text=path)

    def run(self):
        # Validate inputs
        if not self.fit_path:
            messagebox.showwarning("Missing FIT file", "Please select a FIT file.")
            return
        if not self.out_dir:
            messagebox.showwarning("Missing Output Folder", "Please select an output folder.")
            return
        try:
            max_spd = float(self.max_speed.get())
            if max_spd <= 0:
                raise ValueError
        except Exception:
            messagebox.showwarning("Invalid Max Speed", "Enter a positive number for max speed.")
            return

        # Close the UI immediately
        self.destroy()

        # Prepare output subfolder
        base = os.path.splitext(os.path.basename(self.fit_path))[0]
        out_sub = os.path.join(self.out_dir, base)
        os.makedirs(out_sub, exist_ok=True)

        # Build output paths
        csv_path    = os.path.join(out_sub, f"{base}_data.csv")
        street_html = os.path.join(out_sub, f"{base}_street.html")
        sat_html    = os.path.join(out_sub, f"{base}_satellite.html")

        # Run processing
        try:
            process(self.fit_path, csv_path, street_html, sat_html, max_spd)
            webbrowser.open(f"file://{os.path.abspath(sat_html)}")
        except Exception as e:
            # Standalone alert after window closed
            tk.Tk().withdraw()
            messagebox.showerror("Processing Error", str(e))

if __name__ == "__main__":
    FitProcessorGUI().mainloop()
