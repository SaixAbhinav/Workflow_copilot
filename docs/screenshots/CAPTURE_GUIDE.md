# Screenshot & demo capture guide

The README embeds these images. Capture them while the app is running
(`python main.py` with Ollama running + a Google account added), then save the
PNGs in **this folder** with the exact filenames below. Delete this guide once the
images are in place, or keep it — it's harmless.

## Screenshots to capture (PNG)

| Filename | What to show |
|---|---|
| `main.png` | Main window with a finished result rendered — run **Summary** or **Tasks** on a sample doc so the output panel is full. This is the hero shot. |
| `task-review.png` | The Task review dialog (run **Tasks**, then click through to review) showing editable title / deadline / priority rows. |
| `history.png` | The run-history view with a few past runs listed. |
| `settings.png` | The Settings dialog (`Ctrl+,`). Optional — remove its row from the README if you skip it. |

Tips:
- Use a clean window size (not maximized on a 4K monitor — keeps text legible when scaled down).
- Avoid showing your real email address / personal data in the frame if you'd rather not.
- Pick a neutral sample input (there are samples in `ui/samples.py`).

## Demo GIF (`../demo.gif`)

Record a ~20–40s clip of **one full workflow**, e.g.:
1. Paste or drop a document.
2. Run **Tasks**.
3. Open the task review dialog, tweak a task.
4. Push to Google Calendar.

Convert the recording to a GIF and save it as `docs/demo.gif` (one level up from
this folder). Keep it under ~10 MB so it loads quickly on GitHub.

- Windows capture: Xbox Game Bar (`Win+G`) or [ScreenToGif](https://www.screentogif.com/) (records straight to GIF).
- For the **portfolio site**, host a higher-quality MP4 of the same recording — GIFs
  are lower quality than video.
