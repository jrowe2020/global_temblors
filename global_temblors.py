import json
import requests
import plotly.express as px
from datetime import datetime
from zoneinfo import ZoneInfo

# Toggle to True to test the warning banner even when no tsunami == 1 exists in the data
TEST_MODE = True


# 1. Fetch live daily earthquake data from the USGS API.
url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_day.geojson"
response = requests.get(url)
response.raise_for_status()  # Verify the request succeeded
all_eq_data = response.json()

# 2. Extract metadata and earthquake features.
title = all_eq_data['metadata']['title']
all_eq_dicts = all_eq_data['features']

# --- ADD FAKE EARTHQUAKE FOR TESTING ---
if TEST_MODE:
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
    },
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
        warning_text = f"{eq_title} <br>(Mag: {mag}, Lat: {lat}, Lon: {lon})"
        Warning_link = f"https://www.tsunami.gov"
        tsunami_warnings.append(warning_text)
    else:
        marker_colors.append('mag')    # Standard magnitude-based value


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

# 5. Add the Tsunami Warning Banner with clickable HTML link

tsunami_url = "https://www.tsunami.gov/"
link_html = f"<a href='{tsunami_url}' target='_blank' style='color: #ffe600;'>Official Tsunami Warning Center (Tsunami.gov)</a>"
    
if tsunami_warnings:
    # Active Tsunami Alert Styling (Red)
    banner_text = (
        "<b>TSUNAMI WARNING ACTIVE</b><br>"
        + "<br>".join(tsunami_warnings)
        + f"<br>More info: {link_html}"
    )
    bg_color = "crimson"
    border_color = "darkred"
    y_pos = 0.95
else:
    # No Tsunami Warning Styling (Blue)
    banner_text = (
        f"No active tsunami advisories noted:"
        f" <br>{link_html}"
    )
    bg_color = "gray"
    border_color = "navy"
    y_pos = 3.00



# add instruction and attribution text
instruction_text = (
    "<b>Navigation instructions:</b><br>"
    "• <b>Zoom:</b>  Pinch or double-click<br>"
    "• <b>Pan:</b>  Drag with finger or cursor<br>"
    "• <b>Get Earthquake Details:</b>  Tap or click any colored circle"
)

attribution_text = (
    "<b>Project Credits & Data Sources:</b><br>"
    "• Base code adapted from the <i>Python Crash Course</i> earthquake visualization exercise.<br>"
    "• Seismic event data provided by the U.S. Geological Survey (USGS).<br>"
    "• Enhanced features, research, and error handling developed with assistance from Google."
)

# Update layout
fig.update_layout(
    autosize=True,
    dragmode='pan',
    # Since the tsunami warning moved to the top right, b=85 gives plenty of room for the colorbar + attribution
    margin=dict(l=12, r=12, t=48, b=170), 
    font=dict(family='-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'),
    title=dict(font=dict(size=16,color="#111111"), x=0.5, xanchor='center'),
    coloraxis_colorbar=dict(
        orientation="h",
        yanchor="top",
        y=-0.02,          # Sits right below the bottom edge of the map
        xanchor="left",   # Left-aligns the colorbar so it lines up with the attribution below
        x=0.01,
        len=0.8,
        thickness=14
    )
)

# Example using fig.add_annotation in Plotly:
fig.add_annotation(
    text=banner_text,
    xref="paper", yref="paper",
    x=0.5,              # Centers horizontally on the map
    y=0.99,             # Keeps it tucked neatly near the top edge
    xanchor="center",   # Anchors the middle of the box at x=0.5
    yanchor="top",      # Grows downward from the top edge
    align="center", 
    showarrow=False,
    font=dict(size=13, color="white"),
    bgcolor=bg_color,
    bordercolor=border_color,
    borderwidth=1,
    borderpad=7
)

# Instruction text box in top left corner
fig.add_annotation(
    text=instruction_text,
    xref="paper",
    yref="paper",
    x=0.02,             # Flush near the left margin
    y=0.02,             # Inside the bottom edge of the map canvas, above the colorbar
    xanchor="left",     # Grows rightward from the left edge
    yanchor="bottom",   # Anchors from the bottom up so multi-line text never clips downward
    align="left",
    showarrow=False,
    bgcolor=bg_color,
    bordercolor=border_color,
    borderwidth=1,
    borderpad=7,
    font=dict(size=12, color="#FFFFFF")
)

# Instructions/attribution text box tucked in the lower-left corner above the colorbar
fig.add_annotation(
    text=attribution_text,
    xref="paper",
    yref="paper",
    x=0.02,             # Flush near the left margin
    y=-0.27,             # Inside the bottom edge of the map canvas, above the colorbar
    xanchor="left",     # Grows rightward from the left edge
    yanchor="bottom",   # Anchors from the bottom up so multi-line text never clips downward
    align="left",
    showarrow=False,
    bgcolor="rgba(248, 249, 250, 0.95)",
    bordercolor="#cccccc",
    borderwidth=1,
    borderpad=7,
    font=dict(size=11, color="#222222")
)

# Export HTML with native 1.0 viewport scaling for crisp mobile rendering
html_str = fig.to_html(
    full_html=True,
    include_plotlyjs=True,
    config={'responsive': True, 'displayModeBar': False}
)

mobile_head = """<head>
    <meta name="viewport" content="width=device-width, initial-scale=0.75, maximum-scale=1.0, user-scalable=no">
    <style>
        html, body {
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100dvh;
            display: flex;
            justify-content: center;
            align-items: center;
            overflow: hidden;
            background: #ffffff;
        }
        .plotly-graph-div {
            width: 100vw !important;
            height: 92dvh !important;
        }
    </style>"""



html_str = html_str.replace('<head>', mobile_head, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html_str)

fig.show()

