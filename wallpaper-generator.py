"""
Wallpaper Generator. See original HTML/Javascript version by roytanck (Roy Tanck)
https://github.com/roytanck/wallpaper-generator 
"""

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
import math
import os
from PIL import Image, ImageDraw
import random
import shutil
import sys
import time

def generateValues(width, verbose=False):
    # line segments (either few, or fluent lines (200))
    segments = 1 + math.floor(9 * random.random()) if random.random() < 0.5 else 200
    # wavelength
    wl = width / (5 + (15 * random.random()))

    # other random values
    random_vals_dict = {
        'segments': segments,
        'wl': wl,
        'layers': 3 + math.floor(10 * random.random()),
        'hueStart': 360 * random.random(),
        'hueIncrement': 20 - (40 * random.random()),
        'ampl': (0.1 * wl) + (0.9 * wl) * random.random(),
        'offset': width * random.random(),
        'offsetIncrement': width / 20 + (width / 10) * random.random(),
        'sat': 15 + (35 * random.random()),
        'light': 15 + (45 * random.random()),
        'lightIncrement': (2 + (4 * random.random())) if random.random() < 0.5 else -(2 + (4 * random.random()))
    }
    
    if verbose:
        print(random_vals_dict)
    return random_vals_dict

def hsl_to_rgb(h, s, l):
    # Convert HSL to RGB
    # Code borrowed from https://www.programcreek.com/python/example/94482/colorsys.hsv_to_rgb
    h /= 360
    s /= 100
    l /= 100
    c = (1 - abs(2*l - 1)) * s
    x = c * (1 - abs((h*6) % 2 - 1))
    m = l - c/2
    c += m
    x += m
    if h < 1/6: return (c, x, m)
    elif h < 1/3: return (x, c, m)
    elif h < 1/2: return (m, c, x)
    elif h < 2/3: return (m, x, c)
    else: return (x, m, c)

def render_wallpaper(width=3840, height=2160, verbose=False):
    """Renders a single wallpaper in memory and returns a PIL Image."""
    values = generateValues(width, verbose=verbose)
    segments = values['segments']
    layers = values['layers']
    hueStart = values['hueStart']
    hueIncrement = values['hueIncrement']
    wl = values['wl']
    ampl = values['ampl']
    offset = values['offset']
    offsetIncrement = values['offsetIncrement']
    sat = values['sat']
    light = values['light']
    lightIncrement = values['lightIncrement']

    image = Image.new('RGB', (width, height))
    draw_ctx = ImageDraw.Draw(image)

    # background
    r, g, b = [int(x * 255) for x in hsl_to_rgb(hueStart, sat, light)]
    draw_ctx.rectangle([(0, 0), (width, height)], fill=(r, g, b))

    # draw the layers
    for l in range(layers):
        h = hueStart + ((l+1) * hueIncrement)
        s = sat
        v = light + ((l+1) * lightIncrement)
        r, g, b = [int(x * 255) for x in hsl_to_rgb(h, s, v)]
        layerOffset = offset + (offsetIncrement * l)
        offsetY = ((l+0.5) * (height / layers))
        startY = offsetY + (ampl * math.sin(layerOffset / wl))
        coords = [(0, startY)]
        for i in range(segments+1):
            x = i * (width / segments)
            coords.append((x, startY + (ampl * math.sin((layerOffset + x) / wl))))
        coords.append((width, height))
        coords.append((0, height))
        coords.append((0, startY))
        draw_ctx.polygon(coords, fill=(r, g, b))

    return image

def generate_filename(base_dir, base_name):
    """Returns a filename of the form 'name-{n}' and uses the next available highest number."""
    os.makedirs(base_dir, exist_ok=True)
    files = os.listdir(base_dir)

    highest_num = 0
    for file in files:
        if file.startswith(base_name) and file.endswith('.png'):
            try:
                num = int(file[len(base_name):-4])
                highest_num = max(highest_num, num)
            except ValueError:
                pass

    return os.path.join(base_dir, f"{base_name}{highest_num + 1}.png")

