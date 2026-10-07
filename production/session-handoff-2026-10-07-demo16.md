# Session handoff: Houma Mall Rewind (Oct 7, 2026, afternoon): Demo 16, the mall in two wings

Read this first. Then read `design/godot-wings.md`, which covers how the wings, stand-ins, crossing, export and publish work.

## Live
- **Demo 16:** https://stevenboudreaux.github.io/Southland-Mall-95/prototypes/godot-mall/play/
  - Wing 1 is the default. `?wing=2` opens Wing 2.
  - Commit and pack-size details are below, under Publish.

## Steven's direction this session (Oct 7, ~11:40–11:55)
- **File size:** split the game by wing, not by storefront. The seam is at the east hall / Dillard's court floor change (z = 48). Gumballs belongs to Wing 1, and its court door is also a crossing.
- **Crossing:** Fallout-style prompt; E, controller A, click or tap.
- **Stand-in:** looking across the seam must look exactly like the other wing as it is now, and must stay current. That is now a publish guard.
- **Work style:** no previews and no questions. Make every call and publish.
- **Machine:** work on the MacBook Air only.

## Built (Demo 16)
- **Wing split:** `wing1.tscn` / `wing2.tscn`, with per-wing gen in `gen/w1`, `gen/w2`.
  - Each wing has its own walk grid, so the seam is a wall.
  - Seam prompt and fade (`scripts/player.gd`).
  - Per-wing export: `w1/w2 .desktop/.mobile.pck`.
  - Cache Storage prefetch of the other wing (`web/shell.html`).
  - Stand-ins: the other wing's halls are real geometry; its storefronts are captured pictures (`tools/capture_standin.*`).
  - `tools/wing_hash.sh` stamps the pictures, and `publish_build.sh` refuses stale ones.
  - Multi-job Mac bake plugin. About 7 minutes per bake on the Air.
- **5-7-9:** the pink front from photos 01/04. Polished-steel portal, open front, hot-pink walls, pink risers with mannequins; the oval logo is kept on the white header.
- **Great American Cookie Co.:** black fascia with checker steps at the corners, red neon "Great American" script (Kaushan Script) and white lit "COOKIE CO." (Poppins Black), all 3D.
- **Cucos:** the script traced from Steven's night photo. The small c and o were redrawn because the photo is soft. It is a 3D can with a neon tube round each letter and a soft glow. A blue "MEXICAN CAFE" band below it is slightly backlit. The rest of the front is unchanged.
- **Foot Locker:** a soft red halo behind the letters, and the faces lit a little more.
- **Southland Cinema 4 (front only):** white-painted brick and three bronze arches (box office, doors, doors), with carriage lanterns and silver poster cases.
  - The welcome case has no United Artists logo.
  - The posters are invented films: Bayou Run, Comet Kids, Gulf Breeze, Red Mesa.
  - A dim lobby sits behind the glass.
  - Code: `tools/stores/cinema/`.
- **Champs Sports / Sports Avenue:** shut to walking. Inside are sports stock (`tools/stores/small/sports.gd`): invented-team jerseys, a trainer wall, caps, rounders, ball bins and pennants.
- **Narrowing** (`tools/narrow_stores.py`, run after convert_map / open_interiors):
  - **Lion's Share:** 12 → 9.3 m.
  - **Wicks 'N' Sticks:** 6 → 5 m.
  - **Coming Soon stall:** a new 3.7 m closed stall between those two (cream barricade).
  - **Radio Shack:** 8 → 6.4 m, with a 1.6 m plain wall next to GNC.
  - The hall length is unchanged.
- **Checks:**
  - **Evidence:** `production/qa/evidence/d16-{night,day}-sheet*.jpg` and `d16-seam-*.png`.
  - **Movetest:** 0 errors across 11 cameras per mode.
  - **Seam test:** `tools/qa/seamtest.py` crossed 1→2 by key and 2→1 by clicking the prompt.
  - **Packs:** both load every resource natively (`--main-pack`).
- **Lesson:** never bring the Mac's re-saved `wing<n>.tscn` back. Its resource IDs don't match the cloud files, and the export silently dropped more than 100 meshes. See `design/godot-wings.md`.
- **Review:** a period-art-director pass was done. I applied one finding, the Cucos band reading at night. I declined the rest, with reasons:
  - "foot Locker" with a lowercase f is the real 1995 logo.
  - The poster case pairs a one-sheet with a "coming soon" teaser on purpose.
  - The welcome card's wording is copied from Steven's photo.

## Open / next
- **Grade the new signs and fronts:** 5-7-9, Cookie, Cucos, Foot Locker, the cinema.
- **Seam:** walk it on the iPhone, especially the Gumballs court door, and check the crossing speed with the cache.
- **Mall historian:** was the Coming Soon unit really empty in 1995?
- **Next interiors:** the cinema, then Champs and Sports Avenue (walkable).
- **More narrowing:** Steven said he'd mark up more stores the same way. Add them to `narrow_stores.py`, then rebuild, rebake and recapture.
- **Still owed by Steven (from Demo 15):** JW's facade structure, Franks, Blockbuster signage detail, the Woolworth restaurant sign, K&B's hidden third word.
