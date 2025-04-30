#!/usr/bin/env python3
import sys
import os
from fitparse import FitFile
import pandas as pd
import folium
from branca.colormap import LinearColormap
from branca.element import Element  # for injecting custom CSS


def parse_fit(fit_path):
    fit = FitFile(fit_path)
    rows = []
    for rec in fit.get_messages('record'):
        data = {f.name: f.value for f in rec.fields}
        ts = data.get('timestamp')
        raw_lat = data.get('position_lat')
        raw_lon = data.get('position_long')
        speed_ms = data.get('speed')
        if None not in (ts, raw_lat, raw_lon, speed_ms):
            lat = raw_lat * (180.0 / 2**31)
            lon = raw_lon * (180.0 / 2**31)
            speed_kmh = speed_ms * 3.6
            rows.append({
                'timestamp': ts,
                'lat': lat,
                'lon': lon,
                'speed_kmh': speed_kmh
            })
    return pd.DataFrame(rows)


def write_csv(df, csv_path):
    out = df.copy()
    out['timestamp'] = out['timestamp'].dt.strftime('%Y-%m-%dT%H:%M:%S')
    out.to_csv(csv_path, index=False,
               columns=['timestamp','lat','lon','speed_kmh'])
    print(f"✔ CSV written to {csv_path}")


def build_map(df, html_path, *_args, max_speed=100.0):
    # Single-series: combined street + satellite layers
    center = (df.lat.mean(), df.lon.mean())
    m = folium.Map(location=center, zoom_start=13, tiles=None)
    folium.TileLayer('OpenStreetMap', name='Street View').add_to(m)
    folium.TileLayer(
        'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        name='Satellite View', attr='Esri World Imagery'
    ).add_to(m)

    # Colourbar
    valid = df.speed_kmh[(df.speed_kmh >= 0) & (df.speed_kmh <= max_speed)]
    vmin, vmax = (valid.min(), valid.max()) if not valid.empty else (0, max_speed)
    cmap = LinearColormap(['blue', 'red'], vmin=vmin, vmax=vmax, caption='Speed (km/h)')
    cmap.add_to(m)
    css = """
    <style>
    .legend svg text { stroke: white !important; stroke-width: 2px !important; paint-order: stroke fill !important; }
    </style>
    """
    m.get_root().header.add_child(Element(css))

    for i in range(len(df) - 1):
        a, b = df.iloc[i], df.iloc[i+1]
        tooltip = folium.Tooltip(f"{a.speed_kmh:.1f} km/h",
                                 style="color:black; text-shadow:-1px -1px 0 white,1px -1px 0 white,-1px 1px 0 white,1px 1px 0 white;")
        folium.PolyLine([(a.lat, a.lon), (b.lat, b.lon)],
                        color=cmap(a.speed_kmh), weight=6, opacity=0.8,
                        tooltip=tooltip).add_to(m)

    folium.LayerControl().add_to(m)
    m.save(html_path)
    print(f"✔ Combined map written to {html_path}")


def build_map_multi(series_list, html_path, *_args, max_speed=100.0):
    # Multi-series: combined street + satellite, with distinct outlines
    if len(series_list) == 1:
        _, df = series_list[0]
        build_map(df, html_path, max_speed=max_speed)
        return

    all_lats = pd.concat([df.lat for _, df in series_list])
    all_lons = pd.concat([df.lon for _, df in series_list])
    center = (all_lats.mean(), all_lons.mean())
    m = folium.Map(location=center, zoom_start=13, tiles=None)
    folium.TileLayer('OpenStreetMap', name='Street View').add_to(m)
    folium.TileLayer(
        'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        name='Satellite View', attr='Esri World Imagery'
    ).add_to(m)

    all_speeds = pd.concat([
        df.speed_kmh[(df.speed_kmh >= 0) & (df.speed_kmh <= max_speed)]
        for _, df in series_list
    ])
    vmin, vmax = (all_speeds.min(), all_speeds.max()) if not all_speeds.empty else (0, max_speed)
    cmap = LinearColormap(['blue', 'red'], vmin=vmin, vmax=vmax, caption='Speed (km/h)')
    cmap.add_to(m)
    css = """
    <style>
    .legend svg text { stroke: white !important; stroke-width: 2px !important; paint-order: stroke fill !important; }
    </style>
    """
    m.get_root().header.add_child(Element(css))

    outline_colors = ['black', 'yellow', 'lime', 'magenta', 'cyan']
    layer_emojis = ['⚫', '🟡', '🟢', '🟣', '🔵']
    outline_weight, inner_weight = 10, 6
    
    for idx, (name, df) in enumerate(series_list):
        emoji = layer_emojis[idx % len(layer_emojis)]
        fg = folium.FeatureGroup(name=f"{emoji} {name}")
        outline = outline_colors[idx % len(outline_colors)]

        # draw outlines
        for i in range(len(df) - 1):
            a, b = df.iloc[i], df.iloc[i+1]
            folium.PolyLine([(a.lat, a.lon), (b.lat, b.lon)],
                            color=outline, weight=outline_weight, opacity=1).add_to(fg)
        # draw coloured
        for i in range(len(df) - 1):
            a, b = df.iloc[i], df.iloc[i+1]
            tooltip = folium.Tooltip(f"{a.speed_kmh:.1f} km/h",
                                     style="color:black; text-shadow:-1px -1px 0 white,1px -1px 0 white,-1px 1px 0 white,1px 1px 0 white;")
            folium.PolyLine([(a.lat, a.lon), (b.lat, b.lon)],
                            color=cmap(a.speed_kmh), weight=inner_weight, opacity=1,
                            tooltip=tooltip).add_to(fg)
        fg.add_to(m)

    folium.LayerControl().add_to(m)
    m.save(html_path)
    print(f"✔ Combined map written to {html_path}")


def process(fit_in, csv_out, html_out, max_speed=100.0):
    df = parse_fit(fit_in)
    if df.empty:
        print("⚠️ No valid GPS records found.")
        sys.exit(1)
    write_csv(df, csv_out)

    build_map(df, html_out, max_speed=max_speed)


def process_multiple(fit_paths, out_dir, html_out, max_speed=100.0):
    series = []
    for fit in fit_paths:
        df = parse_fit(fit)
        if df.empty:
            print(f"⚠️ No valid GPS records in {fit}, skipping.")
            continue
        base = os.path.splitext(os.path.basename(fit))[0]
        write_csv(df, os.path.join(out_dir, f"{base}_data.csv"))
        series.append((base, df))
    if not series:
        print("⚠️ No valid data to map.")
        sys.exit(1)

    build_map_multi(series, html_out, max_speed=max_speed)


def main():
    if len(sys.argv) not in (5,6):
        print(f"Usage: {sys.argv[0]} input.fit output.csv street.html satellite.html [max_speed]")
        sys.exit(1)
    in_fit, out_csv, street, sat = sys.argv[1:5]
    max_sp = float(sys.argv[5]) if len(sys.argv)==6 else 100.0
    process(in_fit, out_csv, street, sat, max_sp)

if __name__ == '__main__':
    main()


# launcher.py remains unchanged
