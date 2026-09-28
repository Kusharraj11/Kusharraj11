# Profile fonts

The generator uses a system monospace fallback by default. To embed a licensed font in generated SVGs, place a webfont at:

```text
profile/assets/fonts/profile-font.woff2
```

Then update `profile/assets/fonts/font-license.json` with the font family, source URL, license, and attribution. The generator embeds the font as a data URI only when that file exists; no font is bundled by default.
