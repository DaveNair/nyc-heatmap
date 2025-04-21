## NYC Heatmap 
## by Dave Nair

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import json
import warnings
import os
from pathlib import Path
import sys

from config import plot_config
from lib import utils
from lib.utils import check, sanity_check
import commute
from constants import RENT_COLUMN_RENAMES, GEOM_COLUMN_RENAMES, COMMUTE_KEY, SCORE_KEY, GRAVIKEY, ANTIGRAV_KEY, NYC_ZIPS, BAD_VAL
import retry_logic
from retry_logic import MAX_API_CALLS_PER_RUN, MAX_API_CALLS_PER_MONTH
from config.settings import ZCTA_GEOFILE, RENT_FILE, MERGED_FILE, JOIN_SETTINGS, CHOSEN_BR_COUNT, CHOSEN_METRIC, VERBOSE, VERBOSE_DETAILED
from config.settings import ANALYSIS_ZIPS

## PATHS & FILENAMES SET
PARENT_PATH = Path(__file__).resolve().parent.parent
DATA_PATH = PARENT_PATH / "data"
ZCTA_GEOFILE = DATA_PATH / "processed" / ZCTA_GEOFILE
RENT_FILE = DATA_PATH / "raw" / RENT_FILE
MERGED_FILE = PARENT_PATH / "outputs" / MERGED_FILE


# === FUNCTIONS ===

def estimate_upcoming_api_calls(dataframe, dest_col=False, lat_col='lat', lon_col='lon', intro='Beginning API requests...\n'):
	if intro:
		print(intro)
	unique_origins = len(dataframe[[lat_col, lon_col]].dropna().drop_duplicates())
	if dest_col==False:
		unique_destinations = 1
	else:
		unique_destinations = len(dataframe[[dest_col]].dropna().drop_duplicates())
	current_estimate = unique_origins*unique_destinations

	## print the usage & MAX as well, if this is verbose
	if VERBOSE:
		run_percentage = float(current_estimate) / MAX_API_CALLS_PER_RUN
		monthly_percentage = float(_PERSISTED_PRECOUNTER+current_estimate) / MAX_API_CALLS_PER_MONTH
		print(f"Upcoming API calls:\n\tRun Max: \t{current_estimate} \t\t/{MAX_API_CALLS_PER_RUN} ({run_percentage*100:.1f}%)\n\tMonthly Max: \t{current_estimate}+{_PERSISTED_PRECOUNTER} \t/{MAX_API_CALLS_PER_MONTH} ({monthly_percentage*100:.1f}%)\n")
	return current_estimate

def prompt_user_for_confirmation(number_to_confirm):
	if (number_to_confirm >= MAX_API_CALLS_PER_RUN) or ((_PERSISTED_PRECOUNTER+number_to_confirm) >= MAX_API_CALLS_PER_MONTH) or VERBOSE_DETAILED:
		monthly_percentage = float(_PERSISTED_PRECOUNTER+number_to_confirm) / MAX_API_CALLS_PER_MONTH
		run_percentage = float(number_to_confirm) / MAX_API_CALLS_PER_RUN
		print(f"Detected large amount of upcoming API calls:\n\t{number_to_confirm} calls ({monthly_percentage*100:.1f}% monthly max; {run_percentage*100:.1f}% run max)")
		## check user
		user_input = False
		while user_input==False or user_input[0]!='y':
			user_input = input("Do you want to continue? [Y]es/[N]o\n?>> ").strip().lower()
			if user_input=='':
				## we will ASSUME the user is ok continuing and meant to click Yes...
				user_input = 'y'
			if user_input[0] in ['q','n']:
				print("Exiting...")
				sys.exit(1)
		print("Continuing...")
	pass

# def plot(dataframe, column=CHOSEN_METRIC, legend=True, missing_kwds={'color':'lightgrey'}):
# 	settings = plot_config.SETTINGS.get(column, {})
# 	## let's interpret ALL settings
# 	cmap = settings.get("colorscale", "viridis")
# 	if settings.get("reverse_color", False):
# 		cmap += '_r'
# 	alpha = settings.get("alpha", 1)
# 	vmin = settings.get("vmin", None)
# 	vmax = settings.get("vmax", None)
# 	label = settings.get("label", column)
# 	units = settings.get("units", "")
# 	fmt = settings.get("tooltip_fmt", "{:.0f}")
# 	edge_color = settings.get("edge_color", "black")
# 	edge_width = settings.get("edge_width", 0.1)

# 	dataframe.plot(column=column, cmap=cmap, alpha=alpha, legend=legend, 
# 		edgecolor=edge_color, linewidth=edge_width, 
# 		vmin=vmin, vmax=vmax, missing_kwds=missing_kwds)

# 	# Title: (example) "Rent per Commute Minute ($/min)"
# 	title = f"{label} ({units})" if units else label
# 	plt.title(title)
# 	plt.show()
# 	return True

def file_exists(filepath):
	return os.path.exists(filepath)

def load_geoms(geomfile, RenameDict, AdditionalFilters=None):
	'''This function includes all transformations.'''
	gdata = gpd.read_file(geomfile)
	gdata = gdata.rename(columns=RenameDict)
	# now our normalized keys should work
	gdata = gdata[list(RenameDict.values())]
	gdata['zcta'] = gdata['zcta'].astype(str).str.zfill(5)
	## going to do Additional Filtering here
	if AdditionalFilters:
		if type(AdditionalFilters)==list:
			## assume this is a list of zip codes, as per our latest geom
			filter_col = 'zcta'
			gdata = gdata[gdata[filter_col].isin(AdditionalFilters)].copy()
		elif type(AdditionalFilters)==dict:
			filter_col = list(AdditionalFilters.keys())[0]
			filter_val = list(AdditionalFilters.values())[0]
			gdata = gdata[gdata[filter_col].isin(filter_vals)].copy()
		else:
			print(f"You have provided an unidentified type for AdditionalFilters: {type(AdditionalFilters)}\nPlease check again. Exiting."); sys.exit(1)

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

