## Utils & Common functions
from datetime import datetime
import os
import geopandas as gpd
import pandas as pd 
import json

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

def store_df(dataframe, outpath, OVERWRITE=False, DRIVER="GeoJSON", RemoveCols=False, PrettyPrint=False):
	'''Geopandas has a bad prettyprint - we'll be using json.'''
	if outpath==True: 
		outpath = utils.tempfile(prefix=f"store_df-")
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

def log_error(message, filename='errors.log', timestamp=True):
	if timestamp==True:
		timestamp = f"{datetime.now()}:"
	with open(filename, 'a') as f:
		f.write(f"{timestamp} {message}\n")

def tempfile(prefix='tempfile-', suffix='.txt'):
	return f"{prefix}{datetime.now()}{suffix}"

## Plotting

def plot_heatmap(dataframe, column=CHOSEN_METRIC, legend=True, missing_kwds={'color':'lightgrey'}):
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


