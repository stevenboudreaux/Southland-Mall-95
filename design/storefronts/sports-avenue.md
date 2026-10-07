# Sports Avenue: front and store (1995 map, store s8b)

**Source (Oct 7, 2026).** The Southland facade record (from Steven's photos): "Sports Avenue (from the photos): the whole front hangs off a gold goalpost: a red padded post at the door, a goose-neck curving up to the crossbar, uprights rising past the sign with red flags on top. Between the uprights a gold marquee, wider at the top, carries a field of white bulbs with SPORTS picked out in red, a star at each corner; under it AVENUE in separate gold capitals on a rail against blue. Behind the glass: jerseys pinned in a grid, forms in hoods and shorts, caps, a red table."

**Accuracy level:** 2 to 3 for the front (the record). The inside is a period type, built on the shared kits.

**Guessed:** the layout, the goose-neck (drawn as a straight gold pole).

**Frame.** A 6 m front facing south onto the hall at z = 48 (x −26 to −20), beside Gumballs; the store runs 12 m north. Map tiles x 135–137, y 118–123.

## Front
- The front hangs off a gold goalpost.
- A gold marquee of white bulbs with SPORTS in red bulbs and a star at each corner.
- AVENUE in gold capitals on a gold rail against royal blue.
- Gold uprights rising past the sign with red flags on top, a crossbar, and a red padded post at the door.
- Glass on a blue bulkhead.

## Inside (walkable)
- Grey carpet.
- Slatwall of jerseys and tops, a round rack, the cash wrap, and a fitting room.

## Files
`tools/stores/small/wave7.gd` (the nine Wave 7 shops, materials `w7_*`), `paint7.py` → `tex/w7/`, `make_signs.py` (letters). Hooks in `tools/build_mall.gd` and `tools/open_interiors.py`.

## Sign pass (Oct 7, 2026)
See design/storefronts/photos/ for Steven's photos; built with tools/stores/signs/ (make_logos.py batch4, channel.gd sg_* materials).
The marquee now in 3D: a deep gold box, a field of lit bulbs, SPORTS raised in red with white edges (Francois One, OFL), red rails, gold stars at the corners; AVENUE and the goalpost frame as before (photos/sports-avenue).