def draw():
    """Backwards-compatible draw function for single wallpaper generation."""
    image = render_wallpaper(3840, 2160, verbose=True)
    try:
        image.show()
    except Exception:
        pass
    next_filename = generate_filename('./generated-wallpapers', 'generated-')
    image.save(next_filename, 'PNG')
    print(f"Saved: {next_filename}")
    return next_filename

def _save_one(index, out_dir, width, height, compress_level, prefix, pad_len):
    filename = f"{prefix}{index:0{pad_len}d}.png"
    filepath = os.path.join(out_dir, filename)
    img = render_wallpaper(width, height)
    img.save(filepath, 'PNG', optimize=False, compress_level=compress_level)
    return filename

def generate_batch(count=10000, output_dir="./generated-wallpapers", width=3840, height=2160,
                   compress_level=6, max_workers=None, prefix="wallpaper-"):
    """Generates count wallpapers in parallel using ThreadPoolExecutor."""
    os.makedirs(output_dir, exist_ok=True)
    if max_workers is None:
        cpu_count = os.cpu_count() or 4
        max_workers = min(32, max(4, cpu_count * 2))

    pad_len = max(4, len(str(count)))
    print(f"Generating {count:,} wallpapers ({width}x{height}) in '{output_dir}' with {max_workers} worker threads...")
    start_time = time.time()
    
    filenames = []
    step = max(50, count // 20)  # log progress approximately every 5%
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(_save_one, i, output_dir, width, height, compress_level, prefix, pad_len)
            for i in range(1, count + 1)
        ]
        completed = 0
        for f in futures:
            fname = f.result()
            filenames.append(fname)
            completed += 1
            if completed % step == 0 or completed == count:
                elapsed = time.time() - start_time
                rate = completed / elapsed if elapsed > 0 else 0
                print(f"  Progress: {completed:,}/{count:,} ({completed/count*100:.1f}%) in {elapsed:.1f}s ({rate:.1f} img/s)")

    filenames.sort()
    total_time = time.time() - start_time
    print(f"Successfully generated {count:,} wallpapers in {total_time:.2f}s.")
    return filenames

