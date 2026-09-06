# S3 distributions numerical checks

Checked in the rendered page with headless Chrome on 2026-09-06.

- `Binomial(n=10,p=0.5)`, interval `[3,7]`: rendered probability `0.8906` (exact value `912/1024 = 0.890625`).
- `Uniform(0,8)`, interval `[2,5]`: rendered probability `0.3750`; the SVG contains one exact shaded rectangle and three step-boundary line segments.
- `Normal(0,1)`, reversed inputs `[1,-1]`: inputs are visibly reordered to `[-1,1]`; rendered probability `0.6827`. The status states that the plot window is `mu +/- 4 sigma` while probability uses the complete requested interval.
- Narrow normal interval `[0,0.001]`: the shaded SVG polygon exists with 122 boundary points, so nonzero intervals narrower than the 121-point display curve grid remain visible.
- Out-of-range endpoints `[-999,999]` are visibly clamped and written back as `[-100,100]`.
- Fixed-seed exponential simulation with `n=10` and 160 sample means: empirical mean `1.023`, empirical SD `0.304`, theoretical SD `0.316`.
- No browser `pageerror` was emitted.
