## general config settings for nyc-heatmap

SETTINGS = {
    "score": {
        "label": "Rent Dollars per Commute Minute",
        "units": "$/min",
        "colorscale": "turbo", #"reverse_color": True,
        "alpha": 0.9,
        "edgecolor": "white",
        "vmin": 0,
        "vmax": 200,
        "interactive": True,
        "tooltip_fmt": "{:.2f}",
        "normalize": False
    },
    "gravity": {
        "label": "Rent Dollars per Square Commute",
        "units": "$/min^2",
        "colorscale": "magma",
        "alpha": 0.9,
        "edgecolor": "white",
        "interactive": True,
        "tooltip_fmt": "{:.2f}",
        "normalize": False
    },
    "antigravity": {
        "label": "Square Commute per Rent",
        "units": "min^2 per $",
        "colorscale": "magma",
        "alpha": 0.9,
        "edgecolor": "white",
        "vmin": 0,
        "vmax": 100,
        "interactive": True,
        "tooltip_fmt": "{:.2f}",
        "normalize": False
    },
    "commute_minutes": {
        "label": "Commute Time to Times Square",
        "units": "min",
        "colorscale": "Blues",
        "vmin": 0,
        "vmax": 60,
        "interactive": True,
        "tooltip_fmt": "{:.0f}",
        "normalize": False
    },
    "rent_1BR": {
        "label": "Estimated Rent (1BR)",
        "units": "$",
        "colorscale": "Greens",
        "vmin": 900,
        "vmax": 5000,
        "interactive": True,
        "tooltip_fmt": "${:,.0f}",
        "normalize": False
    },
    "rent_0BR": {
        "label": "Estimated Rent (Studio)",
        "units": "$",
        "colorscale": "Greens",
        "vmin": 900,
        "vmax": 5000,
        "interactive": True,
        "tooltip_fmt": "${:,.0f}",
        "normalize": False
    },
    "rent_2BR": {
        "label": "Estimated Rent (2BR)",
        "units": "$",
        "colorscale": "Greens",
        "vmin": 900,
        "vmax": 5000,
        "interactive": True,
        "tooltip_fmt": "${:,.0f}",
        "normalize": False
    },
    "rent_3BR": {
        "label": "Estimated Rent (3BR)",
        "units": "$",
        "colorscale": "Greens",
        "vmin": 900,
        "vmax": 5000,
        "interactive": True,
        "tooltip_fmt": "${:,.0f}",
        "normalize": False
    },
    "rent_4BR": {
        "label": "Estimated Rent (4BR)",
        "units": "$",
        "colorscale": "Greens",
        "vmin": 900,
        "vmax": 5000,
        "interactive": True,
        "tooltip_fmt": "${:,.0f}",
        "normalize": False
    }
}
