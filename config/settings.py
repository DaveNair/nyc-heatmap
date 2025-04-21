## Settings File for NYC Rent Heatmap
## by Dave Nair

ZCTA_GEOFILE = "nyc_zcta_2020.shp" # these are actually multiple files that need to be next to each other
RENT_FILE = "HUD_FY2025_FairMarketRent_SmallArea.xls"
MERGED_FILE = "nyc-ScorePerZCTA.geojson"
MERGED_FILE = "test.geojson"

RENT_JOIN_SETTINGS = {'left_on':'zcta', 'right_on':'rent_zip', 'how'='left'}

CHOSEN_METRIC = 'score'
