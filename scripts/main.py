## Entryfile for NYC Rent Heatmap
## by Dave Nair

from pathlib import Path
import sys

# --- Step 1: Startup logic (pathing, env vars) ---
ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from dotenv import load_dotenv
load_dotenv(dotenv_path=ROOT / ".env")

# --- Step 2: Main logic ---
from config.settings import MERGED_FILE, OUTPUTS_FOLDER, CHOSEN_METRIC

def main():
	if OUTPUTS_FOLDER:
		OUTPUT_PATH = ROOT / OUTPUTS_FOLDER / MERGED_FILE
	else:
		OUTPUT_PATH = ROOT / MERGED_FILE
	if OUTPUT_PATH.exists():
		print(f"Cached file found here: {OUTPUT_PATH}. Plotting directly...")
		from lib.utils import plot_heatmap
		plot_heatmap(OUTPUT_PATH, column=CHOSEN_METRIC)
	else:
		print(f"Searching: {OUTPUT_PATH}\nNo cache found. Running full pipeline.")
		from scripts.NYCRentHeatmap import run_analysis
		run_analysis()
	print(f"Done! Hope you enjoyed!")

# --- Step 3: Entrypoint ---
if __name__ == "__main__":
    main()

