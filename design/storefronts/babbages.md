# Babbage's: front and store (1995 map, store n39b)

**Sources (Oct 6, 2026).**
- **The front and the inside:** a home video of Babbage's in Killeen Mall, Killeen, Texas, 1997 (YouTube `W4H3YabEcsw`, credit Cyrus Martin). Steven: "hands down this is the best, it's from 1997 but that's perfect." Notes in the project doc `claude/babbages-1997-notes.md`.
- **The layout:** Steven's memory (Oct 6, 18:05): the cash registers were on the **left** looking in from the mall. The store was not especially deep: open floor, then a few low rows of books, then the shelving that wraps round the back wall and along both sides.
- **The facade record** (level 3): white curved bulkhead, fat rounded pink neon letters, a dark red column at each side of a wide opening, a bright shop of game boxes.

**Accuracy level:** 3 for the front (the record and the video agree), 2 for the inside (a same-chain store two years later, laid out to Steven's memory).

**Guessed (not from a Southland source):**
- the room's depth (8 m: Corn Dog 7's dining room is behind it) and the fixture count;
- what the 2 m jog on the right of the stall was. It is built as a show window;
- the header words. They are generic categories, because the video's headers name consoles;
- the mall wall over the fascia (white, with a return-air grille as in the video).

**Left out for 1995 (period-art-director, Oct 6):** the video's trade-in card (1997). All box art, covers, posters and price cards are invented. No console, game, logo or character is reproduced. The video's character standee and console posters are replaced by generic cards.

**Frame.**
- **The unit:** a 6 m front at z = 60 (x −130 to −124), facing north onto the hall by Corn Dog 7. A 2 m jog on the right (x −132 to −130) stands back to z = 62. The room runs to z = 68: 8 m wide at the back, 8 m deep. Map tiles x 83–85, y 130–133, and x 82, y 131–133.
- **u** runs along the front from x = −130 (the viewer's right, u = 0) to x = −124 (u = 6). The jog is u −2 to 0.
- **d** runs into the store (+z); d < 0 is the hall.

## Front
- **Fascia.** White, 2.75–3.65 m, standing 0.3 m out over the hall, with its bottom edge rounded. The mall wall above it is white, with a dark return-air grille.
- **Letters.** "Babbage's" in fat rounded lower-case channel letters with a capital B, lit pink-red: caps 0.42 m, 3.06 m long, 9 cm deep. Outlines: Nunito Black (OFL), from `make_letters.py`.
- **Opening.** Fully open between two round maroon columns (0.4 m) at u 0.2 and u 5.8.
- **Soffit.** A white soffit at 2.75 m over the first metre inside, with three downlights. It steps up to the 3.0 m ceiling.
- **The jog.** A white wall, a 0.55 m white bulkhead and a glass show window. Behind the glass, a white riser with PC boxes.
- **In the opening:** a white demo kiosk with a TV showing an invented racing game (at the left, as in the video), a chrome stand with a red "new low price · 32-BIT SYSTEM · $299.99" poster (the fall 1995 price of a 32-bit console), and three hanging cards just inside (HOT SALE, ONLY $19.99, GIFT CERTIFICATES).

## Inside (walkable)
- **Room.** Dark grey carpet. A white 2 × 4 ft lay-in ceiling at 3.0 m with two rows of troffers. A white soffit round the back and both sides at 2.62 m, with a maroon trim line (video 19:42).
- **Cash wrap (left, Steven).** A white counter with a maroon band, 2.6 m long, parallel to the left wall from d 0.9. It has a beige register and an orange crate of games (video 1:00). Behind it, white slatwall with shelves of games and peg accessories, and the yellow NEW RELEASES board with weekly 1995 street dates (video 0:22–6:32).
- **Wall bays.** White bays of face-out stock with radiused white end caps, five shelves to 1.77 m, and a lit header box over each bay (white, dark grey words: 16-BIT, 32-BIT, CD-ROM, PC GAMES, FAMILY, EDUCATION, VALUE ZONE, ACCESSORIES, HANDHELD, NEW RELEASES, 8-BIT, BOOKS). They run along the left wall past the counter, across the back, and down the right side, with round maroon columns at the corners (video 10:12, 19:32).
- **Low rows of books (Steven).** Two short double-sided gondolas, about 1.1 m high, across the middle toward the back, holding strategy guides and computer books.
- **Not built.** Shoppers and staff, the character standee, the "OUT OF STOCK" cards.

## Files
- `prototypes/godot-mall/project/tools/stores/media/babbages.gd` (geometry), `kit.gd` (shared fixtures, materials `md_*`), `paint.py` (textures → `tex/md/`), `make_letters.py` → `bb_letters.json`.
- Hooks: `tools/build_mall.gd` (dispatch, `BUILT_RECTS`, `md_` materials) and `tools/open_interiors.py` (n39b).
