#!/usr/bin/env python3
import sys
from fitparse import FitFile
import pandas as pd
import folium
from branca.colormap import LinearColormap

# --- Parse FIT and convert semicircles → decimal degrees, compute speed in km/h ---
def parse_fit(fit_path):
    fit = FitFile(fit_path)
    rows = []
    for rec in fit.get_messages('record'):
        data = {f.name: f.value for f in rec.fields}
        ts        = data.get('timestamp')
        raw_lat   = data.get('position_lat')
        raw_lon   = data.get('position_long')
        speed_ms  = data.get('speed')
        if None not in (ts, raw_lat, raw_lon, speed_ms):
            # semicircles → degrees
            lat = raw_lat * (180.0 / 2**31)
            lon = raw_lon * (180.0 / 2**31)
            # convert speed from m/s to km/h
            speed_kmh = speed_ms * 3.6
            rows.append({
                'timestamp': ts,
                'lat':       lat,
                'lon':       lon,
                'speed_kmh': speed_kmh
            })
    return pd.DataFrame(rows)

# --- Write CSV ---
def write_csv(df, csv_path):
    out = df.copy()
    out['timestamp'] = out['timestamp'].dt.strftime('%Y-%m-%dT%H:%M:%S')
    out.to_csv(csv_path, index=False,
               columns=['timestamp','lat','lon','speed_kmh'])
    print(f"✔ CSV written to {csv_path}")

# --- Build a map with clickable segments showing speed ---
def build_map(df, html_path, tiles, name):
    center = (df.lat.mean(), df.lon.mean())
    m = folium.Map(location=center, zoom_start=13, tiles=None)
    folium.TileLayer(tiles=tiles, name=name, attr=name).add_to(m)

    # color scale
    vmin, vmax = df.speed_kmh.min(), df.speed_kmh.max()
    cmap = LinearColormap(
        ['blue', 'red'],
        vmin=vmin,
        vmax=vmax,
        caption='Speed (km/h)'
    )
    cmap.add_to(m)

    # clickable segments
    for i in range(len(df) - 1):
        start = df.iloc[i]
        end = df.iloc[i + 1]
        speed = start.speed_kmh
        folium.PolyLine(
            locations=[(start.lat, start.lon), (end.lat, end.lon)],
            color=cmap(speed),
            weight=4,
            opacity=0.8,
            tooltip=f"{speed:.1f} km/h",
            popup=f"{speed:.1f} km/h"
        ).add_to(m)

    folium.LayerControl().add_to(m)
    m.save(html_path)
    print(f"✔ {name} map written to {html_path}")

# --- Primary processing function ---
def process(fit_in, csv_out, street_html, sat_html):
    df = parse_fit(fit_in)
    if df.empty:
        print("⚠️ No valid GPS records found.")
        sys.exit(1)
    write_csv(df, csv_out)
    build_map(
        df,
        street_html,
        tiles='OpenStreetMap',
        name='OpenStreetMap'
    )
    build_map(
        df,
        sat_html,
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        name='Esri World Imagery'
    )

# --- CLI entrypoint ---
def main():
    if len(sys.argv) != 5:
        print(f"Usage: {sys.argv[0]} input.fit output.csv street_map.html satellite_map.html")
        sys.exit(1)
    process(*sys.argv[1:])

if __name__ == '__main__':
    main()
