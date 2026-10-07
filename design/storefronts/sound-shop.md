# Sound Shop: front and store (1995 map, store s19)

**Sources (Oct 6, 2026).**
- **The front and a look inside:** the 1993 Hammond Square Mall commercial (YouTube `WvaGN9lUpr0`, 4.3–4.9 s). It shows a Sound Shop of the same Louisiana chain: a dark fascia with red italic letters, a wide open front, and a bright white store with wall racks, low white islands and big posters hung high.
- **For period detail:** Valley View Mall, Dallas, Sept 1995 (YouTube `rjvPS1FIqS4`, 3:57–4:17), which shows Camelot Music, a different chain: red letters and a poster band.
- **The layout:** Steven (Oct 6, 18:30): the registers were on the **left** looking in. Behind them was the concert box office: the counter sold concert tickets. It is built as a generic "TICKETS · CONCERT BOX OFFICE" board, with no ticket company's name or logo.

**Accuracy level:** 2. The front and the inside come from another mall's Sound Shop. Steven's memory sets the counter.

**Open question for Steven.** The 8-bit game's record for Southland's Sound Shop (`facade_records.json`, source not stated) describes a taupe bulkhead, letters lit yellow to orange with a red halo, and a satin-aluminium door frame around one big sheet of glass. The 3D front follows the Hammond video instead: a dark fascia, rose-red letters, open front. If his memory matches the record, the fascia colour, the letters and the glass are quick to change.

**Guessed (not from a Southland source):**
- the depth (24 m, as Kay-Bee next door) and the fixture count;
- the categories on the header boxes (ROCK, POP, R & B, COUNTRY, RAP, JAZZ, CLASSICAL, SOUNDTRACKS, CAJUN & ZYDECO, GOSPEL, NEW RELEASES, CASSETTES). CAJUN & ZYDECO is a guess for a Houma record store;
- the browser bins down the middle (the commercial shows only the front of the store).

All covers, posters, act names and dates are invented: scribbled titles, generic shapes. The ticket board uses real 1995 weekdays (period-art-director).

**Frame (as Kay-Bee's).**
- **The unit:** 6 m wide and 24 m deep. Map tiles x 131–142, y 68–70. It faces east onto the hall between Lane Bryant (north) and Kay-Bee Toys (south).
- **u** runs along the front from z = −64 (the viewer's right, Lane Bryant's side) to z = −58 (u = 6, Kay-Bee's side).
- **d** runs into the store (−x).

## Front
- **Fascia.** Dark grey, 2.75–3.6 m, standing 0.22 m out, with a light reveal under it. The mall wall above it is dark grey too, as in the commercial.
- **Letters.** "SOUND SHOP" in fat rounded italic capitals lit rose-red: caps 0.36 m, 3.6 m long. Outlines: Nunito Black Italic (OFL), from `make_letters.py`.
- **Opening.** Wide open between two dark grey piers (0.32 m) with deep reveals. A dark grey soffit with three downlights covers the first 0.8 m.
- **At the door.** A chrome stand with a "SALE $9.99" card.

## Inside (walkable)
- **Room.** A light vinyl tile floor and a white lay-in ceiling at 3.0 m with two rows of troffers. White walls. A stockroom door with an exit sign at the back right.
- **Registers (left, Steven).** A white counter with a red band, 3 m long, parallel to the left wall from d 1.4, with two beige registers. Behind it on the wall: a dark panel with the TICKETS board (2 m × 1 m: invented acts, 1995 dates, a seating chart), and a back counter of cassettes behind glass.
- **By the door.** Two white islands of new-release CDs with NEW RELEASES and TOP 30 cards on stems (commercial).
- **CD walls.** White wall racks of CDs face-out, nine rows to about 2 m with a cassette row at the bottom. They run along the left wall past the counter and the whole right wall, with radiused end caps. A lit header box hangs over every other bay. Cassette racks fill the back wall.
- **Middle.** Two runs of waist-high CD browser bins (six bins each), with cassettes in the kick and a NEW RELEASES card at each run's front.
- **Posters.** Two strips of four invented album posters, hung from the ceiling over the browser runs (commercial: big posters high up).

## Files
- `prototypes/godot-mall/project/tools/stores/media/sound_shop.gd` (geometry), `kit.gd`, `paint.py`, `make_letters.py` → `ss_letters.json`.
- Hooks: `tools/build_mall.gd` and `tools/open_interiors.py` (s19).
