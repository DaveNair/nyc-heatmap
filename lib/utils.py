## Utils & Common functions
from datetime import datetime
import os
import geopandas as gpd
import pandas as pd 
import json
from pathlib import Path

from config import plot_config
from config.settings import VERBOSE, VERBOSE_DETAILED


## I/O

def read_file(filename, filetype=None):
	if not filetype:
		filetype = os.path.splitext(filename)[1].lower().strip('.')
		# filetype = filename.split('.')[-1]
	elif filetypein ['shp', 'json', 'geojson', 'gpkg']:
		return gpd.read_file(filename)
	elif filetype in ['csv']:
		return pd.read_csv(filename)
	elif filetype in ['xlsx', 'xls']:
		return pd.read_excel(filename)
	elif filetype in ['parquet', 'pq']:
		return pd.read_parquet(filename)
	elif filetype in ['jsonl']:
		with open(filename, 'r', encoding='utf-8') as f:
			return [json.loads(line) for line in f]
	elif filetype in ['txt']:
		with open(filename, 'r', encoding='utf-8') as f:
			return f.read()
	else:
		raise ValueError(f"Unsupported file type: \t{filetype}.\nPlease check file: \t{filename}")

def store_df(dataframe, outpath, outfolder=False, OVERWRITE=False, DRIVER="GeoJSON", RemoveCols=False, PrettyPrint=False):
	'''Geopandas has a bad prettyprint - we'll be using json.'''
	if outpath==True: 
		outpath = utils.tempfile(prefix=f"store_df-")
	## apply optional folder
	if outfolder:
		outpath = Path(outfolder) / Path(outpath).name
	else:
		outpath = Path(outpath)
	if RemoveCols!=False:
		outdf = dataframe.drop(columns=RemoveCols)
	else:
		outdf = dataframe
	if not OVERWRITE and os.path.exists(outpath):
		## quit here, OVERWRITE=False & outpath exists
		print(f"Could not write dataframe to location: {outpath}\nPlease check if location already exists.")
		return

	## ensure outfolder exists
	outpath.parent.mkdir(parents=True, exist_ok=True)

	if not PrettyPrint:
		outdf.to_file(outpath, driver=DRIVER)
	else:
		## PrettyPrint JSON logic
		geojson_dict = json.loads(outdf.to_json())
		geojson_dict["crs"] = {
			"type": "name", 
			"properties": {"name": "EPSG:4326"}} # preserving crs in json
		with open(outpath.with_suffix('.json'), "w") as f:
			json.dump(geojson_dict, f, indent=2)
	print(f"Wrote dataframe to location: {outpath}\n")

def log_error(message, filename='errors.log', timestamp=True):
	if timestamp==True:
		timestamp = f"{datetime.now()}:"
	with open(filename, 'a') as f:
		f.write(f"{timestamp} {message}\n")

def tempfile(prefix='tempfile-', suffix='.txt'):
	return f"{prefix}{datetime.now()}{suffix}"

#### I/O Convenience

def check(dataframe, name='', N=5):
	if VERBOSE:
		print(name)
		print(dataframe.head(N))
		return True
	return False

def sanity_check(dataframe, name=''):
	if VERBOSE_DETAILED:
		print(name)
		print(dataframe.head())
		return True
	return False

## Plotting

def plot_heatmap(dataframe, column, legend=True, missing_kwds={'color':'lightgrey'}):
	if type(dataframe)==str:
		dataframe = read_file(dataframe)
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


