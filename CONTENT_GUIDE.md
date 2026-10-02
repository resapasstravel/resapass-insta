# @resapass Instagram content guide

Resapass (resapass.co): hotel booking site, 2M+ hotels, net rates from 280+ suppliers plus a flat 10% margin. No subscription, no hidden fees, free cancellation on most rooms, 7/7 support. Audience: travellers worldwide, Europe first. Language: **English**.

## Hard rules
- NEVER invent prices, savings or comparisons for a named hotel or competitor. No "Hotel X: Booking 180 / Resapass 120" unless real, verified figures are supplied in `deals/`.
- The "18% cheaper" claim is always "on average vs major booking sites", with the disclaimer "Average across our price checks vs major booking sites. Not guaranteed on every hotel or date." (stat/bigstat templates include it; captions add an asterisk note).
- Booking-site commissions: say "usually 15 to 25%", never a precise figure for a named company.
- Destination facts must be well-established general knowledge. No made-up openings, events or prices.
- No em dashes. No AI filler ("dive into", "unlock", "elevate", "game-changer", "hidden gem"). One ask per caption. Exactly 3 hashtags.

## Weekly mix (7 posts, one per day, Mon-Sun)
1. Mon: carousel explaining the model or a booking concept
2. Tue: single, bigstat or manifesto (rotate angles: no subscription, flat 10%, free cancellation, 2M+ hotels, 7/7 support)
3. Wed: carousel, list of tips/mistakes (save-worthy)
4. Thu: carousel city guide "where to stay, by vibe" (5 neighbourhoods; rotate European cities, never repeat one already in `tools/week-*.json`)
5. Fri: single, manifesto or bigstat
6. Sat: carousel travel hack
7. Sun: single question post driving comments

## Templates (tools/render.py)
cover(kicker,title,sub) · point(n,title,body) · place(n,title,tag,body) · stat(big,title,body) · bigstat(kicker,big,title,body) · manifesto(lines[],title,body) · question(kicker,title,body) · cta(title,body).
Carousels: cover first, cta last, 5 to 9 slides. Titles under ~60 characters, bodies under ~120.
See `tools/week-2026-10-05.json` for the exact JSON format.
