A high-resolution procedural deep-sea / jellyfish animation driven by real marine wave data. It renders an atmospheric underwater scene (marine snow, bioluminescence, kelp shadows, hydrothermal vents) and a luminous jellyfish whose motion and morphology respond to wave parameters in a CSV file.

## Features
- Data‑driven animation using columns:
  - `wave_height (m)` – scales tentacle count, wave layers, particle density
  - `wave_direction (°)` – influences lateral drift / orientation offset
  - `wave_period (s)` – modulates background wave oscillation speeds
  - `ocean_current_velocity (m/s)` – affects sway amplitude & speed factors
- Smooth temporal interpolation between successive rows for fluid motion
- Layered deep-sea gradient with subtle multi-wave parallax
- Dense marine snow particle field (drifting via current)
- Pulsing bioluminescent points with multi‑color glow
- Kelp forest shadow silhouettes with procedural sway
- Hydrothermal vent systems: glowing bases + turbulent plumes
- Procedural jellyfish:
  - Concentric dotted bell with shimmer gradients & sparkles
  - Dynamic trunk and mirrored tentacles (S‑curve motion + afterimages)
  - Parameter‑sensitive counts, sizes, and sparkle probabilities
- Postprocessing blur (OpenCV Gaussian) for soft cinematic look

## Repository Contents
| File | Purpose |
|------|---------|
| `wave data.py` | Main visualization script (Pygame + OpenCV + NumPy) |
| `open-meteo-54.54N10.21E0m.csv` | Sample marine wave dataset (Open‑Meteo style) |
| `wave.mp4` | (Optional) Placeholder / potential output video (not auto‑generated yet) |

## Requirements
- Python 3.9+ (tested with CPython; 3.11+ also fine)
- Packages:
  - `pygame`
  - `opencv-python`
  - `numpy`

### Quick Install
```powershell
py -m pip install --upgrade pip
py -m pip install pygame opencv-python numpy
```

## Running the Visualization
From the project directory:
```powershell
py "wave data.py"
```
A Pygame window + OpenCV display window will appear. Press `Esc` (focus the OpenCV window) or close the window to exit.

## Data File Format
The loader expects a CSV with (at least) the following header names (or compatible lines after filtering):
```
 time,wave_height (m),wave_direction (°),wave_period (s),ocean_current_velocity (m/s)
```
Lines beginning with `latitude` or `time,` are skipped. All numeric columns are parsed as `float`.

If you replace the CSV:
1. Keep the same column names (or adjust `fieldnames` in `load_wave_data`).
2. Ensure consistent units.
3. Avoid blank trailing commas.

## Configuration
Edit the constants near the top of `wave data.py`:
```python
WIDTH, HEIGHT = 1920, 1920  # Output resolution (square)
FPS = 30                    # Frame rate target
CSV_FILE = 'open-meteo-54.54N10.21E0m.csv'
```
Recommended starting alternative for mid-range hardware:
```python
WIDTH, HEIGHT = 1280, 1280
```

## Performance Tuning
Because the default resolution (1920×1920) plus heavy particle counts can stress GPUs/CPUs, consider these adjustments:
| Area | Where in code | What to change |
|------|---------------|----------------|
| Resolution | Top constants | Reduce `WIDTH, HEIGHT` |
| Frame rate | Top constants | Lower `FPS` (e.g., 24) |
| Marine snow density | `add_deep_sea_details` | Lower base count: `for i in range(250 + int(wave_height * 80))` |
| Bioluminescent points | `add_deep_sea_details` | Change `for i in range(75)` |
| Light rays | `add_deep_sea_details` | Change `for i in range(15)` |
| Kelp fronds | `add_kelp_shadows` | Change `for i in range(20)` |
| Vents | `add_hydrothermal_vents` | Change `for vent_id in range(5)` |
| Tentacles | `draw_creature` | Adjust `n_tentacles = int(24 + wave_height * 90)` |
| Gaussian blur cost | Main loop | Remove or enlarge kernel (currently `cv2.GaussianBlur(..., (0,0), 2.5)`) |

Tip: Reduce the heaviest multiplicative loops first (marine snow, tentacles, vents) before lowering visual fidelity elsewhere.

## How Interpolation Works
`interp_steps = 60` inside the main loop creates 60 frames between raw records (smooth transitions). Set lower for faster time progression or higher for slower cinematic pacing.

## Adding Video Export (Optional)
Currently frames are only displayed. To save an MP4 (H.264 may require system codecs on Windows), you can add near the start of `main()`:
```python
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
writer = cv2.VideoWriter('wave.mp4', fourcc, FPS, (WIDTH, HEIGHT))
```
Then after creating `arr` each frame (before `cv2.imshow`):
```python
writer.write(arr)
```
And before quitting:
```python
writer.release()
```
If color channels look off, ensure the frame is BGR (the script already converts).

## Potential Enhancements (Roadmap Ideas)
- Keyboard controls: pause, speed up/down, toggle layers
- Headless render mode (no window, direct video export)
- CLI arguments (`argparse`) for width, height, CSV, duration
- Adaptive particle density based on frame time (dynamic performance scaling)
- Multi‑creature mode with variation seeds
- Save random seeds to reproduce identical animation sequences
- Color grading LUT / filmic tonemapping
- Option to output PNG sequence instead of video

## Troubleshooting
| Symptom | Possible Cause | Fix |
|---------|----------------|-----|
| Black or blank window | Window hidden behind others | Alt+Tab / bring to front |
| Very low FPS | High resolution & particle counts | Reduce WIDTH/HEIGHT & counts (see table) |
| `No module named pygame` | Dependencies missing | Install packages (see Requirements) |
| Video window freezes but Pygame runs | OpenCV waitKey timing | Ensure `cv2.waitKey(1000//FPS)` not 0; keep blur cost low |
| Wrong CSV parsing | Header mismatch | Adjust `fieldnames` or rename columns |
| Memory usage climbs | Writer not released after adding export | Call `writer.release()` |

## Extending the Data Mapping
Inside `draw_creature` & `add_deep_sea_details` you can:
- Map `wave_period` to sway amplitude or glow pulse speed
- Map `current_speed` to particle drift vector strength
- Clamp extreme values to avoid harsh jumps

## Code Architecture Overview
- Data ingestion: `load_wave_data()` collects structured dicts
- Frame loop: interpolates parameters & composes scene
- Scene layering order:
  1. Deep sea gradient + parallax waves
  2. Environmental particles / rays / kelp / vents
  3. Jellyfish (bell, trunk, tentacles)
  4. Text overlay (wave stats)
  5. Postprocess blur & display

## License
No license specified yet. Consider adding an OSI‑approved license (e.g., MIT) so others know usage permissions.

## Attribution / Data Source
Wave sample file appears derived from Open‑Meteo style output. If distributing externally, attribute: https://open-meteo.com/

## Disclaimer
Visualization is artistic and not intended for scientific accuracy of biological forms or exact ocean optics.

---
Enjoy exploring and customizing the deep sea! Feel free to request automated video export or performance simplification if needed.
