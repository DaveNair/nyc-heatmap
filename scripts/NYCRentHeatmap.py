## NYC Heatmap 
## by Dave Nair

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import warnings
import os
from pathlib import Path

import commute

# == INPUTS, CONSTANTS, & UI PLACEHOLDERS ===
CHOSEN_BR_COUNT = 1
COMMUTE_KEY = 'commute_minutes'
SCORE_KEY = 'score'
CHOSEN_LAYER = SCORE_KEY
VERBOSE = True
VERBOSE_DETAILED = True

SCRIPT_PATH = Path(__file__).resolve().parent ## this is current wd of THIS FILE
PARENT_PATH = SCRIPT_PATH.parent
RAW_DATA_PATH = PARENT_PATH / "data" / "raw"
OUTPUTS_PATH = PARENT_PATH / "outputs"
NTA_GEOFILE = RAW_DATA_PATH / "nynta2020_25a" / "nynta2020.shp"
HUD_COUNTY_RENT_FILE = RAW_DATA_PATH / "HUD_FY2025_FairMarketRent_50p_county.xls"
MERGED_FILE = OUTPUTS_PATH / "nyc-countyRent_perNTA.geojson"
NYC_COUNTIES = [i+' County' for i in 'Bronx,Kings,New York,Queens,Richmond'.split(',')]

# getting out of HUD, NTA, and other datasource-specific stuff
HUD_COLUMN_RENAMES = {'rent_50_1':'rent_1BR',
	'rent_50_0':'rent_0BR', 'rent_50_2':'rent_2BR', 'rent_50_3':'rent_3BR', 'rent_50_4':'rent_4BR',
	'pop2020':'pop_2020', 'state_alpha':'state_alpha',
	'cntyname':'county_name', 'county_code':'county_id', 'hud_areaname':'hud_area_name'}
POP_KEY = HUD_COLUMN_RENAMES['pop2020']
NTA_COLUMN_RENAMES = {'BoroName':'borough', 
	'NTA2020':'nta_id', 'NTAName':'nta_name', # 'NTAType':'nta_type', 
	# 'CDTA2020':'cdta_id', 'CDTAName':'cdta_name',
	'Shape_Leng':'geo_length', 'Shape_Area':'geo_area'}

# inputs are interpretted
RENT_KEY = "rent_{0}BR".format(CHOSEN_BR_COUNT)
if CHOSEN_BR_COUNT==0:
	RENT_TITLE = "Studio Rent ($)"
else:
	RENT_TITLE = "{0}BR Rent ($)".format(CHOSEN_BR_COUNT)

TITLES = {
	RENT_KEY : RENT_TITLE,
	POP_KEY : 'Pop. (2020)',
	COMMUTE_KEY : 'Commute Time (mins)',
	SCORE_KEY : 'Score, Rent per Commute [$/min]'
	}

MAP_LAYERS = {
	RENT_TITLE: RENT_KEY,
	TITLES[POP_KEY]:'pop_2020',
	TITLES[COMMUTE_KEY]:'commute_minutes',
	TITLES[SCORE_KEY]:'score'}

## program interprets your choices; don't change below here
CHOSEN_METRIC = MAP_LAYERS[TITLES[CHOSEN_LAYER]]
TITLES[RENT_KEY] = "{0}BR Rent ($)" ## just gonna messily add the Rent NBR value to titles now...

# IMPORTANT_COLUMNS = ['nta_id', 'nta_name', 'borough', 'geometry',
# 	'centroid', 'lat', 'lon', RENT_KEY, POP_KEY, 
# 	'state_alpha', 'county_name']


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

def plot(dataframe, column, color='plasma', legend=True, keywords={'color':'lightgrey'}):
	global TITLES
	dataframe.plot(column=column, cmap=color, legend=legend, missing_kwds=keywords)
	plt.title(TITLES[column])
	plt.show()
	return True

def file_exists(filepath):
	return os.path.exists(filepath)

def load_geoms(geomfile, RenameDict):
	'''This function includes all transformations.'''
	gdata = gpd.read_file(geomfile)
	gdata = gdata.rename(columns=RenameDict)
	gdata = gdata[list(RenameDict.values())+['geometry']]
	# now our normalized keys should work
	sanity_check(gdata, name='NTA')
	#### add centroids to nta
	gdata = gdata.to_crs(epsg=4326) ## coord ref system WGS84 (EPSG:4326)
	with warnings.catch_warnings():
		warnings.filterwarnings("ignore", message='Geometry is in a geographic CRS.')
		## UserWarning keeps getting thrown about calculating centroids 
		gdata['centroid'] = gdata.geometry.centroid
	gdata['lat'] = gdata['centroid'].y 
	gdata['lon'] = gdata['centroid'].x
	## after the centroid step, we've added an extra geom column - lets recast to prevent downstream issues
	gdata = gpd.GeoDataFrame(gdata, geometry='geometry')
	gdata.set_crs("EPSG:4326", inplace=True) # just re-enforcing crs
	return gdata

def load_rent(rentfile, RenameDict):
	'''This function includes all transformations.'''
	rdata = pd.read_excel(rentfile)
	rdata = rdata.rename(columns=RenameDict)
	rdata = rdata[RenameDict.values()]
	## now RENT_KEY and others should work!
	sanity_check(rdata, name='RENT')

	## specifically for HUD Data, we still need to:
	## - filter to NYC (state=NY && county.isin(counties))
	## - add boroughs
	rdata = rdata[
		(rdata['state_alpha']=='NY') 
		& (rdata['county_name'].isin(NYC_COUNTIES))
		]

	county_to_borough_dict = {'New York County':'Manhattan', 
		'Kings County':'Brooklyn',
		'Queens County':'Queens',
		'Bronx County':'Bronx',
		'Richmond County':'Staten Island'}

	rdata['rent_borough'] = rdata['county_name'].map(county_to_borough_dict)
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

## check output (/cache)
if MERGED_FILE not in [False,True] and file_exists(MERGED_FILE):
	print(f"Found cached output file: {MERGED_FILE}\nLoading file and skipping transformations...")
	nta_gdf = gpd.read_file(MERGED_FILE)
	plot(nta_gdf, SCORE_KEY)
else:
	## this is the MAIN
	# load nta & rent
	nta_gdf = load_geoms(NTA_GEOFILE, RenameDict=NTA_COLUMN_RENAMES)
	rent_df = load_rent(HUD_COUNTY_RENT_FILE, RenameDict=HUD_COLUMN_RENAMES)
	# merge
	nta_gdf = nta_gdf.merge(rent_df, left_on='borough', right_on='rent_borough', how='left')
	## apply google commute times & scores
	nta_gdf[COMMUTE_KEY] = nta_gdf.apply(lambda row: commute.get_google_time(row['lat'], row['lon']),axis = 1)
	nta_gdf[SCORE_KEY] = nta_gdf[RENT_KEY] / (nta_gdf[COMMUTE_KEY]+1)
	plot(nta_gdf, SCORE_KEY)
	store_df(nta_gdf, MERGED_FILE, OVERWRITE=False, RemoveCols=['centroid'], PrettyPrint=False)

print("Done! Hope you enjoyed!")

