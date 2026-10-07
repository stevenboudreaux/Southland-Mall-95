# Champs Sports: front and store (1995 map, store s49)

**Source (Oct 7, 2026).** The Southland facade record (from Steven's photos): "Champs Sports (from the photos): a smooth white portal with the navy badge outlined in red, cream serif capitals and SPORTS in its lower lobe; a royal-blue soffit with downlights; the blue WE KNOW GAME panel on a grey block plinth; a dark ceiling hung with rows of dome pendants, a slat-wood back wall of hung tops, a mannequin in a teal tee and white cap at the glass doors, and a wall of trainers on the right."

**Accuracy level:** 2 to 3 for the front (the record). The inside is a period type, built on the shared kits.

**Guessed:** the depth (24 m of the 28 m stall), the layout. The wall of trainers and the dark ceiling with dome pendants are not built yet (shoes are on hold).

**Frame.** A 12 m front facing south onto the hall at z = 48 (x −122 to −110), between The Limited and B. Dalton; the store runs 24 m north. Map tiles x 87–92, y 112–123.

## Front
- A smooth white portal with a navy badge outlined in red, carrying CHAMPS in cream serif capitals (DejaVu Serif Bold) and SPORTS under it. The badge's lobe shape is simplified to a box.
- A royal-blue soffit with downlights.
- A navy panel on a grey block plinth at the left, left blank: the record's slogan is the chain's.
- A mannequin in a teal tee at the doors.

## Inside (walkable)
- Grey carpet and white walls.
- Black slatwall of hung tops.
- Racks and tables, the cash wrap on the left, and fitting rooms at the back.

## Files
`tools/stores/small/wave7.gd` (the nine Wave 7 shops, materials `w7_*`), `paint7.py` → `tex/w7/`, `make_signs.py` (letters). Hooks in `tools/build_mall.gd` and `tools/open_interiors.py`.

## Sign pass (Oct 7, 2026)
See design/storefronts/photos/ for Steven's photos; built with tools/stores/signs/ (make_logos.py batch4, channel.gd sg_* materials).
Steven: the blue badge logo (photos 03, 04), on the polished-steel front of photos 01, 02. The badge: navy, bowed top, a lobe below with SPORTS in a red-lined oval, a red edge, CHAMPS in white-cream (Old Standard Bold, OFL, widened, the end letters taller), hung on three rods; steel piers, a steel header band and steel-framed windows either side of the open middle. Replaces the red/navy box sign. The inside is still apparel; Steven: it should look like a sports store (later, with the interiors).
