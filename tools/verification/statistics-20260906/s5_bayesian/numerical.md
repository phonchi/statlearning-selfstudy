# S5 numerical checks

- Disease example: 0.90 x 0.01 / (0.90 x 0.01 + 0.05 x 0.99) = 0.1538461538.
- Likelihood ratio example: 0.7^7 x 0.3^3 / 0.5^10 = 2.2769316864.
- `w25betaDensity(x, 1, 1)` at x = 0, 0.5, 1: 1, 1, 1 (floating error below 2e-15).
- `w25betaDensity(0.5, 2, 2)`: 1.5.
- Beta(2,2) + 7 successes + 3 failures: posterior Beta(9,5), mean 0.643, MLE 0.700.
- Zero observations: UI reports MLE as non-unique; posterior equals prior.
- 20 successes and 0 failures: all plotted points remain finite, including p = 0 and p = 1.
