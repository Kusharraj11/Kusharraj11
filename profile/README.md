# Self-generating profile

`profile/source/profile.md` is the editable source for the human-written profile. The root `README.md` is generated from that source and checked-in SVG assets.

## Generate locally

From the repository root:

```bash
python scripts/generate_profile.py
```

The generator uses only Python's standard library. It reads public GitHub data for `Kusharraj11` when `GITHUB_TOKEN` is available (the token is optional), and writes deterministic output to:

- `README.md`
- `profile/assets/generated/stats.svg`
- `profile/assets/generated/portrait.svg`

Set `GITHUB_USERNAME` to generate the same profile for another public account. Network failures or missing credentials use a checked-in, empty-data fallback rather than erasing the profile.

## Portrait pipeline

The future high-resolution portrait input path is `profile/assets/portrait/source/portrait.pgm` (portable graymap) or `portrait.ppm` (portable pixmap). The standard-library pipeline converts that source into animated ASCII SVG frames. Keep the source image out of git if it is personal; the generated placeholder remains usable until a photo is supplied. A JPG/PNG can be converted to PGM/PPM with any image editor before generation.

## Fonts and licensing

See `profile/assets/fonts/README.md`. A local `profile-font.woff2` is intentionally ignored by default and is embedded only when its license metadata is recorded in `font-license.json`.
