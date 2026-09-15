# Wallpaper Generator (4K)

Algorithmic procedural 4K wallpaper generator in Python. Generates beautiful abstract wave landscapes rendered in 3840×2160 resolution.

## Features

- **Incremental Wallpaper Persistence**: Does not remove old wallpapers. Each run generates new wallpapers and appends them sequentially (`wallpaper-1.png`, `wallpaper-2.png`, etc.).
- **Unpadded File Names**: File names have no leading zeros, making them easy to download in simple loop scripts.
- **Count API**:
  - `https://<user>.github.io/Wallpaper-Generator-py/count/` returns only the number of wallpapers present (plain text).
  - `https://<user>.github.io/Wallpaper-Generator-py/count.txt` (plain text).
  - `https://<user>.github.io/Wallpaper-Generator-py/count.json` returns `{"count": 10000}`.
  - `https://<user>.github.io/Wallpaper-Generator-py/api/count` (plain text).
  - `https://<user>.github.io/Wallpaper-Generator-py/api/count.json` (JSON).
- **`/random` Endpoint**: 
  - `https://<user>.github.io/Wallpaper-Generator-py/random` instantly redirects to a random wallpaper image.
  - `https://<user>.github.io/Wallpaper-Generator-py/random?view=1` opens an interactive viewer with an "Another Random" button.
- **Automated Workflows**: Runs on every commit and hourly via GitHub Actions, automatically deploying the updated site to GitHub Pages.

## Downloading Wallpapers via Script

Because filenames have no leading zeros, you can download all available wallpapers with a simple bash script:

```bash
BASE_URL="https://anon7238593-create.github.io/Wallpaper-Generator-py"
COUNT=$(curl -s "${BASE_URL}/count/")

echo "Downloading $COUNT wallpapers..."
mkdir -p wallpapers
for i in $(seq 1 $COUNT); do
  curl -s -O "${BASE_URL}/wallpapers/wallpaper-${i}.png"
done
```

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Generate a Single Wallpaper
```bash
python3 wallpaper-generator.py
```

### Generate Wallpapers and Build Site
```bash
python3 wallpaper-generator.py --count 10000 --output-dir dist/wallpapers --site-dir dist --build-site
```

### CLI Options

| Argument | Description | Default |
| --- | --- | --- |
| `--count`, `-n` | Number of new wallpapers to generate | `1` |
| `--start-index` | Starting index (auto-detects highest + 1) | Auto |
| `--output-dir`, `-o` | Output directory for PNGs | `./generated-wallpapers` |
| `--site-dir` | Directory for generated website | `./dist` |
| `--build-site` | Build minimal site (`index.html`, `/random`, count APIs) | `False` |
| `--width` | Image width in pixels | `3840` |
| `--height` | Image height in pixels | `2160` |
| `--threads`, `-j` | Worker threads for parallel generation | Auto |
| `--compress` | PNG compression level (1-9) | `6` |
| `--show` | Open image after generation (single image mode) | `False` |

## GitHub Actions Workflows

- **`Generate Wallpapers and Deploy Pages`** (`.github/workflows/generate-wallpapers.yml`):
  - Triggered on every commit (`push`), on hourly schedule (`0 * * * *`), and on manual `workflow_dispatch`.
  - Checks out existing wallpapers from the `artifacts` branch, generates the new batch, updates count APIs and site files, and pushes incrementally.
  - Automatically deploys to GitHub Pages in the same workflow run.

## Original Code & Credits

- Original Demo: [https://tanck.nl/wallpaper/](https://tanck.nl/wallpaper/)
- Original HTML/Javascript Code by [Roy Tanck](https://github.com/roytanck/wallpaper-generator)
