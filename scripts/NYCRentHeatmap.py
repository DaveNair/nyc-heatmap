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
CHOSEN_LAYER = SCORE_KEY #; CHOSEN_LAYER = 'rent_1BR'
VERBOSE = True
VERBOSE_DETAILED = True

SCRIPT_PATH = Path(__file__).resolve().parent ## this is current wd of THIS FILE
PARENT_PATH = SCRIPT_PATH.parent
DATA_PATH = PARENT_PATH / "data"
OUTPUTS_PATH = PARENT_PATH / "outputs"

# FILENAMES BELOW
ZCTA_GEOFILE = DATA_PATH / "processed" / "nyc_zcta" / "nyc_zcta_2020.shp"
HUD_ZIP_RENT_FILE = DATA_PATH / "raw" / "HUD_FY2025_FairMarketRent_SmallArea.xls"
MERGED_FILE = OUTPUTS_PATH / "nyc-RentPerZCTA.geojson"

# getting out of HUD, NTA, and other datasource-specific stuff
HUD_COLUMN_RENAMES = {'SAFMR\n1BR':'rent_1BR',
	'SAFMR\n0BR':'rent_0BR', 'SAFMR\n2BR':'rent_2BR', 'SAFMR\n3BR':'rent_3BR', 'SAFMR\n4BR':'rent_4BR',
	# 'pop2020':'NULL', # 'state_alpha':'state_alpha',
	'ZIP\nCode':'rent_zip', 'HUD Area Code':'hud_area_code', 'HUD Fair Market Rent Area Name':'hud_area_name'}
POP_KEY = HUD_COLUMN_RENAMES.get('pop2020', 'NULL') # we don't have population data in this dataset... we could join later
ZCTA_COLUMN_RENAMES = {'ZCTA5CE10':'zcta', 
	'ALAND10':'area_land','AWATER10':'area_water', 'INTPTLAT10':'lat_census', 'INTPTLON10':'lon_census', 
	'geometry':'geometry'}

NYC_COUNTIES = [i+' County' for i in 'Bronx,Kings,New York,Queens,Richmond'.split(',')]
NYC_ZIPS = ['10001', '10002', '10003', '10004', '10005', '10006', '10007', '10009', '10010',
    '10011', '10012', '10013', '10014', '10016', '10017', '10018', '10019', '10020',
    '10021', '10022', '10023', '10024', '10025', '10026', '10027', '10028', '10029',
    '10030', '10031', '10032', '10033', '10034', '10035', '10036', '10037', '10038',
    '10039', '10040', '10044', '10065', '10069', '10075', '10128', '10280', '10282',
    '10301', '10302', '10303', '10304', '10305', '10306', '10307', '10308', '10309',
    '10310', '10312', '10314', '10451', '10452', '10453', '10454', '10455', '10456',
    '10457', '10458', '10459', '10460', '10461', '10462', '10463', '10464', '10465',
    '10466', '10467', '10468', '10469', '10470', '10471', '10472', '10473', '10550',
    '11101', '11102', '11103', '11104', '11105', '11106', '11201', '11203', '11204',
    '11205', '11206', '11207', '11208', '11209', '11210', '11211', '11212', '11213',
    '11214', '11215', '11216', '11217', '11218', '11219', '11220', '11221', '11222',
    '11223', '11224', '11225', '11226', '11228', '11229', '11230', '11231', '11232',
    '11233', '11234', '11235', '11236', '11237', '11238', '11239', '11354', '11355',
    '11356', '11357', '11358', '11360', '11361', '11362', '11363', '11364', '11365',
    '11366', '11367', '11368', '11369', '11370', '11372', '11373', '11374', '11375',
    '11377', '11378', '11379', '11385', '11411', '11412', '11413', '11414', '11415',
    '11416', '11417', '11418', '11419', '11420', '11421', '11422', '11423', '11426',
    '11427', '11428', '11429', '11430', '11432', '11433', '11434', '11435', '11436',
    '11691', '11692', '11693', '11694', '11697']


# inputs are interpretted
RENT_KEY = f"rent_{CHOSEN_BR_COUNT}BR"
if CHOSEN_BR_COUNT==0:
	RENT_TITLE = "Studio Rent ($)"
else:
	RENT_TITLE = f"{CHOSEN_BR_COUNT}BR Rent ($)"

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
TITLES[RENT_KEY] = RENT_TITLE ## just gonna messily add the Rent NBR value to titles now...

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

def plot(dataframe, column=CHOSEN_METRIC, color='plasma', legend=True, keywords={'color':'lightgrey'}):
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

