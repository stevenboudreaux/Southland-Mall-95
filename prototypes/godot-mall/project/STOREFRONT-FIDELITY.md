# Storefront fidelity and the accuracy meter (draft, Oct 4 2026)

Steven's priority after the whole mall: storefronts and signage built store by
store from real photos, with a meter that says how well each one is sourced.
This is a draft of how that would work in the Godot mall. Nothing here is built yet.

## 1. A facade description per store

Each store gets a small record, separate from the map data, that the builder
reads instead of the generic storefront:

```json
{
  "store": "WOOLWORTH",
  "years": [1991, 1996],
  "sign": {"text": "Woolworth", "style": "channel letters", "font": "serif",
           "color": "#f6d25a", "backing": "#b3131b", "lit": true, "image": "signs/woolworth.png"},
  "front": {"type": "glass", "door": "double, centre", "door_width_m": 3.0,
            "bulkhead": "#efe6d3", "pilasters": "stone base", "mullions": "bronze"},
  "depth": {"recessed_entry_m": 1.2, "sign_projection_m": 0.15},
  "interior": "variety store: aisles, red price signs",
  "sources": [
    {"photo": "photos/woolworth/abc123.jpg", "year": 1993, "angle": "straight", "shows": ["sign", "front"]},
    {"photo": "photos/woolworth/def456.jpg", "year": 1995, "angle": "left 30deg", "shows": ["front", "depth"]}
  ],
  "confirmed_by": ["Steven"]
}
```

Photos come from the existing photo boards (photos.json), so anything visitors
submit and Steven approves can become a source.

## 2. The accuracy meter

Scored from the `sources` list, not from how the model looks:

| Level | Needs | What it lets us build |
|---|---|---|
| 0 Placeholder | name and colours from the map | generic front, plain lettering |
| 1 Sign-accurate | a readable photo of the sign from that era | the real sign: lettering, colours, lit or not |
| 2 Facade-accurate | a straight-on photo of the whole front | door position, glass layout, materials, bulkhead |
| 3 Depth-accurate | at least one angled photo | recessed entry, sign projection, columns, returns |
| 4 Verified | a dated photo plus a second person's confirmation | locked for that year |

Each year map scores separately: a 1995 photo doesn't verify the 1991 front.

## 3. Where it shows

- Owner editor: a coloured badge on each storefront (grey, bronze, silver, gold, green).
- A "most wanted" list: stores sorted by traffic or memory value with the lowest
  scores first, saying exactly what photo would raise each one ("a straight-on
  photo of Kay-Bee Toys, any year 1990-1996"). This doubles as a public wish list.
- In the mall (optional): a small plaque at each storefront for visitors.

## 4. How a store moves up a level

1. Steven (or a visitor) adds photos at the storefront, as today.
2. Claude reads the photos, fills in the facade record, and rebuilds that store only.
3. Steven compares the render with the photo side by side and confirms or corrects.
4. The meter updates from the record; only the zone around that store is re-baked.
