# Solarium: front and tanning lobby (1995 map, store n8)

**Source (Oct 7, 2026).** The Southland facade record (level 1, from Steven's memory): "a pale stone fascia carrying only the name, in soft aqua-green lowercase neon bent as one tight line; under it a glass front onto a calm tanning-salon lobby: sea-glass walls, a white front desk with an aqua stripe, a palm, a shelf of lotions and a lit beach print."

**Conflict (open question):** the game's flat front shows a dark teal fascia and clothing racks. The 3D follows the record.

**Accuracy level:** 1. The neon is traced from a stand-in face (Poppins Medium) as separate letters, not one joined line.

**Guessed:** the depth (8 m of the 26 m stall), the layout, the two tanning rooms at the back.

**Frame.** A 6 m front facing east at x = -10 (z -86 to -80), beside Rave, built 8 m deep. Map tiles x 140–142, y 57–59.

## Front
- Pale stone fascia with "solarium" in soft aqua-green neon.
- White-framed glass with the doorway in the middle.

## Inside (walkable)
- Sandy floor, sea-glass walls.
- The white front desk with an aqua stripe and a register; a white bench; a potted palm by the window.
- A shelf of lotions; a lit beach print; two tanning-room doors across the back.

## Files
`tools/stores/small/wave9.gd` (the six Wave 9 shops, materials `w9_*`), `paint9.py` → `tex/w9/`, `make_signs.py` (letters). Hooks in `tools/build_mall.gd` and `tools/open_interiors.py`.