def load_rent(rentfile, RenameDict, AdditionalFilters=NYC_ZIPS):
	'''This function includes all transformations.'''
	rdata = pd.read_excel(rentfile)
	rdata = rdata.rename(columns=RenameDict)
	## now RENT_KEY and others should work!
	rdata = rdata[RenameDict.values()]
	rdata['rent_zip'] = rdata['rent_zip'].astype(str).str.zfill(5)
	## going to do Additional Filtering here -- including down to NYC_ZIPS, which it should do by default
	if AdditionalFilters:
		if type(AdditionalFilters)==list:
			## assume this is a list of zip codes, as per our latest geom
			filter_col = 'rent_zip'
			rdata = rdata[rdata[filter_col].isin(AdditionalFilters)].copy()
		elif type(AdditionalFilters)==dict:
			filter_col = list(AdditionalFilters.keys())[0]
			filter_val = list(AdditionalFilters.values())[0]
			rdata = rdata[rdata[filter_col].isin(filter_vals)].copy()
		else:
			print(f"You have provided an unidentified type for AdditionalFilters: {type(AdditionalFilters)}\nPlease check again. Exiting."); sys.exit(1)
	# we can add county-to-borough-to-zip logic some other time if we need to
	sanity_check(rdata, name='RENT')
	return rdata

# def store_df(dataframe, outpath, OVERWRITE=False, DRIVER="GeoJSON", RemoveCols=False, PrettyPrint=False):
# 	'''Geopandas has a bad prettyprint - we'll be using json.'''
# 	if outpath==True: 
# 		outpath = utils.tempfile(prefix=f"store_df-")
# 	if RemoveCols!=False:
# 		outdf = dataframe.drop(columns=RemoveCols)
# 	else:
# 		outdf = dataframe
# 	if OVERWRITE!=True and not os.path.exists(outpath):
# 		if PrettyPrint==False:
# 			outdf.to_file(outpath, driver=DRIVER)
# 		elif PrettyPrint==True:
# 			## switch to json
# 			geojson_dict = json.loads(outdf.to_json())
# 			geojson_dict["crs"] = {"type": "name", "properties": {"name": "EPSG:4326"}} # preserving crs in json
# 			with open(outpath.replace('.geojson','.json'), "w") as f:
# 				json.dump(geojson_dict, f, indent=2)
# 		print(f"Wrote dataframe to location: {outpath}")
# 		return True
# 	print(f"Could not write dataframe to location: {outpath}\nPlease check if the location already exists.")

def remove_bad_rows(dataframe, column, bad_val=BAD_VAL, badfile=False):
	if badfile:
		bad_df = dataframe[dataframe[COMMUTE_KEY]==BAD_VAL]
		store_df(bad_df, outpath=badfile)
	good_df = dataframe[dataframe[COMMUTE_KEY]!=BAD_VAL]
	return good_df

def run_analysis():
	print(f"Beginning data load:\n\tGeom File:\t{ZCTA_GEOFILE}\n\tRent File:\t{RENT_FILE}\n")
	RENT_KEY = f"rent_{CHOSEN_BR_COUNT}BR"
	
	# load nta & rent
	geom_df = load_geoms(ZCTA_GEOFILE, RenameDict=GEOM_COLUMN_RENAMES, AdditionalFilters=ANALYSIS_ZIPS)
	rent_df = load_rent(RENT_FILE, RenameDict=RENT_COLUMN_RENAMES, AdditionalFilters=ANALYSIS_ZIPS)
	
	# merge
	geom_df = geom_df.merge(rent_df, left_on=JOIN_SETTINGS['left_on'], right_on=JOIN_SETTINGS['right_on'], how=JOIN_SETTINGS['how'])
	print("FINISHED MERGING"); sys.exit(1)
	
	## before we run any commute api's, we can run a quick estimate 
	_PERSISTED_PRECOUNTER = retry_logic.get_counter()
	number_of_upcoming_requests = estimate_upcoming_api_calls(geom_df)
	prompt_user_for_confirmation(number_of_upcoming_requests)
	print("FINISHED PROMPTING"); sys.exit(1)
	
	## apply google commute times & scores
	geom_df[COMMUTE_KEY] = geom_df.apply(retry_logic.call_api_with_limits, axis=1) ## this function ASSUMES lat & lon columns
	retry_logic.write_counter()
	print("Finished commute computations & API calls.\n")
	
	## API can return BAD_VAL, so we need to remove those dataframes
	geom_df = remove_bad_rows(geom_df, column=COMMUTE_KEY, bad_val=BAD_VAL, badfile=False)
	
	geom_df[SCORE_KEY] = geom_df[RENT_KEY] / (geom_df[COMMUTE_KEY]+1)
	geom_df[GRAVIKEY] = geom_df[RENT_KEY] / ((geom_df[COMMUTE_KEY])**2+1)
	utils.plot_heatmap(geom_df, column=CHOSEN_METRIC)
	
	utils.store_df(geom_df, MERGED_FILE, outfolder=False, OVERWRITE=False, RemoveCols=['centroid'], PrettyPrint=False)
	return 
