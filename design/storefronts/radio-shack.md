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

## Inside (walkable)
- Grey carpet, white walls.
- Pegboard bays of parts and boxed electronics on both walls, a gondola down the middle.
- The counter with a register at the back.

## Files
`tools/stores/small/store2.gd` (the four Wave 6 shops, materials `s6_*`), `paint.py` → `tex/sm/`; the sign: `tools/stores/signs/` (materials `sg_rs_*`). `rs_letters.json` is no longer used.
