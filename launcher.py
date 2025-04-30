#!/usr/bin/env python3
import os
import sys
import webbrowser
import tkinter as tk
from tkinter import filedialog, messagebox
from main import process, process_multiple

class FitProcessorGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FIT → CSV & Map Generator")
        self.resizable(False, False)
        if sys.platform == "win32":
            import ctypes
            myappid = "ca.mcmasterbaja.stravaparser"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        self.fit_paths = []
        self.out_dir = ""
        self.max_speed = tk.DoubleVar(value=100.0)

        tk.Label(self,
                 text="Convert one or more .fit GPS files into:\n"
                      " • timestamped CSVs\n"
                      " • two interactive HTML maps (street & satellite)",
                 justify="left").grid(row=0, column=0, columnspan=2,
                                      padx=8, pady=(8,16), sticky="w")

        tk.Button(self, text="Select FIT File(s)…", command=self.choose_fit)\
          .grid(row=1, column=0, padx=8, pady=4, sticky="ew")
        tk.Label(self, text="No files selected", anchor="w")\
          .grid(row=1, column=1, padx=8, sticky="w")

        tk.Button(self, text="Select Output Folder…", command=self.choose_folder)\
          .grid(row=2, column=0, padx=8, pady=4, sticky="ew")
        tk.Label(self, text="No folder selected", anchor="w")\
          .grid(row=2, column=1, padx=8, sticky="w")

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

        tk.Button(self, text="Run", command=self.run)\
          .grid(row=5, column=0, columnspan=2,
                padx=8, pady=(16,8), sticky="ew")

    def choose_fit(self):
        paths = filedialog.askopenfilenames(
            title="Select your FIT file(s)",
            filetypes=[("FIT files", "*.fit"), ("All files", "*.*")]
        )
        if paths:
            self.fit_paths = list(paths)
            self.grid_slaves(row=1, column=1)[0].config(
                text=f"{len(paths)} file(s) selected"
            )

    def choose_folder(self):
        path = filedialog.askdirectory(title="Select output folder")
        if path:
            self.out_dir = path
            self.grid_slaves(row=2, column=1)[0].config(text=path)

    def run(self):
        if not self.fit_paths:
            messagebox.showwarning("Missing FIT file(s)", "Please select at least one FIT file.")
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

        self.destroy()
        base_names = [os.path.splitext(os.path.basename(p))[0] for p in self.fit_paths]
        os.makedirs(self.out_dir, exist_ok=True)

        try:
            if len(self.fit_paths) > 1:
                out_sub = os.path.join(self.out_dir, base_names[0] + "-and-more")
                os.makedirs(out_sub, exist_ok=True)
                html_path    = os.path.join(out_sub, f"{base_names[0]}_and_more_map_view.html")
                process_multiple(self.fit_paths, out_sub, html_path, max_spd)
                webbrowser.open(f"file://{os.path.abspath(html_path)}")
            else:
                single = self.fit_paths[0]
                out_sub = os.path.join(self.out_dir, base_names[0])
                os.makedirs(out_sub, exist_ok=True)
                csv_path    = os.path.join(out_sub, f"{base_names[0]}_data.csv")
                html_path    = os.path.join(out_sub, f"{base_names[0]}_map_view.html")
                process(single, csv_path, html_path, max_spd)
                webbrowser.open(f"file://{os.path.abspath(html_path)}")
        except Exception as e:
            tk.Tk().withdraw()
            messagebox.showerror("Processing Error", str(e))

if __name__ == "__main__":
    FitProcessorGUI().mainloop()
