# Regression diagnostics supplement verification — 2026-09-28

Scope: Chapter 3 `linear_regression.html`, generated from
`tools/enrich/enrich_regression.py`. The supplied lecture PDF, notebooks, other
chapters, all JavaScript blocks, baked datasets and existing controls are unchanged.

Eight default-closed disclosures cover WLS, correlation/ACF, the studentized-residual
cutoff, leverage sensitivity, Cook's distance derivation and cutoff, coefficient
compensation under collinearity, and VIF cutoffs. KNN self-inclusion is explained
beside its existing definition. No lecture page numbers or production records are
added to the student-visible content.

`verify.py` checks source/render idempotence, IDs, anchors, disclosure depth, scope
and preserved script bytes, then independently verifies formulas by perturbing and
refitting a full-rank 24-observation regression. Seed 20260928, 4 parameters,
NumPy least squares. All 24 deleted fits agree with the analytic formulas;
maximum Cook identity error is recorded in `math-and-structure.json`.
WLS/transformed-OLS equivalence, coefficient variance/VIF, and KNN inclusion and
leave-one-out exclusion also pass.

`browser.py` verifies every new disclosure at 1440px and 390px, rendered MathJax,
page width, diagnosis controls, and the VIF slider/reset. `shots/` contains every
new disclosure at both widths and the KNN section. Representative images were
visually inspected; long formulas were split into shorter equivalent steps and
lists indented before the final browser run. `browser.json` records final bounds.

`run.log` contains the checks. The existing validator reports no failures and one
size advisory (the chapter is larger than its suggested 300KB limit); there are no
new dependencies, charts, or external assets. Reader contract checks pass.

Method references checked during planning:
- https://www.statsmodels.org/stable/generated/statsmodels.regression.linear_model.WLS.html
- https://www.statsmodels.org/stable/generated/statsmodels.stats.diagnostic.acorr_ljungbox.html
- https://www.itl.nist.gov/div898/software/dataplot/refman1/auxillar/regrdiag.htm
- https://scikit-learn.org/stable/modules/generated/sklearn.neighbors.KNeighborsRegressor.html

These records are for maintenance and are not linked from the teaching page.
