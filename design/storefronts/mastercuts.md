# MasterCuts: front and salon (1995 map, store s24mc)

**Sources (Oct 7, 2026).** The Southland facade record (level 3, from Steven's photos): "a band of sea-green terrazzo with two brass lines, white condensed lettering standing off on black returns, a fluted cherry rail and cherry piers; shelves of bottles, a style poster, price balloons." The 1992 Pecanland video (8:16–8:28) shows a MasterCuts salon of the period.

**Accuracy level:** 3 for the front (record). The salon is a period type.

**Guessed:** the depth (14 m of the 28 m stall), the glass front with an open door, the three styling stations, the shampoo bay, and the reception desk.

**Frame.** A 4 m front facing west onto the east hall (x = 2, z −48 to −44). Map tiles x 149–155, y 76–77.

## Front
- A sea-green terrazzo band with two brass lines, carrying "MasterCuts" in white condensed letters on black returns (DejaVu Sans Condensed Bold). A white wall above.
- A cherry rail under the band, and cherry piers.
- Glass on a cherry bulkhead, and an open door.

## Inside (walkable)
- A light vinyl floor and white walls.
- At the front: a reception desk with a register and a shelf of bottles.
- Three styling stations on the left wall: cherry counters, mirrors, hydraulic chairs.
- At the back: a shampoo bay with two basins.
- A style poster (an invented profile) and a CUTS $8 card.

## Customers (Oct 20, 2026)
- **Steven:** "make the logic of regis apply to mastercuts. only 1-2 woman in chair at a time, no other congregating here."
- MasterCuts is no longer a store or window goal for the crowd (`npcs.json` "no_browse").
- Up to two women at a time: each of two salon slots (`npcs.json` "salons") sends one woman from the crowd to a free styling chair. The chairs are at x 6.7 / 8.3 / 9.9, z −45.22, facing −z as built (backs to the mirrors). She sits for 150–330 s, then rejoins the crowd, and the slot waits 20–60 s before the next.
- No stylist.

## Files
`tools/stores/small/store.gd`, `paint.py`, `make_signs.py` → `mc_letters.json`.
