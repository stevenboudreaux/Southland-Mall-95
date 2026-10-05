# Corn Dog 7 — facade and customer area (1995 map, store s54)

Sources (Oct 5, 2026): Steven's board photo `photos/corndog7/20261003212357aakc.jpg` (Dec 2025, from the left,
shows the sign, pier, counter, hood, menu TVs, floor); Google Maps user photos of the Houma shop (Aug 2024 wide
front, a tall shot from the left, a counter/floor close-up, a dining-room wall shot, food on tables); Yelp
photos (food, tabletops). The shop is unchanged since the 1990s, so 2024–25 photos stand for 1995. The sign's
lettering comes from the vector trace made from Steven's photo (index.html, `CD7` / `CD7O`).
Accuracy level: 3 (depth-accurate) — several angles; not yet 4 (Steven has not confirmed the build).

Frame: `u` runs along the frontage from the store's north end (the mall viewer's left) to its south end
(12 m in the layout: z = 68 → 80 at x = −138); `d` runs into the store (east); `y` up.

## Frontage (what you see from the hall)
- The unit is 12 m wide in the layout; the real front is ~9 m. The opening is u 1.5 → 10.5. Either side is
  the mall's wall (white glossy 8-inch tile in the 2024 photos; here the mall's own 1995 wall finish), with a
  fire-extinguisher cabinet at u ≈ 0.9, y 1.0–1.7 on the left.
- Piers: 0.30 m wide, 0.35 m deep returns, floor to the awning (y 0 → 2.75), navy glossy 4-inch (10 cm)
  square tiles with white grout, all faces. Navy ≈ #1b2466.
- Awning / sign box: a bullnose canopy in glossy taxi yellow (#f6dc2c, highlights to #fff27a), vacuum-formed
  panels with faint vertical seams every ~1.3 m. Cross-section: vertical front face from y 2.75 to ~3.5, then a
  quarter-round roll (radius ≈ 0.7) up and back to the wall at y ≈ 4.2; projection 1.1 m. The two ends are
  rounded in plan (radius ≈ 0.6) so the roll wraps round the corners. Bottom edge: a brushed aluminium trim
  strip (4 cm). Under the awning a white soffit with a recessed fluorescent strip.
- Navy pinstripe: 7 cm tall, 0.33 m above the awning's bottom edge, running the full length and round both
  ends. Lettering (navy, the traced vectors): "seasoned fries" script, cap height ≈ 0.30 m, sitting on the
  stripe at u ≈ 2.9–5.0; "CORN DOG 7" condensed brush caps, ≈ 0.48 m tall, above the stripe, centred at
  u ≈ 7.6 (its right end near u 9.6); "fresh lemonade" script, ≈ 0.22 m, below the stripe at the right end,
  starting at u ≈ 9.3 and wrapping onto the rounded end.
- Above the awning to the ceiling (y 4.2 → 4.6): vertical oak slats (tongue-and-groove, ~9 cm), medium oak.

## Inside — customer area (walkable), 11 m deep
- Ceiling 2.9 m: 2×4 ft lay-in acoustic tiles, white grid, 2×4 prismatic fluorescent troffers on a 2.4 m grid.
- Floor: wood-look ceramic tile in basketweave blocks (each 30 cm block = three 10×30 cm planks, blocks
  alternating direction), tan / caramel / brown mix, dark grout.
- Walls: yellow 10 cm tile wainscot to 1.5 m with a navy two-tile band at the top, white painted above
  (dining room, left and back). Behind the counter the kitchen is seen through the partition.
- Counter: front face at d 3.0 from u 4.8 to u 10.2 (runs to the right pier; a stainless condiment table on
  casters stands against it at u ≈ 9.4), with a 45° chamfer at its left end (u 4.8 → 5.3). Height 1.0 m,
  0.8 m deep. Front: navy 10 cm tile base (two courses), yellow tile field with 3×3 navy checker panels
  (checker = alternating navy/yellow 10 cm tiles, 30 × 30 cm, one panel per ~0.9 m), a navy course under the
  top. Top: brushed stainless with a 5 cm overhang. On it, from u 5.6 to 9.4: glass food cases 0.5 m tall,
  0.55 m deep, stainless frames, lit inside. Brushed stainless hood canopy over the back counter (u 6.0–8.6,
  d 3.6–4.4, y 2.0–2.6).
- Back-bar partition at d 4.5, u 4.8 → 10.5: oak-framed glass panels (y 1.1 → 2.4) over solid oak below,
  oak posts every 1.2 m; two TV menu boards (black bezel, yellow/white text on dark blue) at u 8.9 and 10.0,
  y 2.3–2.75, angled down; paper notices on the glass. The kitchen beyond is dim: stainless shelving,
  fryers' glow, a red-shirted crew.
- Dining room: u 1.5 → 4.5, d 3.5 → 11. Along the left wall three booths (oak ends and benches, dark red
  vinyl seats, laminate butcher-block tables), each 1.3 m long, from d 4.2. In the open floor two four-tops
  (butcher-block tops 0.75 m square on black pedestal bases, black metal chairs with oak slat backs).
- Partition between dining room and the queue: oak half-wall 1.1 m high with glass to 1.8 m, from d 3.5 to
  d 8 at u 4.5, with silk ficus plants on top.
- Queue area d 0 → 3 across the opening: open, two black stanchions optional (not in 1995 photos — omitted).

## Build notes
- Built by `tools/stores/corn_dog_7.gd`, called from `storefront()` for store s54; textures painted by
  `tools/stores/paint_corn_dog_7.py` into `tex/cd7/`.
- Walk grid: tiles x 79–80 × y 134–139 (queue) and x 81–84 × y 134–135 (dining) opened in layout_mall.json
  by `tools/open_interiors.py`; the counter, booths, tables and partitions are obstacles.
- Lights: the troffers (emissive + omni), case lights, soffit strip, menu TVs (emissive).
