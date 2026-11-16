import json
import requests
import plotly.express as px
from datetime import datetime
from zoneinfo import ZoneInfo

# 1. Fetch live daily earthquake data from the USGS API.
url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_day.geojson"
response = requests.get(url)
response.raise_for_status()  # Verify the request succeeded
all_eq_data = response.json()

# 2. Extract metadata and earthquake features.
title = all_eq_data['metadata']['title']
all_eq_dicts = all_eq_data['features']

# print(title)
# print(all_eq_dicts)

la_tz = ZoneInfo("America/Los_Angeles")

mags, sizes, lons, lats, depths, eq_titles, eq_times, tsunamis = [], [], [], [], [], [], [], [],
for eq_dict in all_eq_dicts:
    mag = eq_dict['properties']['mag']
    lon = eq_dict['geometry']['coordinates'][0]
    lat = eq_dict['geometry']['coordinates'][1]
    depth = eq_dict['geometry']['coordinates'][2]  # Depth in kilometers
    eq_title = eq_dict['properties']['title']
    tsunami = eq_dict['properties']['tsunami']
    timestamp_ms = eq_dict['properties']['time']

        # 3. Skip entries with missing or negative magnitudes to prevent Plotly errors.
    if mag is not None and mag > 0:
        mags.append(mag)
        sizes.append(mag ** 5)
        lons.append(lon)
        lats.append(lat)
        depths.append(round(depth, 1))
        eq_titles.append(eq_title)
        tsunamis.append("Yes" if tsunami == 1 else "No")

        # Convert Unix timestamp (milliseconds) to Los Angeles time
        dt_la = datetime.fromtimestamp(timestamp_ms / 1000, tz=la_tz)
        eq_times.append(dt_la.strftime("%b %d, %Y %I:%M:%S %p %Z"))

# 4. Build and display the interactive map.
fig = px.scatter_map(
    lat=lats,
    lon=lons,
    size=sizes,
    size_max=50,
    title=title,
    color=mags,
    color_continuous_scale='Portland',
    labels={'color': 'Magnitude'},
    map_style="open-street-map",  # Shows cities, roads, parks, and labels
    center={'lat': 25.0, 'lon': -165.0}, 
    zoom=1.6,
    hover_name=eq_titles,
    custom_data=[tsunamis, depths, eq_times],
)
fig.update_traces(
    hovertemplate=(
        "<b>%{hovertext}</b><br><br>"
        "Magnitude: %{marker.color}<br>"
        "Time (LA): %{customdata[2]}<br>"
        "Depth: %{customdata[1]} km<br>"
        "Latitude: %{lat}<br>"
        "Longitude: %{lon}<br>"
        "Tsunami Warning: %{customdata[0]}"
        "<extra></extra>"
    )
)

fig.show()

from IPython.display import display, HTML
display(HTML("<style>:root { --jp-notebook-max-width: 100% !important; }</style>"))