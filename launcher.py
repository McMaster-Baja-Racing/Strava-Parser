#!/usr/bin/env python3
import os
import webbrowser
import tkinter as tk
from tkinter import filedialog, messagebox
from main import process  # assumes main.py in the same folder


def main():
    # Hide main Tk window
    root = tk.Tk()
    root.withdraw()

    # 1) Select FIT file
    fit_file = filedialog.askopenfilename(
        title="Select your FIT file",
        filetypes=[("FIT files", "*.fit"), ("All files", "*.*")]
    )
    if not fit_file:
        return

    # 2) Choose a parent directory for output
    parent_dir = filedialog.askdirectory(
        title="Select a folder to save results in"
    )
    if not parent_dir:
        return

    # 3) Create an output folder named after the FIT base name
    base_name = os.path.splitext(os.path.basename(fit_file))[0]
    out_dir = os.path.join(parent_dir, base_name)
    try:
        os.makedirs(out_dir, exist_ok=True)
    except Exception as e:
        messagebox.showerror("Error creating folder", str(e))
        return

    # 4) Build output file paths inside that folder
    csv_path    = os.path.join(out_dir, f"{base_name}_data.csv")
    street_html = os.path.join(out_dir, f"{base_name}_street.html")
    sat_html    = os.path.join(out_dir, f"{base_name}_satellite.html")

    # 5) Process the FIT and open the satellite map
    try:
        process(fit_file, csv_path, street_html, sat_html)
        webbrowser.open(f"file://{os.path.abspath(sat_html)}")
    except Exception as e:
        messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    main()