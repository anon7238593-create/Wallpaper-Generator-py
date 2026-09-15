# Wallpaper Generator (4K)

Algorithmic procedural 4K wallpaper generator in Python. Generates beautiful abstract wave landscapes rendered in 3840×2160 resolution.

## Features

- **Hourly GitHub Action**: Generates 1,000 new 4K wallpapers automatically every hour.
- **`artifacts` Branch**: All 1,000 wallpapers, manifest, and website are saved and tracked in the `artifacts` branch.
- **GitHub Pages Deployment**: Deploys a minimal, responsive website showcasing all 1,000 wallpapers with very little CSS and zero heavy frameworks.
- **`/random` Endpoint**: 
  - `https://<user>.github.io/Wallpaper-Generator-py/random` instantly redirects to a random wallpaper image.
  - `https://<user>.github.io/Wallpaper-Generator-py/random?view=1` opens an interactive viewer with a "🎲 Another Random" button.
- **Fast Multi-threading**: Parallel rendering generates 1,000 4K wallpapers in ~2–3 minutes.

## Installation

```bash
pip install Pillow
```

## Usage

### Generate a Single Wallpaper
```bash
python3 wallpaper-generator.py
```

### Generate 1,000 Wallpapers and Build Site
```bash
python3 wallpaper-generator.py --count 1000 --output-dir dist/wallpapers --site-dir dist --build-site
```

### CLI Options

| Argument | Description | Default |
| --- | --- | --- |
| `--count`, `-n` | Number of wallpapers to generate | `1` |
| `--output-dir`, `-o` | Output directory for PNGs | `./generated-wallpapers` |
| `--site-dir` | Directory for generated website | `./dist` |
| `--build-site` | Build minimal site (`index.html`, `/random`, `wallpapers.json`) | `False` |
| `--width` | Image width in pixels | `3840` |
| `--height` | Image height in pixels | `2160` |
| `--threads`, `-j` | Worker threads for parallel generation | Auto |
| `--compress` | PNG compression level (1-9) | `6` |
| `--show` | Open image after generation (single image mode) | `False` |

## GitHub Actions Workflows

1. **`Generate Wallpapers`** (`.github/workflows/generate-wallpapers.yml`):
   - Triggered on schedule (`0 * * * *` - every hour) and manual `workflow_dispatch`.
   - Generates 1,000 4K wallpapers and the minimal site.
   - Pushes the site snapshot cleanly to the `artifacts` branch.
2. **`Deploy GitHub Pages`** (`.github/workflows/deploy-pages.yml`):
   - Automatically triggered upon completion of `Generate Wallpapers` or on manual `workflow_dispatch`.
   - Deploys the static site from the `artifacts` branch to GitHub Pages.

## Setting up GitHub Pages

In the GitHub repository:
1. Go to **Settings** > **Pages**.
2. Under **Build and deployment** > **Source**, choose **GitHub Actions** (or select branch **artifacts** with folder `/ (root)`).

## Original Code & Credits

- Original Demo: [https://tanck.nl/wallpaper/](https://tanck.nl/wallpaper/)
- Original HTML/Javascript Code by [Roy Tanck](https://github.com/roytanck/wallpaper-generator)
