# Zales: front and store (1995 map, store s7)

**Sources (Oct 7, 2026).**
- The Southland facade record (level 2, from a photograph of the shop): "stone-tile piers and header, a wood fascia carrying a mauve sign box with brushed-silver letters, and an open front onto lit glass jewellery cases on a wood base, a cream room with a square column, rece[ssed lights]".
- The 1993 Hammond Square commercial (18.2–18.55 s) shows ZALES JEWELERS of the period.
- The map gives navy carpet.

**Accuracy level:** 2.

**Guessed:** the case layout and the second front's sign.

**Frame.** A corner shop beside Corn Dog 7, open on two halls. The north front is at z = 68 (x −154 to −146); the east front is at x = −146 (z 68–78). Map tiles x 71–74, y 134–138.

## Front
- Stone tile over both fronts and on the piers.
- A wood fascia with a mauve sign box, carrying ZALES and JEWELERS in brushed-silver letters. The east front carries a second box with ZALES.
- Open fronts with a cream soffit and downlights.

## Inside (walkable)
- Navy carpet, cream walls, a square cream column.
- Lit glass cases on wood bases along the west wall and the back, and a back-to-back island of two cases, all with trays of rings, chains and watches on navy velvet.

## Files
`tools/stores/small/store2.gd`, `make_signs.py` → `zl_letters.json`, `zl_sub_letters.json`.

## Sign pass (Oct 7, 2026)
Steven sent three photos of Zales mall fronts (refs/zales-1..3.jpg) and asked for the corner to be two-sided. Both faces now have: tan stone tile (the fascia and piers), a cherry panel 3.4 × 1.4 m, ZALES over JEWELERS traced from refs/zales-1.jpg in white lit letters (ZALES 2.6 m across). Replaces the mauve panels and the stand-in silver letters (`zl_letters.json` is no longer used). Files: `store2.gd` zales() and zales_sign(), `tools/stores/signs/` (zl_*).
