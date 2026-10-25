# Godot mall: the outside (wing 3, "Outside") — Demo 44, Oct 24, 2026

**Asked for (Steven, Oct 23–24):** the exterior phase — the parking lot and the building as seen
from it, built from the Oct 23 site visit (the report's shared exterior table), with the Cucos
neon on the east entrance's outside fascia ("add the neon that you have on the inside entrance up
there").

## What it is
- A third game file, **wing 3**: the lot round the whole building, the building's shell with a
  skin per face, the entrances, the Horton tank, the palm drive, the outparcels and the
  neighbours. 1995 only for now (no 2026 outside yet; the year button is hidden there).
- **Getting out and in:** every exit door of the walkable mall offers "Go outside" when you stand
  at it (the same prompt as the wing seam: E / Enter, a gamepad's A, a tap): the main entrance
  (s39), the Sears hall's east entrance (s43), the cinema-side exit (s41) and the south entrance
  (s55). Outside, each door offers "Enter the mall · …" and loads the wing it belongs to. The
  "Jump to" menu has an "Outside" entry (the main entrance's walk).
- The doors and their spots are in `exterior.json` (`doors`), read by `scripts/player.gd` for
  every wing; `gen/w1` and `gen/w2` did not change, so the stand-in stamps stay valid.

## Frame and sources
- Metres, +x east, +z south (as the whole build). West Park Ave is the east road (the main
  entrance's palm drive), Bayou Gardens Blvd the south one, Armour Dr the north one. Sears is the
  north box, Dillard's the south-east one, JCPenney the west one.
- `tools/make_exterior.py` reads the 1995 map (`index.html` mall-data) and writes `exterior.json`:
  the building's outline as wall runs with the store behind each and the side it faces
  (`segments`), the footprint rectangles (`roofs`), the standalone block n2 west of the back lot
  (Steven, 4486 @112 s: the original 1969 standalone Sears, Unitech today), the doors, and the
  lot's walk grid (every map tile outside a building).
- `tools/exterior/exterior.gd` builds the scene from it; `tools/exterior/paint_exterior.py` paints
  the textures in `tex/ex/` (brick, block, stucco, the 6 m concrete lot panel with its tar joint,
  asphalt, mulch, grass, chain-link).
- Build: `godot --headless --path . --script res://tools/build_mall.gd -- --wing=3` →
  `wing3.tscn`, `gen/w3/`. Bake: `AUTOBAKE="wing3:fastday"` (day only, like the game). Export:
  presets "Wing 3 Desktop" / "Wing 3 Mobile" (`w3.desktop.pck` / `w3.mobile.pck`), `?wing=3`.

## The building (the report's table; heights are parapets)
| Face | Built as | 1995 confidence |
|---|---|---|
| Store backs north of the Concourse row (z = 20) | tan-brown brick 6.5 m, dark soldier course at 4.7 m, peach pilasters and downspouts every 8 m, beige service doors with wall packs, yellow bollards | good (unchanged) |
| Store backs south of the Concourse (z = 100), the restrooms, Wesley Austin, TGO | blank tan brick 5 m | good |
| Dillard's wing rear lane (z = 70) | back doors 3026–3029 on stoops | good |
| Woolworth block | red brick 9 m, compactor enclosure | good |
| Sears | white painted block 9 m; loading dock on the north wall (canopy on pipe columns, dock 1.2 m, yellow rail); "Sears" on three faces | dock good; walls a guess |
| Cinema box | salmon brick 9 m, peach pilasters, hooded exit doors, the ramp with its rail | good (original) |
| Cinema-wing exit (s41) | brown aggregate precast fascia, white soffit with cans, clear-anodized curtain wall, poster case on the buff return, the 3-loop bike rack | good (original) |
| East facade (x = 30 / 44, main entrance → Cucos) | cream pilasters every 4 m, tan recessed panels, white wainscot, cream stepped cornice | rhythm likely original; finishes a guess |
| K&B bay (s25) | the original folded-plate cream canopy with a can in each pleat, raked windows, tan bulkheads, cream band with the purple oval and "K&B" | canopy good; sign a guess |
| Cucos (s42) | the 2026 massing: 8 m pilaster rhythm, six tall windows in white surrounds, two glazed garage-style doors, stepped parapet at the sign bay; in Cucos's colours (warm stucco, teal band and box awnings, as its mall front), "Cucos Mexican Cafe" | massing good; colours a guess ("repainted") |
| East entrance (s43) | peach fascia, the **Cucos neon** 2.2× centred over the doors, dark-brown curved eyebrow canopy 8 m, bronze 2-tier storefront with 4 doors | Steven's decision; fan ornament era |
| Main entrance (s39) | **placeholder**: flat cream canopy on square columns, glass storefront, "SOUTHLAND MALL" | 1995 form unknown (today's porte-cochère is 2000s) |
| South entrance (s55) | 10 m pavilion, thin white cornice slab, cream pilasters banded dark at the base, doors in a porch, tie-rod canopy, the drop-off bulb with a live oak | mass and position original; skin a guess |
| JCPenney | cream speckled brick (long thin units), 7.5 m west / 9.5 m rear; west customer entrance under a flat maroon fascia, roll-up receiving door, podocarpus columns; south entrance under the red arcade on square columns; north Package Pick-up (coral fascia) and docks 1–2 under a red canopy; "JCPenney" west and south | brick good; signs are 2012-era shapes with the 1995 word |
| Dillard's | 3 storeys peach EIFS scored as ashlar, two cream cornice bands, "Dillard's" east and south; the cast-iron gallery on the east face (bronze columns, lace frieze and brackets, pebble paving, bollard lights), blind panelled doors under sunburst fanlights, flagpole island | gallery as filmed (Steven wants it); 1995 D.H. Holmes-era skin unknown |

## The lot
- Jointed exposed-aggregate concrete panels ~6 × 6 m (one texture per panel, tar joint on two
  edges) over the whole lot; white stall stripes (the 1995 striping under today's yellow) in
  double rows perpendicular to the buildings, row ends ~40 m apart; yellow-curbed pill islands at
  the row ends with live oaks or shrubs; white tapered lot poles ~11 m on square yellow pedestals
  with twin period shoebox heads (sodium light at night).
- The West Park entry drive: 2 lanes, double yellow centreline, 12 sabal palms a side in yellow-
  curbed mulch medians, crape-myrtle islands at the entrance, a signal at the road.
- Bayou Gardens frontage: a long mulched island with 19 sabal palms and 4 live oaks. The pine
  island with the hydrant at JCPenney's north-west; the lawn island with a magnolia and pines.
- The Horton tank (1970, CB&I): 11 m dia × 11 m, 4 ring courses, conical roof, caged ladder,
  riser, in a chain-link yard at x −124..−96, z −18..14 with the peach utility building and the
  conduit pole on its yellow base.
- The water tower (white pedestal, blue "NORTH TERREBONNE" seal) at (−300, −140), the skyline
  landmark; the camera's far plane is 600 m outside.
- Outparcels: the drive-thru bank west of the back lot with the lattice cell tower, the 1-storey
  strip centre along the south edge, Big Lots across the drive from the Sears side exit, Ground
  Pat'i at the SW corner with its 4-sided cube pole sign; the charcoal apartments behind a wood
  fence and the soccer fields behind a black picket fence to the west, St. Bernadette's cream
  building with the green roof beyond.
- Kerbs round the building; a sidewalk's width of panel between them and the walls.

## Known gaps / next
- Period photos: the main entrance, the south entrance and Dillard's are all re-skinned; the
  1995 forms are placeholders until Steven finds photos (the report's open question).
- Not filmed: Dillard's north dock, JCPenney's dock face, the Armour Dr edge (plain here).
- The 2026 outside (today's skins: EIFS, T-Mobile, Shoe Dept. Encore's exterior entrance, the
  LED poles, yellow stalls) is not built; wing 3 is 1995 only.
- Looking out through the mall's exit doors still shows the old 12 m vestibule stand-in, not the
  lot.
- Lot furniture is sparse (no ADA pads, hatched fire lanes, storm grates); the Dillard's lace is a
  dark band, not ironwork.
