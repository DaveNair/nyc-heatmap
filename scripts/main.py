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
from config.settings import MERGED_FILE as OUTPUT_PATH

def main():
	if OUTPUT_PATH.exists():
		print("Cached file found. Plotting directly...")
		from lib.plot_utils import plot_heatmap
		plot_heatmap(OUTPUT_PATH)
	else:
		print("No cache found. Running full pipeline.")
		from scripts.NYCRentHeatmap import run_analysis
		run_analysis()
	print(f"Done! Hope you enjoyed!")

# --- Step 3: Entrypoint ---
if __name__ == "__main__":
    main()

