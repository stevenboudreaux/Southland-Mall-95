# Gumballs: front and store (1995 map, store s8)

**Source (Oct 6, 2026), chosen by Steven:**
- **The video:** "1995 Mall commercial (North East Mall 80s, 90s mall)", YouTube `b1Ilr8WpkgY`, channel Hootyhaha. It is a 1994–95 mall promotional tape of North East Mall in Hurst, Texas. Steven: "the logo is perfect … all of the stuff on the inside that you can see is like perfect … it's the exact store just in a different mall."
- **Frames used:**
  - the sign at 1:07–1:09;
  - the front at 2:50–2:54 and 3:29;
  - the inside at 2:56–3:33.
  - They are kept out of the repo, in the working folder only.

**Accuracy level:** 2. The sign and fixtures come from a same-chain store of the same year; the layout and the corner front are Southland's.

**What Steven asked for:** the most care of any store so far. That means the logo, the colour scheme, the candy, the gumball machines, the T-shirts, the lava lamps and the little knickknacks. It was where the kids hung out, in the middle of the mall.

**Guessed (not from a Southland source):**
- how the front wraps the corner (the video's store is in line);
- where each fixture stands;
- the cash wrap's place;
- the lava lamps: not seen in the video, but Steven remembers them, and they were sold widely again by 1995.

All T-shirt graphics, posters, cards, packaging and the chocolate sign's wording are original. No band, film, cartoon, sports or candy brand, logo or character is reproduced:
- The video's licensed plush and sweatshirts are replaced with generic bears, dogs and cats.
- The branded candy dispensers become a plain blue "SNACKS" tower.
- The "Sweet Shop" sign becomes "Fudge & Chocolates".

## Frame
- **The unit:** a corner store, x −20 … −10 and z 36 … 48 (map tiles x 138–142, y 118–123). It is open on two faces:
  - **Hall face:** east, x = −10, 12 m long, onto the east hall, between Lerner Shop (south) and the court corner.
  - **Court face:** south, z = 48, 10 m long, onto the Dillard's court, between the corner and Sports Avenue (west).
- **Back walls:** west (x = −20, Sports Avenue behind) and north (z = 36, Lerner Shop behind).

## Front (from the video)
- **The sign:**
  - "Gumballs" in a tall, slanted brush script, with a sweeping swash under the word. Glossy cobalt-blue acrylic faces, dark navy returns, on stand-offs.
  - Under the middle, a cluster of coloured gumballs over a blue plaque reading "Sweet Ideas", in cream serif capitals and lower case with a dark red outline.
  - The letters are a traced brush-script face (Mr Dafoe, OFL), thickened. It is not the original artwork, but close in shape.
  - There is one sign on each face.
- **Fascia:** a white band, 2.70–4.05 m, standing 12 cm proud. A grey reveal sits above it, then white bulkhead to the lane ceiling.
- **Openings:** the corner is open from the hall face's z 40.2 round to the court face's x −15.0.
  - The rest of each face is a show window over a white bulkhead.
  - The hall window holds T-shirts and a "BUY 1 T-SHIRT GET 1 ½ PRICE" card.
  - The court window holds lava lamps and boxed gifts.
- **Soffit:** white, 1.2 m deep inside the opening, with round recessed downlights (video).

## Inside (walkable)
- **Room:**
  - white lay-in ceiling at 3.2 m with 2 × 2 ft troffers (video);
  - white vinyl tile floor (guessed; the floor is not seen);
  - white walls.
- **North wall:** the bulk-candy wall.
  - Four tiers of clear acrylic scoop bins, filled with gumballs, jelly beans, sour worms, wrapped mints, rock candy and so on.
  - Small white price labels on the lips.
  - Plush on two white shelves above (video 3:00–3:05).
- **West wall, back:** more bins, with satin jackets hung on a rail above them (video 3:22–3:28).
- **West wall, front:** the black slatwall of bagged T-shirts to the ceiling, with round price tags (video 3:07–3:12), then posters and a keychain spinner by the court window.
- **By the corner door:**
  - the big globe gumball machine on its maroon stand (video 3:30–3:32);
  - two small red gumball machines;
  - a postcard spinner and a card rack (video 2:50).
- **North-east corner:** the cash wrap.
  - An L of white-framed glass showcases with boxed chocolates and lollipops.
  - A register.
  - The red oval "Fudge & Chocolates" sign hanging over it (video 2:56).
- **Middle:**
  - a low white island with boxed novelties and knickknacks (snow globes, mugs, troll-style dolls, slinky-type springs, figurines);
  - lava lamps on its end;
  - a blue "SNACKS" dispenser tower;
  - a round plush bin.
- **Not built:** shoppers, the egg-crate mall ceiling over the sign (it is North East Mall's, not Southland's).

## Files
- `prototypes/godot-mall/project/tools/stores/gumballs/store.gd` (geometry, materials `gb_*`).
- `paint_store.py` → `tex/gb/`.
- `make_logo.py` → `logo.json`.
- Hooks in `tools/build_mall.gd` (dispatch, `BUILT_RECTS`, `gb_` materials) and `tools/open_interiors.py` (s8).
