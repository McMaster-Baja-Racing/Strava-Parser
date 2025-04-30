# FIT-to-CSV & Interactive Map Generator

A simple Python utility to:

- Parse a `.fit` file and extract **timestamp**, **latitude**, **longitude**, and **speed (km/h)**  
- Export the data to a CSV  
- Generate an interactive HTML map with two layers:
  - **Street View** (OpenStreetMap)  
  - **Satellite View** (Esri World Imagery)  
  with your route colored blue→red by speed.
- Multiple routes are differentiated by highlighting accompanied by a legend and the ability to toggle them.

![image](https://github.com/user-attachments/assets/58dad959-d37a-41e4-9733-a553005244b7)



---

## 🚀 Usage
1. Download `MBR-Strava-Parser.exe` from the latest releases.
2. Double click `MBR-Strava-Parser.exe` to run the application.
3. It will prompt you to select a `*.fit` file, see below to extract from Strava.
4. It will then request you select a directory to save the files in. Inside this directory it will create a folder to store the data.
5. Finally, it will open a satellite map with your data!

## 🚩 Exporting a FIT from Strava

*Note: this does not work on mobile.*

1. Log in to Strava on the web and open the activity you want.  
2. Click the **⋯** menu (middle left) and select **Export Original**.  
3. The `.fit` file will download — use this as your `input.fit`.

Or follow the instructions here: https://support.strava.com/hc/en-us/articles/216918437-Exporting-your-Data-and-Bulk-Export

--
# Developper Guide

## ⚙️ Prerequisites

- Python 3.7+  
- Pip  

## 📥 Installation

```bash
git clone <your-repo-url>
cd <repo-folder>
pip install fitparse pandas folium branca
```

## 🚀 Usage

```bash
python main.py input.fit output.csv street_map.html satellite_map.html
```

**Example:**

```bash
python main.py my_ride.fit ride_data.csv ride_street.html ride_satellite.html
```

- **input.fit** Downloaded FIT from Strava  
- **output.csv** CSV with columns:  
  ```
  timestamp,lat,lon,speed_kmh
  2025-04-13T19:08:42,43.712345,-79.416789,70.2
  ```  
- **map_view.html** Your track over OpenStreetMap  

Open either HTML file in a browser to explore your ride, colored by speed.

## 📦 Packaging as a Standalone Application

To let teammates run this tool by double‑clicking an executable, you can bundle `main.py` and `launcher.py` into a single `.exe` using PyInstaller:

1. **Install PyInstaller** in your Python environment:
   ```bash
   pip install pyinstaller
   ```

2. **Bundle** the launcher script into one executable:
   ```bash
   # From the project root, where main.py and launcher.py live
   python -m PyInstaller --onefile --windowed launcher.py
   ```

   - `--onefile` packs all dependencies into a single `.exe`  
   - `--windowed` suppresses the console window (GUI only)  
   - The generated executable will be in `dist/launcher.exe`.

3. **Include map‑tile definitions** (providers.json) so Folium can resolve custom layers. If you encounter `xyzservices` errors, re-run with:
   ```bash
   python -m PyInstaller \
     --onefile --windowed launcher.py \
     --add-data "<path_to_python_site_packages>/xyzservices/data;xyzservices/data"
   ```

4. **Distribute** the `launcher.exe` file. Teammates can double‑click it, select a FIT file, choose an output folder, and instantly see the satellite map.

---

## 🔄 Workflow

1. **Parse** — read FIT “record” messages  
2. **Convert** — semicircles → decimal degrees; m/s → km/h  
3. **Export** — write `timestamp,lat,lon,speed_kmh` to CSV  
4. **Visualize** — draw line segments on two maps with a speed‑based legend  

---

## 📝 License

MIT © 2025

