# @resapass Instagram content guide

Resapass (resapass.co): hotel booking site, 2M+ hotels, net rates from 280+ suppliers plus a flat 10% margin. No subscription, no hidden fees, free cancellation on most rooms, 7/7 support. Audience: travellers worldwide, Europe first. Language: **English**.

## Hard rules
- NEVER invent prices, savings or comparisons for a named hotel or competitor. No "Hotel X: Booking 180 / Resapass 120" unless real, verified figures are supplied in `deals/`.
- The "18% cheaper" claim is always "on average vs major booking sites", with the disclaimer "Average across our price checks vs major booking sites. Not guaranteed on every hotel or date." (stat/bigstat templates include it; captions add an asterisk note).
- Booking-site commissions: say "usually 15 to 25%", never a precise figure for a named company.
- Destination facts must be well-established general knowledge. No made-up openings, events or prices.
- No em dashes. No AI filler ("dive into", "unlock", "elevate", "game-changer", "hidden gem"). One ask per caption. Exactly 3 hashtags.

## Weekly mix (7 posts, one per day, Mon-Sun)
Goal: a visual, photo-led feed. Every carousel opens on a full-bleed photo cover, and there are 2 reels a week.
1. Mon: carousel explaining the model or a booking concept (photo cover)
2. Tue: REEL on a brand angle (rotate: no subscription, flat 10%, free cancellation, 2M+ hotels, 7/7 support)
3. Wed: carousel, list of tips/mistakes, save-worthy (photo cover)
4. Thu: carousel city guide "where to stay, by vibe" (5 neighbourhoods; rotate European cities, never repeat one already in `tools/week-*.json`; photo cover of that city when `photos/` has one)
5. Fri: REEL, mood or travel-tip story (weekend, room, destination)
6. Sat: carousel travel hack (photo cover)
7. Sun: photo post with a question driving comments (`photo` template, question as title)
Text-only templates (manifesto, bigstat, question, cover) are now the exception: use them only when no fitting photo is left.

## Reels (tools/reel.py, called by publish_week.py)
Post: `{"id","date","type":"reel","scenes":[{"image","kicker"?,"title","body"?}, ...],"end":{"title","body"},"caption"}`.
2 to 4 photo scenes (3 is ideal, about 11 s), each with a slow pan/zoom and a short animated title (under ~35 characters) and body (under ~50). The end card is the brand slide with the resapass.co button.
Output: `posts/<date>/reel.mp4` (1080x1920, H.264, silent AAC, 30 fps) and `posts/<date>/cover.jpg`; the daily file has `type: "reel"`, `video_url` (jsDelivr, served as video/mp4), `cover_url`, `caption` (Make route 3). No music is baked in.
Check frames after rendering (ffmpeg -ss <t> -i reel.mp4 -frames:v 1 x.jpg): text readable, nothing under the bottom 400 px.

## Templates (tools/render.py)
cover(kicker,title,sub) · point(n,title,body) · place(n,title,tag,body) · stat(big,title,body) · bigstat(kicker,big,title,body) · manifesto(lines[],title,body) · question(kicker,title,body) · cta(title,body).
Carousels: cover first, cta last, 5 to 9 slides. Titles under ~60 characters, bodies under ~120.
See `tools/week-2026-10-05.json` for the exact JSON format.

## Photo posts
- Photos live in `photos/` (free-licence or Resapass-owned images only; source noted in `photos/SOURCES.md`).
- Template `photo(image, kicker?, title, body)`: full-bleed photo, brand gradient, white text, Resapass logo in the footer. `image` is the file name inside `photos/`.
- Use photos for every carousel cover, the Sunday post and the reels (about 9 to 11 photos a week). Pick photos that match the topic and keep text readable (check the render). Never reuse a photo already used in an earlier week file. Never claim the photo shows a specific hotel unless SOURCES.md says so.

## No gaps
Every calendar day must have a `daily/YYYY-MM-DD.json` file (Make errors on a missing file and can switch itself off). A day with nothing to post uses `"type": "none"`.
