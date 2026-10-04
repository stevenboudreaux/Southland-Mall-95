# Game Brief: Houma Mall Rewind

> **Working title.** "Southland Mall" is kept only to describe the real place; the
> game's name avoids it because the real mall is still open. The start screen badge
> still says "Retro" until a final name is chosen.

**One-sentence pitch:** Walk your hometown mall the way you remember it, in any year from its 1969 opening on, and pin your photos and memories to the exact stores and spots where they happened: a moderated, pre-social-media place where Houma remembers together.

## Core loop
- Pick a year and walk the mall (3D, side or overhead view).
- A storefront or spot jogs a memory; open its board and browse other people's photos.
- Post your own photo with a date and the story behind it; Steven approves it and it joins the board.
- Come back as more photos, more years and more detail arrive.

## Player goal & fail state — what "working" looks like
- A visit feels complete when someone finds a place they remember and either sees a photo that brings a memory back or adds one of their own.
- Testable: a first-time visitor on an iPhone can walk to any store, read its board and submit a photo without help.

## MVP — what must exist to be the game
- Walkable mall with a year picker and period-faithful storefronts.
- A photo board at every storefront. Photos are **viewed only in place**, at the storefront.
- One Santa board (center court, food court area) and one Easter Bunny board (by Franks).
- Moderated visitor posting: submit → Steven reviews → published. Submitter details stay private.
- Steven's editor ("god mode"): post and Publish without review.

## Out of scope — not building this
- Shopping or any commerce gameplay.
- Multiplayer.
- Other malls *for now* — but keep the builder mall-agnostic so other malls could plug in later.
- Unmoderated posting.
- Likes, follower feeds or ranking algorithms. *(Inferred from the vision; confirm or cut.)*

## Build order
1. ✅ (Oct 4) Trust fixes before more beta testers: submitter emails private, Publish stops if it can't re-read the live list, Approve retryable.
2. ✅ (Oct 4) Board correctness: only one Santa and one Easter Bunny poster; old editor storefront photos (stand-in reference art, sometimes from other locations of the same brand) off the boards and out of the counts.
3. Directory kiosks: 3D three-sided kiosks. Side 1: map, year slider and store list that jumps you to a store; posting allowed from here. Side 2: post photos of the mall itself. Side 3: a feedback "mall survey" for beta testers (what they liked, what's wrong, what to add).
4. Module split, toward a full 3D engine.
5. Geometric 3D storefronts, refined from submitted photos taken at different angles.
6. Department store interiors: Dillard's (three floors, two sets of escalators), Sears.
7. Center court as an event space: the gazebo as the Easter Bunny photo spot; boards for expos, spelling bees and school performances. Add years as photos arrive (roughly 1969–2018, never stated as a hard range).

---
**Who it's for / what they feel:** Everyone who grew up with the mall — Boomers and Gen X who spent the most time there, millennial bike-riding "mall kids", and Gen Z and Gen Alpha who are nostalgic for it secondhand. The feeling: recognition, warmth, and community face to face again.

**Art & audio direction:** A period-faithful mall in the pixel look of the early internet, when the web was smaller, kinder and more collaborative.

**Reference game:** None known; nothing quite like this exists yet. *(Add one if it comes to mind.)*
