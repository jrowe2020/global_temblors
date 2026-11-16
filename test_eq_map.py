from eq_world_map import format_eq_title, build_eq_map

def make_sample_eq(title="M 5.0 - Test Location", mag=5.0, tsunami=0):
    """Helper to create a mock USGS earthquake dictionary."""
    return {
        "properties": {
            "mag": mag,
            "title": title,
            "tsunami": tsunami,
        },
        "geometry": {
            "coordinates": [-122.67, 45.51, 10.0]
        }
    }

def test_hover_banner_shown_when_tsunami_is_1():
    """Verify the warning banner is prepended when tsunami == 1."""
    eq = make_sample_eq(title="M 7.8 - Offshore", tsunami=1)
    result = format_eq_title(eq)
    assert result == "⚠️ TSUNAMI WARNING ⚠️<br>M 7.8 - Offshore"

def test_hover_banner_hidden_when_tsunami_is_0():
    """Verify the title remains unchanged when tsunami == 0."""
    eq = make_sample_eq(title="M 4.2 - Inland", tsunami=0)
    result = format_eq_title(eq)
    assert result == "M 4.2 - Inland"

def test_map_annotation_added_when_tsunami_present():
    """Verify Plotly figure includes the top banner annotation when tsunami == 1."""
    eq_list = [
        make_sample_eq(tsunami=0),
        make_sample_eq(title="M 8.1 - Coast", tsunami=1),
    ]
    fig = build_eq_map(eq_list)
    
    annotations = fig.layout.annotations
    assert len(annotations) == 1
    assert "TSUNAMI ALERT" in annotations[0].text
    assert annotations[0].bgcolor == "crimson"

def test_no_map_annotation_without_tsunami():
    """Verify Plotly figure has no alert annotation when all tsunami flags are 0."""
    eq_list = [make_sample_eq(tsunami=0)]
    fig = build_eq_map(eq_list)
    
    assert len(fig.layout.annotations) == 0