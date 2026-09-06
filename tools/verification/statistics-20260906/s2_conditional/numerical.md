# S2 conditional probability numerical checks

Checked in the rendered page with headless Chrome on 2026-09-06.

- Default counts `(A∩B, A∩Bᶜ, Aᶜ∩B, Aᶜ∩Bᶜ) = (8, 2, 10, 80)` give `P(A)=10/100=0.100`, `P(B)=18/100=0.180`, `P(A|B)=8/18=0.444`, and `P(B|A)=8/10=0.800`.
- Setting every count to zero renders both conditional probabilities as `未定義（分母為 0）` and displays the zero-denominator explanation.
- Entering `-7` for the first cell is normalized back to visible input value `0` before computation.
- No browser `pageerror` was emitted.
