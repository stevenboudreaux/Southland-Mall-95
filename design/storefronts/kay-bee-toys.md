# Kay-Bee Toys: front and store (1995 map, store s18)

**Sources (Oct 6, 2026).** Both chosen by Steven:
- **The front:** his photo of the Kay-Bee Toys front, given as "the facade and signage aesthetic of the Southland Mall location".
- **The inside:** a home video, "KB Toys Green Friday Columbus Ga. 1993" (YouTube, channel UnofficialKBToys, `7gypthCcooY`), shot by a store associate in a Kay-Bee in Columbus, Georgia, before and after opening. Steven: "the youtube video perfectly captures the interior of the store".

**Accuracy level:** 2. The front is from one photo. The inside is a same-chain store of 1993, not Southland's own.

**Guessed (not from a Southland source):**
- the unit's depth (24 m) and the exact fixture count and order;
- which department sits where past the first two boards (the video shows DOLLS on the left and VIDEO on the right walking in; the rest is arranged to fit);
- the cash wrap's position and finish (the video shows it only behind a crowd);
- the show window left of the pier (the photo shows stock behind something there; glass is a guess).

All package art, price cards and screen pictures are original. No real toy brand, logo, character or box art is reproduced. The video's branded department board is left out; the boards carry plain department words only.

**Frame.**
- **The unit:** 6 m wide and 24 m deep (map tiles x 131–142, y 71–73). It faces east onto the hall between Sound Shop (north) and Miller's Outpost (south).
- **u** runs along the frontage from z = −58 (the viewer's right, Sound Shop's side) to z = −52 (u = 6).
- **d** runs into the store (−x); d < 0 is out in the hall.

## Front (from the photo)
- **Wall tile.** White 15 cm glazed tile from the top of the fascia (3.4 m) to the lane ceiling, with single red and blue accent tiles scattered a few tiles apart.
- **Fascia.** A royal-blue band across the whole unit, 2.6–3.4 m, standing 0.25 m out over the hall.
- **Letters.** "KAY·BEE TOYS" in red lit channel letters with a round dot: heavy sans capitals, caps 0.40 m, 4.28 m long, centred, 10 cm deep. Outlines: FreeSans Bold, from `make_letters.py`.
- **Opening.** Open to the hall, 2.6 m high, from the unit's right edge to a blue pier at u 4.7–5.0. A blue pedestal (0.6 m square, 1.85 m tall) with a red ball (0.44 m) stands in the right of the opening.
- **Left of the pier.** A small show window over a blue bulkhead, with a stack of stock behind it.
- **Lit ceiling.** The bright slatted band under the fascia in the photo: a luminous louvred ceiling at 2.62 m over the first 1.5 m.
- **Sale signs.** Three yellow signs with red lettering hang just inside, and stock is piled high on both sides of the opening.

## Inside (from the video; walkable)
- **Room.** Tan level-loop carpet. White 2 × 4 ft lay-in ceiling at 3.2 m with two rows of fluorescent troffers. Off-white side walls, a tan back wall with the stockroom door and an exit sign.
- **Wall shelving.** White 4 ft gondola bays, five shelves to 2.15 m, pegboard backs, ticket strips on the shelf lips, and overstock (more product and shipping cartons) stacked to the ceiling. Left wall from d 1.7: dolls, preschool, games, sports. Right wall from d 4.6: video, vehicles, action toys, games, soft toys. Two bays of soft toys on the back wall.
- **Middle.** A rolling wire dump bin of soft toys, a low double-sided gondola with end caps (d 7.2–12.1), a stack-out with an orange price card, a second gondola (d 15.0–19.9), a second bin.
- **By the door.** A stack with a toy castle on top (video), a promotional stack with an orange "9.99" card, and the cash wrap on the right with a beige register; the video game case (tan cabinet, a demo TV, glass-fronted shelves) is on the wall behind it.
- **Department boards.** Teal boards with lime capitals hanging across the aisles: DOLLS, VIDEO, PRESCHOOL, VEHICLES, GAMES, ACTION TOYS, SPORTS, STUFFED TOYS.
- **Not built.** The chalk queue lines on the carpet and the closed gate (both belong to the video's sale morning), and shoppers.

## Files
- `prototypes/godot-mall/project/tools/stores/kay_bee/store.gd` (geometry, materials `kb_*`), `paint_store.py` (textures → `tex/kb/`), `make_letters.py` → `letters.json`.
- Hooks in `tools/build_mall.gd` (dispatch, `BUILT_RECTS`, `kb_` materials) and `tools/open_interiors.py` (s18).
