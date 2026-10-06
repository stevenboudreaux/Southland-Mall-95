# Pocket Change: front and arcade (1995 map, store s52b)

**Sources (Oct 5, 2026).** Steven's photos:
- **The Southland store in 2009**, taken from the hall on the Chick-fil-A side, looking toward FYE (Blockbuster Music in 1995). Steven: "that's actually at the Southland Mall in 2009, but it's exactly how it looked in the 90s."
- **Other Pocket Change arcades of the 1990s–2000s**, for the interior: a 1995 front at Granite Run Mall, a food-court front with lit glass-block columns, a blue-lit interior, and a token changer.
- **The machine types:** a basketball cage row and a pair of skee-ball alleys.

Steven's description of the interior: the ticket redemption counter on the left as you walk in, claw machines, about four skee-ball, four basketball, the sit-in dinosaur ride in the middle, and the usual video games. "It was very dark."

**Accuracy level:** 2–3. The front is from one angled photo. The room is from memory and same-chain references.

**Guessed (not from Southland photos):**
- the room's finishes (black ceiling, dark walls, blue band and neon);
- the exact layout and machine count;
- the token rate.

The machines' titles and art are original: real titles and logos are not reproduced. The cabinet shapes, sizes and layouts follow the real 1990s machine types.

**Frame.**
- **The unit:** the store is 8 m wide and 40 m deep (map tiles x 93–96, y 130–149) and faces the Concourse (H5) to the north.
- **u** runs along the frontage from x = −110 (the viewer's right, toward Blockbuster Music/FYE) to x = −102 (u = 8, toward Chick-fil-A).
- **d** runs into the store (+z); d < 0 is out in the hall.

## Front (from the 2009 photo)
- **Wall tile.** Pale blue-green (Steven: "bluish green") 12-inch glazed tile with light-grey grout. On both sides of the entrance it climbs the mall's wall in steps, one tile column per step. Next to the fascia the columns are 9, 8, 7, 6 and 5 rows tall (2.7 m down to 1.5 m). The mall's own plaster wall is above and beyond.
- **Glass-block columns.** One clear 8-inch block wide and one deep (0.2 × 0.2 m). They stand 0.2 m out from the wall on tile plinths and run from 0.15 m up to the fascia at 2.4 m, about 11 blocks. That makes the opening ~4.6 m wide and 2.4 m tall.
- **Fascia.** A tile-clad box over the opening, spanning both columns: 5.0 m long (u 1.5–6.5) and ~1.05 m tall (2.4–3.45 m). It stands 0.2 m proud of the wall, with a polished stainless underside (the bright strip in the photo).
- **Letters.** "POCKET CHANGE" in raised channel letters: a heavy grotesque in caps, near-white brushed faces with grey returns. The caps are 0.35 m, the letters 7 cm deep and 2.5 cm off the tile. They start ~0.42 m in from the fascia's left end and fill it to near the right end, with the baseline at 2.9 m. The outlines are FreeSans Bold (a Helvetica clone), from `make_letters.py`.
- **Inside the opening.** Royal-blue returns run 0.8 m back through the front wall, with a small notice sign on the right return (2009: a camera notice; 1995 wording unknown). The head is black over the returns. The arcade carpet starts at the threshold.
- **Not lit.** The letters are non-illuminated, and the hall lighting shows them.

## Inside (walkable, dark)
- **Room.**
  - Ceiling: black lay-in at 3.6 m.
  - Walls: dark charcoal-navy, with a royal-blue band at 2.45–2.6 m and a blue neon tube along both side walls at 3.3 m.
  - Floor: a plain dark charcoal cut-pile carpet, one solid colour with no pattern and no glow (Steven, Oct 6, 2026: "remove the graphics from pocket change carpet just make it solid dark color").
  - Light: black can downlights down the room, with glowing lamp faces (in Godot 4.7 the bake takes its light mostly from emission), and three brighter ones over the redemption counter. With the machines' screens, marquees and lamps, that keeps the room dark but readable (until Oct 6 the carpet also had a glowing confetti pattern; it was removed at Steven's request). The first full-quality bake without the glowing lamp faces and carpet came out nearly black.
  - Back: an employees-only door with an exit sign.
- **Layout (Steven, Oct 6).** Walking in, everything on the right stands flush against the right wall in one line, front to back:
  - three claw machines (styles 0–2), d 0.85–3.3;
  - four skee-ball alleys, played toward the wall, d 3.4–6.4;
  - four basketball games, d 6.5–10.6;
  - then video games to the back.

  On the left:
  - the token changers against the front wall;
  - the redemption counter (a 1.6 m return, then a 5 m glass showcase facing the room, d 3.1–8.1), with the 5 m prize wall behind it;
  - then video games, the two twin racers (d 14.5–18.3), more video games, three pinball machines (d 29–31.6), and video games up to the back door.

  The middle:
  - the sit-in dinosaur ride (d 11.4–14.0), its doorway toward the entrance, so you can step in;
  - an island of back-to-back uprights (d 18.6–20.7);
  - two air hockey tables end to end (d 25.6–28 and 30.8–33.3).

  The air hockey tables match Steven's photo: white and silver cabinet, blue stripe, blue playfield, a chrome arch with a lamp and score unit, clear side guards.

  Three more uprights stand on the back wall.
- **The blue band** under the neon (2.4–2.62 m) is not in the lightmap. At 15 cm it was one texel tall and broke into blocks (Steven's phone, Oct 6). It is now probe-lit with a soft glow of its own.
- **Machines.** Each is a prop module in `tools/stores/pocket_change/` (contract in its README.md): crane, skee, hoops, ride, video, driver (racers and pinball) and redeem (counter, prize wall, tokens). airhockey (from Steven's photo, Oct 6). Each module has a texture painter (`paint_<m>.py` → `tex/pc/<m>_*.png`).

## Period notes (1995)
- **No anachronisms:** CRT screens, backlit marquees, red 7-segment scores, coin doors with token slots, orange ticket strips. No LCDs, card readers or LED boards.
- **The ride.** Steven remembers the Lost World ride, but that came out in 1997. The 1995 map has the earlier (1994-era) enclosed dinosaur-safari motion ride type. A 1997+ year map can carry the Lost World style.
- **Which games.** Steven will list the actual games. Each listed game's cabinet type, colours and layout can then be matched, without copying its art or logo.

## Build notes
- `store.gd` builds:
  - the front, into the hall's (H5) mesh;
  - the room, into `pc_shell`;
  - the machines, into `pc0_mach` … `pc3_mach` (one mesh per 10 m, for culling), at a coarse lightmap texel (1.5×), with compressed vertex data for the dynamic parts.
- **Lightmap atlas.** Plush, the skee-ball rings and other tiny faces go to the dynamic meshes and are lit by probes. In the lightmap, thousands of tiny charts had doubled the atlas. The atlas is now 5 × 1024² layers (was 4); the `.exr.import`'s `slices/vertical` must come back from the Mac with each bake.
- **Sign letters.** These are dynamic, lit by probes plus a little emission standing in for the hall's light.
- **Walk grid.** `tools/open_interiors.py` opens the whole unit. Machine obstacles are padded 0.25 m so the camera stays out of the cabinets.
- **Store probe.** The store has its own interior ReflectionProbe.
- **`BUILT_RECTS`** keeps the neighbours' generic interiors out.
- **Previews.** `tools/qa/preview.sh "store:POCKET CHANGE" …` renders the store without a bake.
