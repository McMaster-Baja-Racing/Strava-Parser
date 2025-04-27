# FIT-to-CSV & Interactive Map Generator

A simple Python utility to:

- Parse a `.fit` file and extract **timestamp**, **latitude**, **longitude**, and **speed (km/h)**  
- Export the data to a CSV  
- Generate two interactive HTML maps:
  - **Street View** (OpenStreetMap)  
  - **Satellite View** (Esri World Imagery)  
  with your route colored blue→red by speed.

---

## ⚙️ Prerequisites

- Python 3.7+  
- Pip  

## 📥 Installation

```bash
git clone https://github.com/McMaster-Baja-Racing/Strava-Parser
cd Strava-Parser
pip install fitparse pandas folium branca
```

## 🚩 Exporting a FIT from Strava

1. Log in to Strava on the web and open the activity you want.  
2. Click the **⋯** menu (upper right) and select **Export Original**.  
3. The `.fit` file will download—use this as your `input.fit`.

*Note: this does not work on mobile.*

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
- **street_map.html** Your track over OpenStreetMap  
- **satellite_map.html** Your track over Esri satellite imagery  

Open either HTML file in a browser to explore your ride, colored by speed. 

---

## 📝 License

MIT © 2025  
