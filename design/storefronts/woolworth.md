# Woolworth: front and store (1995 map, store s13)

**Sources (Oct 6, 2026).**
- **The front:** the Southland facade record (level 3, from photos): a red panel fascia, a white light-box with red slab-serif lettering shadowed in gold, and a wide open front onto a bright white five-and-dime.
- **The inside:** a home video of Woolworths at Signal Hill Mall, Statesville, NC, 1991 (YouTube `JtpaAQChCmo`). Steven (Oct 6, 17:54): "this is the exact Woolworth layout, use this." Notes in the project doc `claude/woolworth-interior-notes.md`.
- **Steven (Oct 6):**
  - Southland's Woolworth had the restaurant, on the **right** as you face the store from the mall. It was entered from inside the store and through **its own door from the mall**.
  - **No garden center.**

**Accuracy level:** 3 for the front (record), 2 for the inside (another store's layout, which Steven confirmed matches).

**Guessed (not from a Southland source):**
- the depth (36 m of the 64 m stall: a square sales floor; the stall's back half is left as stockroom);
- the restaurant's mall door: a glass storefront with an aluminium-framed door held open, and a "Restaurant" plate on the fascia over it;
- the red floor stripe and the red band of department names (from the video; still to confirm for Southland);
- the department layout behind the front end, and the department words.

All packaging, food photos and menu lines are invented. The only real name shown is the store's own. The video's 1991 "Outlet Center / storewide values 50% off" sale cards are left out. The toy aisles reuse Kay-Bee's invented toy packaging.

**Frame.**
- **The unit:** a 36 m front on the east hall (x = −10, z −14 to 22), 36 m deep (to x = −46). Map tiles x 125–142, y 93–110. Lerner Shop is to the north.
- **u** runs along the front from z = −14 (the viewer's right, u = 0) to z = 22.
- **d** runs into the store (−x).

## Front
- **Steven (Oct 7):** the sign is the all-caps lit WOOLWORTH on a dark fascia with cream piers (refs/woolworth-front.png), not the mixed-case video frame (refs/woolworth-video.png). The restaurant's own sign is still to come from Steven.
- **Fascia.** Dark maroon-brown across the whole 36 m, 3.0–4.4 m high, standing 0.25 m out. White wall above.
- **Letters.** WOOLWORTH in lit orange-red channel letters straight on the fascia over the middle of the store's opening: 0.78 m capitals, 8.1 m across, the photo's letter widths and spacing with Coustard Black glyphs (OFL; the photo is too soft to trace), dark returns 12 cm deep, a trim cap, and a halo on the fascia. Built by `tools/stores/signs/` (wl_logo.json, channel.gd).
- **Superseded (Oct 7):** the red panel fascia and the white light-box with Roboto Slab letters.
- **The restaurant's front (u 0–9).** A white bulkhead, glass in aluminium frames, a 1.6 m door opening with both leaves held open, and a "Restaurant" plate (red letters on cream) on the fascia.
- **Cream piers** between the restaurant and the store (u 9–9.6) and at the store's far end (u 35.55–36).
- **The store's front (u 9.6–36).** Wide open, with a white soffit, downlights, a clock and an exit sign just inside (video 5:34).

## Inside (walkable)
- **Store.**
  - Glossy off-white vinyl. A red stripe edges the main aisle (u 21–24, straight in from the entrance) and the cross aisle (d 17–20).
  - A white lay-in ceiling at 3.6 m with long rows of troffers 3 m apart.
  - Plain white square columns flank the main aisle.
- **Red band.** White department names on red, high on the left, back and right walls, over white wall shelving: APPAREL, DOMESTICS, HOUSEWARES, TOYS, PARTY GOODS, GREETING CARDS, SCHOOL SUPPLIES.
- **Front end (right of the entrance).**
  - Four checkout lanes running into the store. Each has grey laminate with a red kick stripe, a register, an impulse rack at its head, and a lit lane-number box on a pole (1, 3, 5, 7: video 2:16).
  - Three red carts by the lanes.
- **Customer service (left front corner).** An L counter, a glass upper wall facing the main aisle, and a red-lettered CUSTOMER SERVICE sign (video 2:22).
- **Departments.**
  - Right front: gondolas of health & beauty and candy.
  - Right back: four toy gondolas.
  - Left front: round racks of clothes.
  - Left back: housewares, small appliances and linens.
  - Behind the restaurant: greeting cards and party goods.
- **The restaurant (u 0–9, d 0–14).**
  - **Walls and light.** A warm, dimmer room. Beige walls over a wood-slat wainscot. Lattice wallpaper panels in wood frames, with brass sconces and globe shades. Framed food photos.
  - **Seating.** Five orange-red vinyl booths along the right wall, and white pedestal tables with orange-red chairs.
  - **Counter.** A counter across the back with food-photo panels on its front, a pie case and a register. Behind it, a stainless back bar with a soda fountain, a backlit black menu board and two monitors (video 5:40–6:25).
  - **Ways in.** From the store through a wood-framed opening with red "Restaurant" letters over it (video 7:37–7:49). From the mall through its own door.
- **Not built.** Shoppers and staff, the hanging sale cards, the soda cooler and film display (branded in the video), and a garden center (Steven: none).

## Files
- `prototypes/godot-mall/project/tools/stores/woolworth/store.gd` (geometry, materials `wl_*`) and `paint.py` (textures → `tex/wl/`, plus six stock sheets → `tex/md/`). It uses the media kit (`tools/stores/media/kit.gd`) for wall bays, gondolas and stock.
- Hooks: `tools/build_mall.gd` (dispatch, `BUILT_RECTS`, `wl_` materials) and `tools/open_interiors.py` (s13).
