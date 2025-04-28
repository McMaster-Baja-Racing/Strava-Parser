#!/usr/bin/env python3
import sys
from fitparse import FitFile
import pandas as pd
import folium
from branca.colormap import LinearColormap

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
            lat = raw_lat * (180.0 / 2**31)
            lon = raw_lon * (180.0 / 2**31)
            speed_kmh = speed_ms * 3.6
            rows.append({
                'timestamp': ts,
                'lat':       lat,
                'lon':       lon,
                'speed_kmh': speed_kmh
            })
    return pd.DataFrame(rows)

def write_csv(df, csv_path):
    out = df.copy()
    out['timestamp'] = out['timestamp'].dt.strftime('%Y-%m-%dT%H:%M:%S')
    out.to_csv(csv_path, index=False,
               columns=['timestamp','lat','lon','speed_kmh'])
    print(f"✔ CSV written to {csv_path}")

def build_map(df, html_path, tiles, name, max_speed):
    center = (df.lat.mean(), df.lon.mean())
    m = folium.Map(location=center, zoom_start=13, tiles=None)
    folium.TileLayer(tiles=tiles, name=name, attr=name).add_to(m)

    # limit to speeds in [0, max_speed], then derive vmin/vmax
    valid = df.speed_kmh[(df.speed_kmh >= 0) & (df.speed_kmh <= max_speed)]
    if not valid.empty:
        vmin, vmax = valid.min(), valid.max()
    else:
        # fallback if no data in range
        vmin, vmax = 0, max_speed

    cmap = LinearColormap(
        ['blue', 'red'],
        vmin=vmin,
        vmax=vmax,
        caption='Speed (km/h)'
    )
    cmap.add_to(m)

    for i in range(len(df) - 1):
        a, b = df.iloc[i], df.iloc[i+1]
        folium.PolyLine(
            locations=[(a.lat, a.lon), (b.lat, b.lon)],
            color=cmap(a.speed_kmh),
            weight=4,
            opacity=0.8,
            tooltip=f"{a.speed_kmh:.1f} km/h",
            popup=f"{a.speed_kmh:.1f} km/h"
        ).add_to(m)

    folium.LayerControl().add_to(m)
    m.save(html_path)
    print(f"✔ {name} map written to {html_path}")

def process(fit_in, csv_out, street_html, sat_html, max_speed=100.0):
    df = parse_fit(fit_in)
    if df.empty:
        print("⚠️ No valid GPS records found.")
        sys.exit(1)

    write_csv(df, csv_out)
    build_map(df, street_html,
              tiles='OpenStreetMap',
              name='OpenStreetMap',
              max_speed=max_speed)
    build_map(df, sat_html,
              tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
              name='Esri World Imagery',
              max_speed=max_speed)

def main():
    if len(sys.argv) not in (5,6):
        print(f"Usage: {sys.argv[0]} input.fit output.csv street.html satellite.html [max_speed]")
        sys.exit(1)

    in_fit, out_csv, street, sat = sys.argv[1:5]
    max_sp = float(sys.argv[5]) if len(sys.argv)==6 else 100.0
    process(in_fit, out_csv, street, sat, max_sp)

if __name__ == '__main__':
    main()
