## Settings File for NYC Rent Heatmap
## by Dave Nair
from scripts import constants
from pathlib import Path

## I/O Settings
ZCTA_GEOFILE = "nyc_zcta_2020.shp" # these are actually multiple files that need to be next to each other
RENT_FILE = "HUD_FY2025_FairMarketRent_SmallArea.xls"
MERGED_FILE = "nyc-ScorePerZCTA.geojson"

OUTPUTS_FOLDER = 'outputs'

DESTINATION = "Times Square, New York, NY"
DESTINATIONS = {
	'Work': "410 Tenth Ave Manhattan, NY 10001",
	'Muay Thai': "40 Ludlow St, New York, NY 10002",
	# 'Times Square': "Times Square, New York, NY",
	'Sirovich': "331 E 12th St New York, NY 10003",
	}
CHOSEN_DEPARTURE = 'tomorrow'

## Important Path settings
REPO_PATH = Path(__file__).resolve().parent.parent
DATA_PATH = REPO_PATH / "data"
ZCTA_GEOFILE = DATA_PATH / "processed" / ZCTA_GEOFILE
RENT_FILE = DATA_PATH / "raw" / RENT_FILE

## Logic settings
JOIN_SETTINGS = {'left_on':'zcta', 'right_on':'rent_zip', 'how':'left'}
ANALYSIS_ZIPS = constants.dn_interest_zips

## Decision settings
CHOSEN_METRIC = 'score'
CHOSEN_BR_COUNT = 1
RENT_KEY = f"rent_{CHOSEN_BR_COUNT}BR"

## Troubleshooting settings
VERBOSE = True
VERBOSE_DETAILED = False
