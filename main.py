#!/usr/bin/env python3
import sys
from fitparse import FitFile
import pandas as pd
import folium
from branca.colormap import LinearColormap

# --- Parse FIT and convert semicircles → decimal degrees ---
def parse_fit(fit_path):
    fit = FitFile(fit_path)
    rows = []
    for rec in fit.get_messages('record'):
        data = {f.name: f.value for f in rec.fields}
        ts        = data.get('timestamp')
        raw_lat   = data.get('position_lat')
        raw_lon   = data.get('position_long')
        speed_m_s = data.get('speed')
        if None not in (ts, raw_lat, raw_lon, speed_m_s):
            # semicircles → degrees:
            lat = raw_lat * (180.0 / 2**31)
            lon = raw_lon * (180.0 / 2**31)
            rows.append({
                'timestamp':   ts,
                'lat':         lat,
                'lon':         lon,
                'speed_m_s':   speed_m_s
            })
    return pd.DataFrame(rows)

# --- Write CSV ---
def write_csv(df, csv_path):
    out = df.copy()
    out['timestamp'] = out['timestamp'].dt.strftime('%Y-%m-%dT%H:%M:%S')
    out.to_csv(csv_path, index=False,
               columns=['timestamp','lat','lon','speed_m_s'])
    print(f"✔ CSV written to {csv_path}")

# --- Build a map given a tiles setup and output path ---
def build_map(df, html_path, tiles, name):
    center = (df.lat.mean(), df.lon.mean())
    # start with no default tiles, so we can add ours:
    m = folium.Map(location=center, zoom_start=13, tiles=None)
    folium.TileLayer(tiles=tiles, name=name, attr=name).add_to(m)

    # color scale blue→red
    vmin, vmax = df.speed_m_s.min(), df.speed_m_s.max()
    cmap = LinearColormap(
        ['blue','red'],
        vmin=vmin,
        vmax=vmax,
        caption='Speed (m/s)'
    )
    cmap.add_to(m)

    # draw segments
    for i in range(len(df)-1):
        s = df.iloc[i]; e = df.iloc[i+1]
        folium.PolyLine(
            locations=[(s.lat, s.lon),(e.lat, e.lon)],
            color=cmap(s.speed_m_s),
            weight=4,
            opacity=0.8,
        ).add_to(m)

    # add layer control in case you want to toggle (though each map only has one)
    folium.LayerControl().add_to(m)
    m.save(html_path)
    print(f"✔ {name} map written to {html_path}")

def main():
    if len(sys.argv) != 5:
        print(f"Usage: {sys.argv[0]} input.fit output.csv street_map.html satellite_map.html")
        sys.exit(1)

    fit_in, csv_out, street_html, sat_html = sys.argv[1:]
    df = parse_fit(fit_in)
    if df.empty:
        print("⚠️ No valid GPS records found.")
        sys.exit(1)

    write_csv(df, csv_out)

    # Street view (OpenStreetMap)
    build_map(
        df,
        street_html,
        tiles='OpenStreetMap',
        name='Street View'
    )

    # Satellite view (Esri World Imagery)
    build_map(
        df,
        sat_html,
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        name='Esri Satellite'
    )

if __name__ == '__main__':
    main()
