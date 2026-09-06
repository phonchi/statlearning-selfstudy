# S6 numerical checks

- Correlation example: 3 / sqrt(2 x 14/3) = 0.9819805061.
- `HC.stat.ols([0,1,2,3,4], [1,2,2,4,5])`: intercept 0.80, slope 1.00, RSS 0.80.
- OLS control reports RSS gap 0.00.
- Slider extreme intercept 4, slope 3: all SVG coordinates are finite.
- All five residual squares remain within the 620 by 430 SVG viewBox after dynamic y-domain expansion.
- ANOVA example independently recomputed: SS between 16, SS within 1.5, SS total 17.5, F = 16.
