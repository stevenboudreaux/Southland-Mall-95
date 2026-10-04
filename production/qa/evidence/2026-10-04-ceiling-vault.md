# Evidence: ribbed barrel-vault ceiling (2026-10-04)

Source of the design: the 2018 walkthrough video (report: "Southland Walkthrough Analysis"), frames 0:52 and 2:06.

- `2026-10-04-ceiling-vault-video-before-after.jpg`: video frame / game before / game after, west hall and the
  hall toward Sears. GPU path (the live first-person page), headless Chromium with software WebGL, 1280×720.
- `2026-10-04-ceiling-vault-phone-night.jpg`: 390×844 phone portrait, day and night themes.
- `2026-10-04-ceiling-vault-cpu-fallback.jpg`: the same four views drawn by the CPU fallback (WebGL off). Matches the GPU path.

What changed: every walk gets a shallow barrel vault springing just above the storefronts (a tan soffit band at
the spring), white ribs every 1.5 tiles that fade with distance, warm cream panels, an oval light between each pair
of ribs along the crown. Where two walks cross: a raised flat ceiling with a skylight grid.

Review: period-art-director, first pass SHIP WITH TWEAKS (wider and lower vault, ribs further apart, warmer,
lights broken into ovals, softer soffit); all four applied in this version.

Cost: CPU fallback draw time about 9 ms → 16 ms per frame in headless Chromium (auto-quality drops at 24 ms).
GPU path: no measurable change (software WebGL in testing; real devices use hardware).

Not checked: side and overhead views (the live page is 3D-only; those views don't draw a ceiling); real iPhone.
Not yet built (report items): distinct court ceilings (Shoe Dept. plaster vault with brass pendants, Dillard's
cove light, Sears clerestory), half-round arched hall ends, lit rings over the kiosks.
