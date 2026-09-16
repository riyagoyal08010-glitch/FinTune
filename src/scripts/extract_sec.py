from pathlib import Path
import zipfile

BASE_DIR = Path(__file__).resolve().parents[1]

ZIP_FILE = Path.home() / "Downloads" / "2025q2.zip"
OUTPUT_DIR = BASE_DIR / "data" / "raw" / "sec" / "2025q2"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print(f"ZIP file: {ZIP_FILE}")
print(f"Extracting to: {OUTPUT_DIR}")

if not ZIP_FILE.exists():
    raise FileNotFoundError(f"ZIP file not found: {ZIP_FILE}")

with zipfile.ZipFile(ZIP_FILE, "r") as zip_ref:
    zip_ref.extractall(OUTPUT_DIR)

print("Extraction complete.")

print("\nExtracted files:")
for file in OUTPUT_DIR.iterdir():
    print(f"  {file.name}")