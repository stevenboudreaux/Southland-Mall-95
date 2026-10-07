# Lerner Shop: front and store (1995 map, store s10)

**Sources (Oct 6, 2026).** Regional videos Steven sent (project doc `claude/hammond-square-video-matches.md`):
- the 1993 Hammond Square commercial (YouTube `WvaGN9lUpr0`, 22.4 s): "Lerner" in white script with NEW YORK under it;
- the 1992 Pecanland Mall opening-day video (`8ZnqaDZMufk`, 16:37–17:13): the same white script on a dark fascia over a glass front, and pink and purple clothes and sale signs inside.

**Accuracy level:** 2. The sign comes from same-chain stores of 1992–93. The layout is guessed.

**Guessed:** the depth (28 m of the 40 m stall), the cash wrap on the left, the fitting rooms at the back, the fixture order, the mauve carpet.

**Frame.** A 14 m front on the east hall (x = −10, z 22–36), beside Woolworth. Map tiles x 129–142, y 111–117. u runs from z = 22 (the viewer's right, Woolworth's side); d runs into the store (−x).

## Front
- A dark wood fascia, 2.8–4.1 m, with "Lerner" in white lit script letters (Mr Dafoe, OFL) and NEW YORK in small white capitals under it.
- Glass windows with dark wood frames each side of a 5 m doorway. Mannequins in the windows.
- A white soffit with downlights just inside.

## Inside (walkable)
- Mauve carpet, cream walls, a lay-in ceiling with troffers.
- White slatwall of face-outs down both sides. The cash wrap is on the left.
- Two columns of round racks, four-ways and tables.
- Purple and pink cards hung over them: $15, SALE, NEW ARRIVALS, 2 for $25.
- Three fitting rooms across the back, and the stockroom door.

## Files
`tools/stores/apparel/more.gd` (all five Wave 4 stores, materials `a2_*`), `paint_more.py` → `tex/a2/`, `make_signs_more.py` → `lerner_letters.json`, `lerner_ny_letters.json`. Hooks in `build_mall.gd` and `open_interiors.py`.
