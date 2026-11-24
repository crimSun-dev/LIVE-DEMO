# Live demo script (draft)

Four runs, all done from the web page (http://127.0.0.1:8000/). **Draft:** check the order and wording against deck slide 9.

**Before class:** `.\run_demo.ps1 -Reset` (this wakes Neon and gives clean data). Confirm the health line says `db=neon fault=none`.
If the venue wifi is dead, use `.\run_demo.ps1 -Offline -Reset` (SQLite + frozen real BMKG sample) or play the backup MP4.

1. **Normal run (I1 → I2 → I3).** Pick an occasion → Recommend. The badge shows **LIVE** with BMKG time, temperature and description,
   and 5 outfits appear. Recommend again: the badge shows **CACHED** ("cache hit") and no new I2 row appears in the interface log.
   Point at rain → rain-ready shoes/outer, hot → no heavy outerwear.
2. **BMKG fails (Ch 9 discontinuity).** Demo controls → fault `timeout` → Set → Recommend. After about 3 s the badge shows
   **CACHED** ("fallback after timeout") and outfits still appear. The interface log shows the failed I2 row (`timeout`).
   Repeat with `http500`, `malformed`, `missing_fields` if there is time.
3. **Cold failure → manual.** Keep a fault on, click "Clear weather cache", Recommend: the badge shows **MANUAL_REQUIRED** and the two-tap
   Rainy/Dry, Hot/Normal prompt appears. Answer it → outfits come back (source **MANUAL**). Set fault back to `none`.
4. **Garment registration (RQ3).** Issue a tag code. Open the public QR link: it shows the product, wishlist only, no ownership.
   Activate the code: the garment is added in its slot. Activate the same code again: "invalid code" (usable once).
   Typing the public serial gives exactly the same error.

**Close:** show `docs/RESULTS.md` (written by `measure.py`) for M1–M5.
