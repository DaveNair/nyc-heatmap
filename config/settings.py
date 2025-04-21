## Settings File for NYC Rent Heatmap
## by Dave Nair
from scripts import constants

## I/O Settings
ZCTA_GEOFILE = "nyc_zcta_2020.shp" # these are actually multiple files that need to be next to each other
RENT_FILE = "HUD_FY2025_FairMarketRent_SmallArea.xls"
MERGED_FILE = "nyc-ScorePerZCTA.geojson"
MERGED_FILE = "test.geojson"

## Logic settings
RENT_JOIN_SETTINGS = {'left_on':'zcta', 'right_on':'rent_zip', 'how'='left'}
ANALYSIS_ZIPS = constants.dn_interest_zips

## Decision settings
CHOSEN_METRIC = 'score'
CHOSEN_BR_COUNT = 1
RENT_KEY = f"rent_{CHOSEN_BR_COUNT}BR"

## Troubleshooting settings
VERBOSE = True
VERBOSE_DETAILED = False
