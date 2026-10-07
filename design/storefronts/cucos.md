# Cucos Border Cafe: front and restaurant (1995 map, store s42)

**Source (Oct 7, 2026).** The Southland facade record (from photographs; level 3): "a front of warm vertical wood planks with teal-green trim and a stepped parapet; the sign board with pale peach stripes behind the big red swash logo (traced from a photo of the sign, with its dark drop shadow) and MEXICAN CAFE beneath; heavy wood lintels over dark double doors; and a clay-tile awning on a green fascia over white-mullioned windows each side." The game's flat front (bar of bottles on the right, papel picado, arched doorways) for the inside.

**Accuracy level:** 3 for the front (the record), with the name in stand-in type (Fraunces, slanted), not the traced swash. The inside is a period type.

**Guessed:** the depth (16 m of the 32 m stall), the layout, the booths and tables, the dark wood tables with tile tops, the pendant lamps. The dark double doors stand open against the reveals so the room is walkable (open question: were they pinned open?).

**Frame.** A 14 m front facing north onto the Sears hall at z = -86 (x 22 to 36), built 16 m deep. Laid out from the viewer's left so the bar is on the right, as on the flat front. Map tiles x 159–165, y 57–64.

## Front
- Vertical wood planks over the whole front; a raised plank panel in the middle with teal edges, teal caps stepping down each side, a teal line at the head.
- **The sign (Oct 7, 2026, evening; Steven: "the most accurate neon Cucos Mexican Cafe sign"):** see "The neon sign" below. It replaces the sign board and the earlier outline trace.
- A heavy dark lintel over the doorway; dark double doors standing open inside.
- Each side: a white-mullioned window over a plank bulkhead with a teal sill; a clay barrel-tile awning (tile ends along the eave) over a green fascia board, on dark brackets.

## The neon sign
**Source.** Steven's five photos of the chain's street sign (Oct 7): a 1100 px close-up from below-left with the neon off, a square-on photo, two distant ones, and the wood-plank restaurant front.

**What the photos show.** An open-face neon channel sign:
- The script is sheet-metal cans with black returns, painted brick red inside. The big C runs into the swash and the S as one can; u, c and o are cans of their own.
- Glass tubes sit inside the cans on standoffs: three abreast where the stroke is wide, two in the middle weights, one in the hairlines and curls.
- Below, a periwinkle-blue cabinet with bullnose ends. Each end has two white stripes with a white tube that runs out along one and back along the other. MEXICAN CAFE is white letters, each with its own white tube.

**How it was traced.**
- The close-up was registered to the square-on photo (a homography found by aligning the two red masks), then levelled on the blue bar: `tools/stores/signs/src/cucos_front.jpg`.
- The letter openings were segmented from that view (`src/cucos_cans.png`); the three places where u, c, o and the S touch were cut by hand so each is its own can.
- `tools/stores/signs/make_cucos.py` turns the mask into outlines, back-pan triangles and tube runs: `cu_sign.json`.

**How it is built** (`tools/stores/signs/cucos_sign.gd`, materials `sg_cu2_*` in `channel.gd`). Geometry and vertex colour only, no textures.
- Cans: 125 mm deep returns, a 4 mm rim, red back pan and inner walls.
- Tubes: 8 mm glass, 42 mm off the fascia; a run 30 mm inside the walls, a centre run where the stroke is wide or too narrow for two. Each run ends in two electrodes in black boots; closed runs keep their gap. Standoffs every 21 cm.
- Light: the tubes glow a little (emission 1.9 at night, 1.4 by day); each lays a pool of light on the red pan; the cans throw a faint halo on the planks.
- Size: the script is 1.80 m wide and 1.04 m tall, the bar 2.32 m by 0.25 m, the whole sign 1.36 m tall on the 1.62 m parapet, centred over the doorway.
- About 20,000 triangles, plus 4,800 for the added light.

**Guessed or approximate.**
- The mall sign's size: scaled to fit the parapet. The street sign is roughly 3 m wide.
- MEXICAN CAFE is set in Old Standard Bold, thickened. The real letters are a heavier wedge-serif; no exact font was found.
- Tube runs follow the walls at a fixed inset. The real glass bender's runs differ in detail (where runs start, stop and cross).
- Whether the 1995 mall sign matched the street sign exactly is not known; the photos are of later street locations.

**Rebuild without a rebake.** The sign is a dynamic mesh, outside the lightmap:
`python3 tools/stores/signs/make_cucos.py`, then `godot --headless --path . --script res://tools/stores/signs/cucos_only.gd` rewrites `gen/w1/dyn_w8cf_sign.res` and `dyn_w8cf_sign_glow.res`. A full wing build calls the same code (`wave8.gd` `cucos_sign`). Then recapture Wing 1's stand-in, export and publish. Preview: `tools/qa/cucos_preview.gd`.

## Inside (walkable)
- Saltillo tile floor, warm adobe walls with a teal tile wainscot, dark beams under a dark wood ceiling.
- Booths down the left wall; tables with ladder-back chairs either side of the aisle; a hostess stand by the door.
- The bar down the right wall at the back: a back bar of bottles, a dark counter with a teal top, red stools.
- Two dark arched niches on the back wall either side of the kitchen door.
- Papel picado strung across the room; copper pendant lamps, warm.

## Files
`tools/stores/small/wave8.gd` (the seven Wave 8 shops, materials `w8_*`), `paint8.py` → `tex/w8/`, `make_signs.py` (letters). The sign: `tools/stores/signs/cucos_sign.gd`, `make_cucos.py`, `cu_sign.json`, `cucos_only.gd`. Hooks in `tools/build_mall.gd` and `tools/open_interiors.py`.
