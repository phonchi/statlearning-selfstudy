# Statistical learning / regression / classification / resampling alignment

Source: current course snapshot `/tmp/statlearning-current-course`, commit
`7c215512b38ed57a98d3289d83030c582a03eeb4`. Lecture PDF contents were extracted
with `pdftotext -layout`; the page groups below are internal audit locations,
not student-facing locators. Lab code/output references use the rebuilt current
`data/source_index/lab_ch{2,3,4,5}.md`.

## Coverage by lecture topic

| Lecture / source group | Website sections | Audit result |
|---|---|---|
| Statistical Learning: notation, estimation/prediction/inference, reducible error (2–8) | prologue, irreducible | Existing definitions and conditional mean decomposition retained. |
| Supervised/unsupervised; nearest-neighbor regression; curse of dimensionality (9–15) | parametric, bayes, reference | Existing explanations retained; concept simulations explicitly distinguish their generated data from textbook data. |
| Parametric structure, linear/spline fits, flexibility/interpretability (16–23) | parametric, tradeoff | Existing concept comparisons retained. |
| Training/test MSE; bias/variance and derivation appendix (24–30, 39–41) | mse, biasvar, reference | Fixed reference prose reversing A/B optimal df: A=7, B=2, C=18. Existing finite-test versus expected-risk distinction retained. |
| Bayes classification, conditional probabilities, KNN (31–38) | bayes | Existing model/error comparison retained. |
| Regression: Advertising, least squares, coefficient inference, fit (2–24) | slr, inference, accuracy, mlr | Source-grounded code/output imports pass; existing numerical/geometry content retained. |
| Categorical coding, interactions, nonlinear predictors (25–36) | qualitative, problems | Existing coding and interaction explanations retained. |
| Nonlinearity, correlated errors, heteroscedasticity, outliers, leverage, collinearity (37–52) | problems | Existing diagnostics retained. |
| Linear regression versus KNN; linear model generalizations (53–59) | vsknn, qualitative | Existing concept comparisons retained. |
| Forward/backward/mixed selection (62–65) | mlr | Added actual algorithms, rank restrictions, greedy-search and post-selection limitations. |
| Bootstrap curve intervals (66–67) | inference | Added paired resampling, fixed prediction grid, percentile intervals and pointwise/mean-response limitations. |
| CCPR / partial regression (68) | mlr | Added both definitions separately; FWL slope relation and collinearity limitation. Lecture title uses both terms; they are not mathematically interchangeable. |
| Models as useful approximations; coefficient interpretation/causality (69–70) | mlr | Added conditional-support and observational-causality explanation; quotations are not duplicated. |
| Classification: coding, logistic/MLE, multinomial, Bayes/LDA (2–23) | prologue, logistic, multinomial, lda | Fixed z versus finite-sample t distinction and actual versus pairwise decision boundaries. |
| Fisher / whitening / reduced rank (24–26) | lda#w04fisher | Added Mahalanobis score including priors; W/B definitions; generalized Rayleigh quotient; generalized eigenproblem; W-orthogonality; binary equivalence; rank bound; full versus truncated subspace; singular-W limitation. |
| Iris discriminant example (27–28) | lda#w04fisher | Added class counts, four variables, exact confusion table, eigenvalues and 98% training-only interpretation; independently verified. |
| Default thresholds/ROC, QDA, NB, comparisons, KNN, GLM, appendix | lda, qda, threshold, glm, reference | Existing content and current lab code/output references retained. |
| Resampling motivation and validation split (2–9) | prologue, validation | Validation graph uses OLS with the lab's orthogonal polynomial design; ten fixed split repetitions are a stated illustration of split variability. |
| LOOCV shortcut, K-fold weighting, comparison (10–18) | loocv, kfold, kbias, cvclass | Graph generator now uses exact lab estimator (`sklearn_sm(sm.OLS)`), raw-power design and degrees 1–5. Removed unsupported degree-10 comparison and synchronized reference table. |
| Leakage; shuffling/validation size/time data (19–21) | cvwrong | Added grouped data, temporal ordering, ShuffleSplit overlap and preprocessing boundary. |
| Portfolio bootstrap, SE, percentile CI, curve bands, dependent data, OOB (22–36) | bootstrap | Existing Portfolio examples retained; added interval distinctions and pointwise grid construction. |
| Prediction intervals, Jackknife, bootstrap vs permutation, classifier permutation (38–42) | bootstrap | Added all subjects with assumptions; corrected two-sided permutation-tail interpretation and use of full training/tuning pipeline. |

## Confirmed checks

- `core-source-import.log`: all four enrich modules load all referenced current lab code and saved outputs; all four flashcard files parse and retain front/back schema.
- `check_fisher.py` and `fisher-run.log`: independently recomputed Iris scatter matrices, eigenvalues, W-orthogonality, binary direction equivalence, and full projected classification equality. Confusion matrix `[[50,0,0],[0,48,2],[0,1,49]]`; positive eigenvalues 32.191929198278004 and 0.28539104262306414; W-orthogonality max error 7.77e-16.
- `resampling-frames.js` and `resampling-run.log`: complete regenerated data and log, exit 0. LOOCV `[24.2315,19.2482,19.335,19.4244,19.0332]`; 10-fold `[24.2077,19.1853,19.2763,19.4785,19.1372]`.
- Python AST syntax checks passed on all four enrich sources.
- Added matching Fisher/CCPR/permutation/Jackknife flashcards, plus Fisher conceptual quiz; actual quiz/card functionality retained.

## Integration / limits

The root agent owns page assembly, locator/URL cleanup, shared tooling and browser acceptance. This agent did not mutate generated HTML or rebuild it. **Resampling frames must be refreshed from the saved generated JS, not preserved from old HTML.** Final rendered MathJax/layout/link behavior must be checked during root integration. Existing unaffected numeric simulations were inspected as authored concept simulations, not independently rerun in this bounded task. This ledger establishes topic coverage; it does not claim every linked external reading or every original lecture figure was independently reproduced.

## Follow-up independent reader/provenance review

Reviewed rendered HTML after shared normalization, plus normalized current source fragments.

- Found generic `lab 範例` replacements weakened distinctions between LDA versus logistic fits, Auto import versus indexing examples, and the separately reset variance sample. Rewrote own source prose using actual example/model names, preserving private `src()` cell metadata.
- Found visible `lab 的第 62 格寫著` survived the shared normalizer; replaced with the Portfolio context. Removed regression lecture's obsolete page-count sentence.
- Removed all authored reader-facing cell-parentheticals in these chapters; actual numbers in confusion matrices, years and sample counts retained. The Smarket table's private locator column is correctly removed by shared normalization; all rendered table header/body widths match.
- `check_core_cards.py` checks all code against exact ordered complete code-cell strings (not only the first line), and each displayed saved output against the referenced source outputs. All **40** cards across the four chapters pass; `core-card-provenance.log` preserves every result.
- Corrected an existing unsupported KNN claim that increasing K beyond 3 never improves results; current prose states only the observed K=1/K=3/QDA comparison and comparison with the majority baseline.
- Resampling HTML still contained the old degree-1–10 FRAMES at the start of this independent review; root was notified to perform the required refresh. This is an integration snapshot, not a new generator failure.
- This follow-up performed DOM/text/provenance checks, not an independent screenshot/browser interaction run. Root browser acceptance remains authoritative.
