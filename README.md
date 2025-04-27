# FIT-to-CSV & Interactive Map Generator

A simple Python utility to:

- Parse a `.fit` file and extract **timestamp**, **latitude**, **longitude**, and **speed (m/s)**  
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
git clone <your-repo-url>
cd <repo-folder>
pip install fitparse pandas folium branca
