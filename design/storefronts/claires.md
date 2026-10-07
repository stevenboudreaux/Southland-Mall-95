# Claire's Boutiques: front and store (1995 map, store s30)

**Source (Oct 7, 2026).** The Southland facade record (level 1): "Claire's, after a photograph of a 1990s shop: a wall of pink-veined cream marble, a white sign box with the name in tall narrow dark-red letters lit red from behind and ACCESSORIES in spaced capitals, and a wide opening under a dark soffit onto walls of carded jewellery, bags, hats and sale signs." The game's two flat fronts (north and west).

**Accuracy level:** 1 to 2 (the record follows a photo of a 1990s Claire's, not the Southland one). The name is stand-in type (DejaVu Sans Condensed, squeezed narrow).

**Guessed:** the depth (10 m), the layout, the counter, the spinners, the SALE cards.

**Frame.** A corner: an 8 m front facing north at z = -6 (x 12 to 20) and a 4 m front facing west at x = 12 (z -10 to -6), beside Gordon's Jewelers. Built from the north edge, 10 m deep; the west wall stays open for its first 4 m. Map tiles x 154–157, y 92–96.

## Front
- Cream marble with pink veins over both openings; a corner pier wrapping both fronts.
- A white sign box on each front, the name in tall narrow dark red lit red from behind, ACCESSORIES in spaced capitals.
- Wide openings under a dark soffit; a SALE board on a stand at the north opening.

## Inside (walkable)
- A pale pink floor, blush walls, a dark ceiling with spots.
- Walls of carded jewellery on purple slatwall over white base cabinets, a shelf of hats and little bags on top: right wall, back wall, the left wall behind the west front.
- Two chrome spinners of cards; SALE cards hung over the floor; the white cash counter at the back.

## Files
`tools/stores/small/wave8.gd`, `paint8.py` → `tex/w8/`. Hooks in `tools/build_mall.gd` and `tools/open_interiors.py`; a new `open_u0_to` option on `apparel/more.gd`'s `shell2`.

## Sign pass (Oct 7, 2026)
See photos/ (Steven's photos for this store) and tools/stores/signs/ (make_logos.py batch3, channel.gd sg_* materials).
White box sign on both faces of the corner: "Claire's" in a compressed Bodoni (Bodoni Moda Bold, OFL, fitted to the photo's word box) as black letters on red returns with a red glow, ACCESSORIES in red (Josefin Sans, OFL). Replaces the flat painted sign.
