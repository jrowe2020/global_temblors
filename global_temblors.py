import json
import requests
import plotly.express as px
from datetime import datetime
from zoneinfo import ZoneInfo

# Toggle to True to test the warning banner even when no tsunami == 1 exists in the data
test = False

# 1. Fetch live daily earthquake data from the USGS API.
url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_day.geojson"
response = requests.get(url)
response.raise_for_status()  # Verify the request succeeded
all_eq_data = response.json()

# 2. Extract metadata and earthquake features.
title = all_eq_data['metadata']['title']
all_eq_dicts = all_eq_data['features']

# --- ADD FAKE EARTHQUAKE FOR TESTING ---
fake_eq = {
    'properties': {
        'mag': 7.8,
        'title': 'M 7.8 - 120 km W of Portland, Oregon (TEST)',
        'place': '120 km W of Portland, Oregon',
        'time': 1731750000000,  # Unix timestamp in milliseconds
        'tsunami': 1
    },
    'geometry': {
        'coordinates': [-124.5, 45.5, 10.0]  # [lon, lat, depth]
    }
}
all_eq_dicts.append(fake_eq)
# ---------------------------------------

la_tz = ZoneInfo("America/Los_Angeles")

mags, sizes, lons, lats, depths, eq_titles, eq_times, tsunamis = [], [], [], [], [], [], [], [],

marker_colors = []
tsunami_warnings = []

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

        # Highlight tsunami earthquakes and record their details
    if tsunami == 1:
        marker_colors.append('red')  # Distinct highlight color
        warning_text = f"{eq_title} <br>(Lat: {lat}, Lon: {lon})"
        tsunami_warnings.append(warning_text)
    else:
        marker_colors.append(mag)    # Standard magnitude-based value

# Determine if the warning banner should be displayed
has_tsunami = (1 in tsunamis) or test

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

if tsunami_warnings:
    details = "<br>".join(tsunami_warnings)
    banner_text = f"⚠️ TSUNAMI WARNING ACTIVE ⚠️<br>{details}"
else:
    banner_text = "No Active Tsunami Warnings"

# Example using fig.add_annotation in Plotly:
fig.add_annotation(
    text=banner_text,
    xref="paper", yref="paper",
    x=0.5, y=0.98,
    showarrow=False,
    font=dict(size=14, color="white"),
    bgcolor="crimson",
    borderpad=8
)


fig.show()

from IPython.display import display, HTML
display(HTML("<style>:root { --jp-notebook-max-width: 100% !important; }</style>"))