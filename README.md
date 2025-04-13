# NYC Rent + Commute Heatmap

This project visualizes median rent and estimated commute time across NYC neighborhoods, helping renters identify areas with optimal trade-offs between cost and travel time.

## Project Goals

- Visualize rent and commute time at the NTA (Neighborhood Tabulation Area) level
- Combine multiple layers into a score-based ranking
- Create a foundation for future interactive dashboards

### Dependencies

Built using Python 3.10, GeoPandas, Pandas, Matplotlib.

## Data Sources

- HUD Median Rent Estimates (2025) — [huduser.gov](https://www.huduser.gov/portal/datasets/fmr.html)
- NYC NTA Shapefiles — [NYC Open Data Portal](https://data.cityofnewyork.us)
- [Planned] Google Maps Directions API (https://developers.google.com/maps/documentation/directions) — for commute time estimation

## Current Features

- Real-time commute estimates per NTA, based on Google API
- Borough-level Rent estimates (0-4 BR), very low-resolution
- Experimental scoring metric S: Dollars Paid (for Rent) per Commute Time (to Times Square)
- Geospatial visualization (heatmap) of Scores per NTA
- Randomized, placeholder commute data to test pipeline

## Getting Started
Currently not packaged — rerun scripts in `scripts/` manually. Main script is NYCRentHeatmap.py. Env file and API key required for commute data.

### Updates

Google Maps API completed

[Rent per GMaps Commute Time](v0_RentPerCommute_LiveAPI.png)

## Future Plans

- Add API caching & retry logic
- Normalize scoring metrics
- Add map layer interactivity (dropdown menu for toggling views)
- Explore subway access or walkability overlays
- Add options for Departure Time, other inputs

### Future Branches

- ZCTA Rent: replace Borough-level Rent with (High-Res) Zip-level Rent; join to ZCTA geometry (replacing NTA)
- RealTime Rent: Explore scraping options
- MTA Analysis: Explore MTA data
- Caching & Retry Logic: add smart API caching, avoid duplicate calls, respect usage limits
- Dashboard/UI Layer: Optional final layer to add

## File Structure

- `scripts/` – processing + analysis code
- `data/` – shapefiles and downloaded datasets
- `output/` – merged GeoJSONs, CSV exports
- `README.md` – project overview and goals

## Author Notes

This is a personal geospatial project designed to test interactive data visualization and real-world planning tools using open data.
