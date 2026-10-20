# Radio Shack: front and store (1995 map, store s21b)

**Sources (Oct 7, 2026).**
- The Southland facade record (level 3, from Steven's photos): "a deep brown fascia box with the lit red wordmark standing off it on dark returns, a bright soffit, and an aluminium-and-glass front on a green marble plinth", with a dressed window.
- The 1993 Hammond Square commercial (23.8–24.15 s) shows the red "Radio Shack" letters of the period.

**Accuracy level:** 3 for the front. The inside is a period type.

**Guessed:** the depth (16 m of the 30 m stall), the door position, the fixtures.

**Frame.** An 8 m front facing west onto the east hall (x = 2, z 26–34), between Coach House Gifts and GNC. Map tiles x 149–156, y 113–116.

## Front (rebuilt Oct 7, 2026: Steven's sign pass)
- **Steven (Oct 7):** "the overall building facade needs to be that one" (refs/radio-shack-front.png); the other four photos (refs/radio-shack-letters-1..4.png) show how the 3D letters are built. Two words, "Radio Shack".
- A black fascia band, 1.9 m deep, with the red channel letters: the logo traced from refs/radio-shack-letters-1.png (warped square-on onto the frontal photo), 4.2 m across, red acrylic faces lit from inside, dark returns 12 cm deep, a darker red trim cap, and a red halo on the fascia. Built by `tools/stores/signs/` (make_logos.py → rs_logo.json, channel.gd).
- Glass in black frames on a low black base, the door at the left, a pale stone pier at the end; the window dressed with boxed electronics on black risers.
- **Superseded:** the deep brown fascia, aluminium frames and green marble plinth from the facade record.

## Inside (walkable; rebuilt Oct 20, 2026)
**Source:** the video Steven sent ("Christmas shopping at RadioShack in 1999", a mall store, 6:44). He asked to recreate it "as closely as possible to the layout and details shown in the video". The store is four years later than the 1995 map. Kept from it are the fixtures, colours and kinds of goods. No products or brand marks are copied: the goods are painted by `tools/stores/small/paint_rs.py`, and the only words are department headers.

- **Walls (0:00–0:44, 5:20–5:56).** Grey shelf units to 2.3 m along the left wall, the right wall and the back:
  - three shelf levels with red price strips on their lips;
  - boxed goods low and black out-of-box electronics above (phones, cordless phones, answering machines, scanners), each item with a small white tag;
  - white pegboard of blister-packed parts from 1.35 m to the top.
- **Above the walls (1:00–1:20, 3:24).** A black-and-white striped valance, then a navy band to a dark charcoal lay-in ceiling with bright 2 × 4 troffers.
- **Headers.** "Telephones" over the left wall and "Cellular" over the right. The back wall carries a red "PowerZone" header over a wall of battery cards (0:56–1:20, 2:36–3:00).
- **Cash wrap (0:00–2:20, 4:00–6:40).**
  - A 6.4 m glass showcase counter runs down the right side on a black kick base, with phones on glass shelves inside.
  - Two beige CRT terminals sit on the clerks' side. Each has a blue screen, a colour-keyed keyboard and a card swiper.
  - Black bags are stacked at the far end.
  - The clerks' aisle and the phone wall behind are beyond the walk grid (u > 6.4).
- **Floor (0:48–0:56).**
  - A low double-sided gondola of boxed goods down the middle.
  - Stacks of R/C truck boxes (purple-blue with yellow flames, invented).
  - A blue R/C monster truck on a white pedestal inside the door.
  - A satellite dish display with a card.
  - Dark grey carpet.
- **Guessed.** Which side the counter is on (the video only shows the clerks' backs to a phone wall), and the depth (16 m).
- **Code.** `tools/stores/small/radio_shack.gd`, materials `s6_rs_*` in `store2.gd`, stock sheets `md_stock_rs*`.

## Files
`tools/stores/small/store2.gd` (the four Wave 6 shops, materials `s6_*`), `paint.py` → `tex/sm/`; the sign: `tools/stores/signs/` (materials `sg_rs_*`). `rs_letters.json` is no longer used.
