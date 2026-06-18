                                                \\\\\\\\\\\\\\\ update-log.md //////////////
                                                ///////////////               \\\\\\\\\\\\\\

                                    This covers what I fixed, what I added, known issues, and ideas for next stuff.

kwaziko 1.3 (what I did):
- added`pi5 dashboard`
- Restored the missing dashboard in the `github things` copy and synced structure with main `index.html`.
- Added a live clock to the dashboard (`pi5-time`) that updates every second.
- Created this update log `UPDATE_LOG.md` summarizing changes.

Issues Fixed:
- Dashboard tab not showing because of id/label mismatch.
- Dashboard missing in one copy of the site.
- Clock was missing; it's now added and updates every second.

Known Limitations / TODOs:
- Stats are client-side only — `platform`, `deviceMemory`, and `uptime` are browser-based approximations, not real Pi metrics. Add a backend endpoint to get real CPU/memory/uptime if you want accurate monitoring.
- Duplicate element IDs exist across the two copies of the site (`pi5-time`, `pi5-refresh`, etc.). That's fine for separate pages, but consider namespacing if loading both in the same DOM.
- The `startup-screen` overlay may hide content briefly during load/animations; timings can be tuned.
- Visual polish and mobile layout improvements would make the dashboard nicer (charts, colors, responsive tweaks).

Ideas / Next features:
- meny more pi dashboard fetures 