def build_site(site_dir, count, wallpaper_dir_rel="wallpapers", filenames=None):
    """
    Builds minimal static website with:
    - index.html: Minimal gallery showing all wallpapers
    - random/index.html: /random endpoint giving a random wallpaper
    - wallpapers.json: Manifest of all wallpapers
    - .nojekyll: Prevent GitHub Pages from ignoring special files
    - favicon.png: Copied if available in workspace
    """
    os.makedirs(site_dir, exist_ok=True)
    os.makedirs(os.path.join(site_dir, "random"), exist_ok=True)

    pad_len = max(4, len(str(count)))
    first_wp_filename = f"wallpaper-{'0' * (pad_len - 1)}1.png"
    if filenames is None:
        filenames = [f"wallpaper-{i:0{pad_len}d}.png" for i in range(1, count + 1)]

    # 1. Manifest wallpapers.json
    now_iso = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    manifest = {
        "count": len(filenames),
        "updated_at": now_iso,
        "resolution": "3840x2160",
        "wallpapers": [f"{wallpaper_dir_rel}/{fn}" for fn in filenames]
    }
    with open(os.path.join(site_dir, "wallpapers.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    # 2. .nojekyll
    with open(os.path.join(site_dir, ".nojekyll"), "w", encoding="utf-8") as f:
        f.write("")

    # 3. Copy favicon if exists
    favicon_src = "favicon.png"
    if os.path.isfile(favicon_src):
        shutil.copy2(favicon_src, os.path.join(site_dir, "favicon.png"))

    # 4. Minimal index.html
    index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Wallpaper Generator (4K)</title>
  <link rel="icon" href="favicon.png" type="image/png">
  <style>
    :root {{
      --bg: #0f1015;
      --card-bg: #181920;
      --card-hover: #21222c;
      --border: #2b2c37;
      --text: #f3f4f6;
      --text-muted: #9ca3af;
      --accent: #6366f1;
      --accent-hover: #4f46e5;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.5;
      padding: 1.5rem;
    }}
    header {{
      max-width: 1440px;
      margin: 0 auto 1.5rem;
      padding-bottom: 1.5rem;
      border-bottom: 1px solid var(--border);
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: center;
      gap: 1rem;
    }}
    .title-group h1 {{
      font-size: 1.6rem;
      font-weight: 700;
      letter-spacing: -0.02em;
    }}
    .title-group p {{
      color: var(--text-muted);
      font-size: 0.88rem;
      margin-top: 0.25rem;
    }}
    .actions {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 0.6rem;
    }}
    .btn {{
      background: var(--card-bg);
      color: var(--text);
      border: 1px solid var(--border);
      padding: 0.45rem 0.85rem;
      border-radius: 6px;
      font-size: 0.85rem;
      font-weight: 500;
      text-decoration: none;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
      transition: background 0.15s, border-color 0.15s;
    }}
    .btn:hover {{ background: var(--card-hover); border-color: #3f4152; }}
    .btn.primary {{ background: var(--accent); border-color: var(--accent); color: #fff; }}
    .btn.primary:hover {{ background: var(--accent-hover); }}
    .btn:disabled {{ opacity: 0.4; cursor: not-allowed; }}
    .search-box {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      color: var(--text);
      padding: 0.45rem 0.75rem;
      border-radius: 6px;
      font-size: 0.85rem;
      width: 150px;
    }}
    .search-box:focus {{ outline: none; border-color: var(--accent); }}
    .toolbar {{
      max-width: 1440px;
      margin: 0 auto 1.25rem;
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: center;
      gap: 0.75rem;
      font-size: 0.88rem;
      color: var(--text-muted);
    }}
    .toolbar-group {{
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }}
    .grid {{
      max-width: 1440px;
      margin: 0 auto;
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      gap: 1.25rem;
    }}
    .card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 8px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      transition: transform 0.15s, border-color 0.15s;
    }}
    .card:hover {{ transform: translateY(-2px); border-color: #434557; }}
    .card.highlight {{
      border-color: var(--accent);
      box-shadow: 0 0 0 2px var(--accent);
    }}
    .img-wrap {{
      position: relative;
      width: 100%;
      aspect-ratio: 16 / 9;
      background: #141419;
      overflow: hidden;
    }}
    .img-wrap img {{
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
    }}
    .card-footer {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0.55rem 0.75rem;
      font-size: 0.8rem;
    }}
    .card-id {{
      color: var(--text-muted);
      font-family: monospace;
      font-weight: 600;
    }}
    .card-links {{ display: flex; gap: 0.5rem; }}
    .card-links a {{
      color: var(--accent);
      text-decoration: none;
      font-size: 0.75rem;
      font-weight: 500;
      padding: 0.2rem 0.4rem;
      border-radius: 4px;
    }}
    .card-links a:hover {{ background: rgba(99, 102, 241, 0.15); }}
    .pagination {{
      max-width: 1440px;
      margin: 2rem auto;
      display: flex;
      flex-wrap: wrap;
      justify-content: center;
      align-items: center;
      gap: 0.5rem;
    }}
    .page-info {{
      color: var(--text-muted);
      font-size: 0.88rem;
      padding: 0 0.5rem;
    }}
    footer {{
      max-width: 1440px;
      margin: 3rem auto 1rem;
      text-align: center;
      color: var(--text-muted);
      font-size: 0.82rem;
      border-top: 1px solid var(--border);
      padding-top: 1.5rem;
    }}
    footer a {{ color: var(--text-muted); }}
    footer a:hover {{ color: var(--text); }}
  </style>
</head>
<body>
  <header>
    <div class="title-group">
      <h1>Wallpaper Generator</h1>
      <p>{count:,} algorithmic 4K wallpapers (3840×2160) • Generated hourly via GitHub Actions</p>
    </div>
    <div class="actions">
      <a href="random/" class="btn primary" title="Gives a direct random wallpaper">🎲 /random</a>
      <a href="random/?view=1" class="btn" title="View random wallpaper interactively">🖼️ Random Viewer</a>
      <a href="wallpapers.json" class="btn" target="_blank">📋 API JSON</a>
      <input type="number" id="jump-input" class="search-box" min="1" max="{count}" placeholder="Go to # (1-{count})...">
    </div>
  </header>

  <div class="toolbar">
    <div class="toolbar-group">
      <span id="counter-text">Showing wallpapers</span>
    </div>
    <div class="toolbar-group">
      <span>Per page:</span>
      <button class="btn per-page-btn" data-size="60">60</button>
      <button class="btn per-page-btn" data-size="120">120</button>
      <button class="btn per-page-btn" data-size="240">240</button>
      <button class="btn per-page-btn" data-size="all">All ({count:,})</button>
    </div>
  </div>

  <main class="grid" id="wallpaper-grid"></main>

  <nav class="pagination" id="pagination-controls">
    <button class="btn" id="prev-btn">◀ Previous</button>
    <span class="page-info" id="page-indicator">Page 1</span>
    <button class="btn" id="next-btn">Next ▶</button>
  </nav>

  <footer>
    <p>Generated automatically by GitHub Actions. Wallpapers saved in the <code>artifacts</code> branch.</p>
    <p style="margin-top:0.4rem;">Based on procedural wave algorithm by <a href="https://github.com/roytanck/wallpaper-generator" target="_blank" rel="noopener">Roy Tanck</a>.</p>
  </footer>

  <script>
    const TOTAL_WALLPAPERS = {count};
    const PAD_LEN = {pad_len};
    const WP_DIR = "{wallpaper_dir_rel}";
    let pageSize = 60;
    let currentPage = 1;
    let showAll = false;

    const grid = document.getElementById('wallpaper-grid');
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    const pageIndicator = document.getElementById('page-indicator');
    const counterText = document.getElementById('counter-text');
    const jumpInput = document.getElementById('jump-input');
    const paginationControls = document.getElementById('pagination-controls');

    function totalPages() {{
      return showAll ? 1 : Math.ceil(TOTAL_WALLPAPERS / pageSize);
    }}

    function renderWallpapers() {{
      grid.innerHTML = '';
      const startIdx = showAll ? 1 : ((currentPage - 1) * pageSize) + 1;
      const endIdx = showAll ? TOTAL_WALLPAPERS : Math.min(currentPage * pageSize, TOTAL_WALLPAPERS);

      counterText.textContent = `Showing #${{startIdx}} - #${{endIdx}} of ${{TOTAL_WALLPAPERS.toLocaleString()}}`;

      const fragment = document.createDocumentFragment();
      for (let i = startIdx; i <= endIdx; i++) {{
        const pad = String(i).padStart(PAD_LEN, '0');
        const filename = `wallpaper-${{pad}}.png`;
        const path = `${{WP_DIR}}/${{filename}}`;

        const card = document.createElement('div');
        card.className = 'card';
        card.id = `wp-${{i}}`;

        card.innerHTML = `
          <div class="img-wrap">
            <a href="${{path}}" target="_blank" rel="noopener">
              <img src="${{path}}" alt="Wallpaper #${{pad}}" loading="lazy" width="3840" height="2160">
            </a>
          </div>
          <div class="card-footer">
            <span class="card-id">#${{pad}}</span>
            <div class="card-links">
              <a href="${{path}}" target="_blank" rel="noopener">View 4K</a>
              <a href="${{path}}" download="${{filename}}">Download</a>
            </div>
          </div>
        `;
        fragment.appendChild(card);
      }}
      grid.appendChild(fragment);

      if (showAll) {{
        paginationControls.style.display = 'none';
      }} else {{
        paginationControls.style.display = 'flex';
        const pages = totalPages();
        pageIndicator.textContent = `Page ${{currentPage}} of ${{pages}}`;
        prevBtn.disabled = currentPage <= 1;
        nextBtn.disabled = currentPage >= pages;
      }}
    }}

    prevBtn.addEventListener('click', () => {{
      if (currentPage > 1) {{
        currentPage--;
        renderWallpapers();
        window.scrollTo({{ top: 0, behavior: 'smooth' }});
      }}
    }});

    nextBtn.addEventListener('click', () => {{
      if (currentPage < totalPages()) {{
        currentPage++;
        renderWallpapers();
        window.scrollTo({{ top: 0, behavior: 'smooth' }});
      }}
    }});

    document.querySelectorAll('.per-page-btn').forEach(btn => {{
      btn.addEventListener('click', () => {{
        const size = btn.getAttribute('data-size');
        if (size === 'all') {{
          showAll = true;
        }} else {{
          showAll = false;
          pageSize = parseInt(size, 10);
          currentPage = 1;
        }}
        renderWallpapers();
      }});
    }});

    jumpInput.addEventListener('keydown', (e) => {{
      if (e.key === 'Enter') {{
        const num = parseInt(jumpInput.value, 10);
        if (num >= 1 && num <= TOTAL_WALLPAPERS) {{
          if (showAll) {{
            const el = document.getElementById(`wp-${{num}}`);
            if (el) {{
              el.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
              el.classList.add('highlight');
              setTimeout(() => el.classList.remove('highlight'), 2000);
            }}
          }} else {{
            currentPage = Math.ceil(num / pageSize);
            renderWallpapers();
            setTimeout(() => {{
              const el = document.getElementById(`wp-${{num}}`);
              if (el) {{
                el.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                el.classList.add('highlight');
                setTimeout(() => el.classList.remove('highlight'), 2000);
              }}
            }}, 50);
          }}
        }}
      }}
    }});

    renderWallpapers();
  </script>
  <noscript>
    <div style="max-width:1440px; margin:2rem auto; padding:1rem; background:#181920; border:1px solid #2b2c37; border-radius:8px;">
      <p>JavaScript is disabled. Explore wallpapers directly:</p>
      <ul style="margin:1rem 0 0 1.5rem;">
        <li><a href="random/" style="color:#6366f1;">Get a Random Wallpaper (/random)</a></li>
        <li><a href="wallpapers.json" style="color:#6366f1;">View wallpapers.json manifest</a></li>
        <li><a href="{wallpaper_dir_rel}/{first_wp_filename}" style="color:#6366f1;">View Wallpaper #{'0' * (pad_len - 1)}1</a></li>
      </ul>
    </div>
  </noscript>
</body>
</html>
"""

    with open(os.path.join(site_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_html.strip() + "\n")

    # 5. Minimal /random endpoint (random/index.html)
    random_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Random Wallpaper</title>
  <link rel="icon" href="../favicon.png" type="image/png">
  <script>
    (function() {{
      const TOTAL_WALLPAPERS = {count};
      const PAD_LEN = {pad_len};
      const params = new URLSearchParams(window.location.search);
      const isViewMode = params.has('view');
      const idx = Math.floor(Math.random() * TOTAL_WALLPAPERS) + 1;
      const pad = String(idx).padStart(PAD_LEN, '0');
      const filename = `wallpaper-${{pad}}.png`;
      const url = `../{wallpaper_dir_rel}/${{filename}}`;

      if (!isViewMode) {{
        // Direct endpoint behavior: immediately redirect to random wallpaper image
        window.location.replace(url);
      }} else {{
        // Save details for viewer mode
        window.__randomWallpaper = {{ idx, pad, filename, url }};
      }}
    }})();
  </script>
  <noscript>
    <meta http-equiv="refresh" content="0; url=../{wallpaper_dir_rel}/{first_wp_filename}">
  </noscript>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: #0f1015;
      color: #f3f4f6;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }}
    header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0.75rem 1.5rem;
      background: rgba(15, 16, 21, 0.9);
      backdrop-filter: blur(8px);
      border-bottom: 1px solid #2b2c37;
      position: sticky;
      top: 0;
      z-index: 10;
    }}
    .brand {{
      color: #9ca3af;
      text-decoration: none;
      font-size: 0.9rem;
      font-weight: 500;
    }}
    .brand:hover {{ color: #fff; }}
    .title {{ font-weight: 600; font-size: 0.95rem; font-family: monospace; }}
    .nav-btns {{ display: flex; gap: 0.5rem; }}
    a.btn, button.btn {{
      background: #181920;
      color: #f3f4f6;
      border: 1px solid #2b2c37;
      padding: 0.45rem 0.85rem;
      border-radius: 6px;
      font-size: 0.85rem;
      cursor: pointer;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
      transition: background 0.15s;
    }}
    a.btn:hover, button.btn:hover {{ background: #22232c; border-color: #3f4152; }}
    .btn.primary {{ background: #6366f1; border-color: #6366f1; color: #fff; }}
    .btn.primary:hover {{ background: #4f46e5; }}
    main {{
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 1rem;
    }}
    main img {{
      max-width: 100%;
      max-height: calc(100vh - 5.5rem);
      border-radius: 8px;
      box-shadow: 0 10px 40px rgba(0, 0, 0, 0.6);
      object-fit: contain;
    }}
  </style>
</head>
<body>
  <header>
    <a href="../" class="brand">← Back to Gallery</a>
    <div class="title" id="wp-title">Random Wallpaper</div>
    <div class="nav-btns">
      <button class="btn" onclick="location.reload()">🎲 Another Random</button>
      <a id="download-btn" class="btn primary" download>⬇ Download 4K</a>
    </div>
  </header>
  <main>
    <img id="wallpaper-img" alt="Random 4K Wallpaper">
  </main>
  <script>
    if (window.__randomWallpaper) {{
      const {{ idx, pad, filename, url }} = window.__randomWallpaper;
      document.getElementById('wallpaper-img').src = url;
      document.getElementById('wallpaper-img').alt = filename;
      document.getElementById('wp-title').textContent = `Wallpaper #${{pad}}`;
      const dl = document.getElementById('download-btn');
      dl.href = url;
      dl.setAttribute('download', filename);
    }}
  </script>
</body>
</html>
"""

    with open(os.path.join(site_dir, "random", "index.html"), "w", encoding="utf-8") as f:
        f.write(random_html.strip() + "\n")

    print(f"Site built successfully in '{site_dir}' (index.html, random/index.html, wallpapers.json).")

def main():
    parser = argparse.ArgumentParser(description="Procedural 4K Wallpaper Generator")
    parser.add_argument("--count", "-n", type=int, default=1, help="Number of wallpapers to generate (default: 1)")
    parser.add_argument("--output-dir", "-o", type=str, default="./generated-wallpapers", help="Output directory for wallpaper PNGs")
    parser.add_argument("--site-dir", type=str, default=None, help="Output directory for site files (default: output-dir or ./dist)")
    parser.add_argument("--build-site", action="store_true", help="Generate website (index.html, random/index.html, manifest)")
    parser.add_argument("--width", type=int, default=3840, help="Image width (default: 3840)")
    parser.add_argument("--height", type=int, default=2160, help="Image height (default: 2160)")
    parser.add_argument("--threads", "-j", type=int, default=None, help="Worker threads for parallel generation")
    parser.add_argument("--compress", type=int, default=6, help="PNG compression level 1-9 (default: 6)")
    parser.add_argument("--show", action="store_true", help="Open generated wallpaper with default viewer (only if count=1)")
    parser.add_argument("--prefix", type=str, default="wallpaper-", help="Prefix for filename (default: 'wallpaper-')")
    args = parser.parse_args()

    # Backwards compatibility: if run with default arguments without flags
    if len(sys.argv) == 1:
        draw()
        return

    site_dir = args.site_dir or (os.path.dirname(args.output_dir) if args.output_dir.endswith("/wallpapers") else "./dist")

    if args.count == 1 and not args.build_site:
        img = render_wallpaper(args.width, args.height, verbose=True)
        filename = generate_filename(args.output_dir, 'generated-')
        img.save(filename, 'PNG', compress_level=args.compress)
        print(f"Saved: {filename}")
        if args.show:
            try:
                img.show()
            except Exception:
                pass
        return

    # Batch generation
    filenames = generate_batch(
        count=args.count,
        output_dir=args.output_dir,
        width=args.width,
        height=args.height,
        compress_level=args.compress,
        max_workers=args.threads,
        prefix=args.prefix
    )

    if args.build_site:
        # Calculate relative path from site_dir to output_dir
        rel_wp_dir = os.path.relpath(args.output_dir, site_dir)
        build_site(site_dir, args.count, wallpaper_dir_rel=rel_wp_dir, filenames=filenames)

if __name__ == "__main__":
    main()
