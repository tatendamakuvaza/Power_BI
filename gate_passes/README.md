# Tererai Trent International School — Student Gate Passes

Generates a printable A4 PDF of student gate passes — **4 passes per page** —
for every student who paid something towards their 3rd-term invoice, for both
the Primary and Secondary school registers.

* Output: `Tererai_Trent_Gate_Passes.pdf` (32 passes, 8 pages)
  * Primary: 10 passes (TTIS-P-001 … TTIS-P-010)
  * Secondary: 22 passes (TTIS-S-001 … TTIS-S-022)
* No fees or amounts appear on the passes.
* Passes are valid **12 – 16 October 2026** (edit `VALIDITY` in the script to change).
* Students with no payment recorded in the register are excluded
  (Primary: Obert Ncube, Blessed Mafukidze, Ashwin Ncube, Munenyasha D. Makawa,
  Anika Matinyarare, Valerie Matinyarare, Yusuf Matinyarare;
  Secondary: Godfrey Ncube, Maita Motsi, Valentine Musariri).
* The official school logo (`school-logo.png`, transparent background, derived
  from the original `school-logo-src.jpeg`) is embedded on every pass as-is.

## Regenerate

```bash
pip install reportlab
python3 generate_gate_passes.py
```

Edit the `PRIMARY_PAID` / `SECONDARY_PAID` lists at the top of
`generate_gate_passes.py` to add or remove students, then re-run.

Print on A4, cut along the dashed lines.
