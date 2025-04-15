## NYC Heatmap 
## by Dave Nair

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import warnings
import os
from pathlib import Path
import sys

import commute

# == INPUTS, CONSTANTS, & UI PLACEHOLDERS ===
## INPUTS

CHOSEN_BR_COUNT = 1
CHOSEN_METRIC = 'score' #; CHOSEN_METRIC = 'rent_1BR'
VERBOSE = True
VERBOSE_DETAILED = False

## INPUTS THAT DON'T CHANGE MUCH
ZCTA_GEOFILE = "nyc_zcta_2020.shp" # these are actually multiple files that need to be next to each other
HUD_ZIP_RENT_FILE = "HUD_FY2025_FairMarketRent_SmallArea.xls"
MERGED_FILE = "nyc-ScorePerZCTA.geojson"

## PATHS & FILENAMES SET
PARENT_PATH = Path(__file__).resolve().parent.parent
DATA_PATH = PARENT_PATH / "data"
ZCTA_GEOFILE = DATA_PATH / "processed" / ZCTA_GEOFILE
HUD_ZIP_RENT_FILE = DATA_PATH / "raw" / HUD_ZIP_RENT_FILE
MERGED_FILE = PARENT_PATH / "outputs" / MERGED_FILE

## we can add $PARENT_PATH to root, so we can run & import stuff inside
sys.path.append(str(PARENT_PATH))
import config.plot_config as plot_config


# === FUNCTIONS ===

def check(dataframe, name='', N=5):
	global VERBOSE
	if VERBOSE:
		print(name)
		print(dataframe.head(N))
		return True
	return False

def sanity_check(dataframe, name=''):
	global VERBOSE_DETAILED
	if VERBOSE_DETAILED:
		print(name)
		print(dataframe.head())
		return True
	return False

def plot(dataframe, column=CHOSEN_METRIC, legend=True, missing_kwds={'color':'lightgrey'}):
	settings = plot_config.SETTINGS.get(column, {})
	## let's interpret ALL settings
	cmap = settings.get("colorscale", "viridis")
	if settings.get("reverse_color", False):
		cmap += '_r'
	alpha = settings.get("alpha", 1)
	vmin = settings.get("vmin", None)
	vmax = settings.get("vmax", None)
	label = settings.get("label", column)
	units = settings.get("units", "")
	fmt = settings.get("tooltip_fmt", "{:.0f}")
	edge_color = settings.get("edge_color", "black")
	edge_width = settings.get("edge_width", 0.1)

	dataframe.plot(column=column, cmap=cmap, alpha=alpha, legend=legend, 
		edgecolor=edge_color, linewidth=edge_width, 
		vmin=vmin, vmax=vmax, missing_kwds=missing_kwds)

	# Title: (example) "Rent per Commute Minute ($/min)"
	title = f"{label} ({units})" if units else label
	plt.title(title)
	plt.show()
	return True

def file_exists(filepath):
	return os.path.exists(filepath)

def load_geoms(geomfile, RenameDict):
	'''This function includes all transformations.'''
	gdata = gpd.read_file(geomfile)
	gdata = gdata.rename(columns=RenameDict)
	# now our normalized keys should work
	gdata = gdata[list(RenameDict.values())]
	gdata['zcta'] = gdata['zcta'].astype(str).str.zfill(5)
	#### add centroids to nta
	gdata = gdata.to_crs(epsg=4326) ## coord ref system WGS84 (EPSG:4326) << WE MIGHT CHANGE THIS
	with warnings.catch_warnings():
		warnings.filterwarnings("ignore", message='Geometry is in a geographic CRS.')
		## UserWarning keeps getting thrown about calculating centroids 
		gdata['centroid'] = gdata.geometry.centroid
	gdata['lat'] = gdata['centroid'].y 
	gdata['lon'] = gdata['centroid'].x
	## after the centroid step, we've added an extra geom column - lets recast to prevent downstream issues
	gdata = gpd.GeoDataFrame(gdata, geometry='geometry')
	gdata.set_crs("EPSG:4326", inplace=True) # just re-enforcing crs
	sanity_check(gdata, name='NTA')
	return gdata

def load_rent(rentfile, RenameDict):
	'''This function includes all transformations.'''
	global NYC_ZIPS
	rdata = pd.read_excel(rentfile)
	rdata = rdata.rename(columns=RenameDict)
	## now RENT_KEY and others should work!
	rdata = rdata[RenameDict.values()]
	rdata['rent_zip'] = rdata['rent_zip'].astype(str).str.zfill(5)
	## we still need to:
	## - filter to NYC Zips
	rdata = rdata[(rdata['rent_zip'].isin(NYC_ZIPS))]
	# we can add county-to-borough-to-zip logic some other time if we need to
	sanity_check(rdata, name='RENT')
	return rdata

def store_df(dataframe, outpath, OVERWRITE=False, DRIVER="GeoJSON", RemoveCols=False, PrettyPrint=False):
	'''Geopandas has a bad prettyprint - we'll be using json.'''
	import json
	if RemoveCols!=False:
		outdf = dataframe.drop(columns=RemoveCols)
	else:
		outdf = dataframe
	if OVERWRITE!=True and not os.path.exists(outpath):
		if PrettyPrint==False:
			outdf.to_file(outpath, driver=DRIVER)
		elif PrettyPrint==True:
			## switch to json
			geojson_dict = json.loads(outdf.to_json())
			geojson_dict["crs"] = {"type": "name", "properties": {"name": "EPSG:4326"}} # preserving crs in json
			with open(outpath.replace('.geojson','.json'), "w") as f:
				json.dump(geojson_dict, f, indent=2)
		print(f"Wrote dataframe to location: {outpath}")
		return True
	print(f"Could not write dataframe to location: {outpath}\nPlease check if the location already exists.")




# === MAIN ===

RENT_KEY = f"rent_{CHOSEN_BR_COUNT}BR"

## check output (/cache)
if MERGED_FILE not in [False,True] and file_exists(MERGED_FILE):
	print(f"Found cached output file: {MERGED_FILE}\nLoading file and skipping transformations...")
	geom_df = gpd.read_file(MERGED_FILE)
	plot(geom_df)#, SCORE_KEY)
else:
	## this is the MAIN
	# load nta & rent
	geom_df = load_geoms(ZCTA_GEOFILE, RenameDict=ZCTA_COLUMN_RENAMES)
	rent_df = load_rent(HUD_ZIP_RENT_FILE, RenameDict=HUD_COLUMN_RENAMES)
	# merge
	geom_df = geom_df.merge(rent_df, left_on='zcta', right_on='rent_zip', how='left')
	## apply google commute times & scores
	geom_df[COMMUTE_KEY] = geom_df.apply(lambda row: commute.get_google_time(row['lat'], row['lon']),axis = 1)
	geom_df[SCORE_KEY] = geom_df[RENT_KEY] / (geom_df[COMMUTE_KEY]+1)
	plot(geom_df)#, SCORE_KEY)
	store_df(geom_df, MERGED_FILE, OVERWRITE=False, RemoveCols=['centroid'], PrettyPrint=False)

print("Done! Hope you enjoyed!")

