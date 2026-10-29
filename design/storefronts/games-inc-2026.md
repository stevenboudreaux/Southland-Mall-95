# games, inc. (2026 map, store s52: the old Blockbuster Music box)

**Source (Oct 28, 2026).** Steven's Oct 23 2026 footage: IMG_4443 (the front from the hall, then
the whole depth of the store, 58 s), IMG_4444 (the air hockey end) and photo IMG_4445 (the
same, upright). Full-res frames cut at 1 fps: `2026 Mall/_derived/full/games/` on the Mac.
The directory (IMG_4455) lists the arcade as Pocket Change; the sign says games, inc.

**Accuracy level:** 3 for the room (walked end to end on video), 1 for the machines (the kinds
and where they stand are from the frames; the cabinets are Pocket Change's 1990s prop modules
standing in until each 2026 kind is painted).

**Frame.** The s52 rect, 8 x 40 m (4 x 20 tiles at x 89, y 130), on the Concourse's south side
between the vacant aqua-tile Pocket Change unit (s52b) and the food-court wall. The front faces
the hall (north); u runs along the frontage from the hall viewer's right, d into the store.
`tools/stores/games_inc/store.gd`, textures `paint.py` -> `tex/gi/`. Walkable: s52 is in
`layout_2026.json`'s `interiors_open` (and `KEEP_OPEN` in `tools/make_layout_2026.py`).

## The front (f003-f016)
- Mustard 6 x 12 glazed tile in a running bond over the whole front: piers each side, the
  frames round two display windows, and the head over a 3.8 m opening (u 2.1-5.9, 2.75 m tall).
  Tile returns run back through the front wall.
- A white panel over the opening carries the lit sign (`y26/parts/games.json`: green "games,
  inc." with the alien mascot). Hall-side star medallions on the piers either side are the
  mall's.
- Two display windows (dark frames, white sill at 0.45 m, white box behind) piled with Pokémon
  plush: Pikachu yellow, Charmander orange, Squirtle blue, Bulbasaur green. Built as soft
  coloured blocks (dynamic) for now.

## The room (f017-f058, g001-g006, IMG_4445)
- Wood-look vinyl plank floor, honey brown, 1.2 x 0.18 m planks, staggered.
- Walls: white slatwall to 2.45 m, then a red-orange band to the ceiling with a mustard stripe
  near its foot; a plush shelf runs along the right wall at 2.3 m, toys all along it.
- White 2 x 2 lay-in ceiling at ~3.4 m, parabolic troffers in two rows about every 3 m, a few
  black track spots. One white round pipe column mid-store (~20 m in), a thin black steel one
  further back (~29 m).
- Left, walking in: a party corner, two white folding tables with benches under a navy wall
  mural ("games, inc. CLAW MANIA", claws, a neon horizon); then the orange "GALACTIC PRIZE
  PORTAL" counter: lit glass showcases of small prizes with the big-prize plush wall behind, and
  a token changer past it. (Built with Pocket Change's `redeem` module: the counter 1.95 m off
  the wall, the prize wall on the wall, 5.4 m long, centred 8.3 m in.)
- Right wall: a long run of claw machines in LED-framed cabinets, front to back in banks with
  breathing room (five banks of four here, from 1.35 m in).
- Left wall past the counter: more claws, then four upright ticket/arcade cabinets (Crossy
  Road, a wheel game and the like in the footage; `video` uprights stand in), two more claws,
  two sit-down racers.
- The middle, front to back: a double coin pusher behind the party corner (11 m), two dome
  ticket games (the pink/blue drop domes with the "TAP" button in f045-f058; the `cyclone`
  stands in) at 15.4 and 18.2 m, two air hockey tables across the room at 24.4 and ~28 m
  (g001-g003), two kiddie rides at 33.4 m (the yellow motorbikes, g005-g006), four uprights on
  the back wall. The back door with its exit sign is on the right of the back wall.

## Guessed / to do
- Machine identities and cabinet art: paint the 2026 kinds from the frames (claws: white
  cabinets with RGB edge lighting and big plush; dome drop games; Crossy Road; the wheel game;
  the yellow kiddie motorbikes; the big "Deal or No Deal"-type ticket cabinets at the back).
  Steven asked for the games to be researched online against the frames.
- The plush windows and the shelf toys as real plush (a painted window texture would be
  cheaper and better than blocks).
- Exact counter and party-table positions (estimated from the walk; the counter's end is
  visible in f025-f027 about 10 m in).
- Whether the arcade keeps a service door to the vacant unit next door (not seen).
