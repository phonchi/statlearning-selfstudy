# Chapter 12: current lecture/Lab alignment

Sources: current nsysu-math524 lecture PDF and Chinese Lab; immutable source SHA-256 in source-hashes.json. Page text and annotations were extracted directly with PyMuPDF. Every source page has a section/anchor assignment in page-coverage.json; title/appendix-only pages are structural, not independent substantive teaching topics.

The existing rich mathematical details remain; this change supplies connected intuition, assumptions, notation checks, the actual Lab workflow, and linked-topic explanation. topic-coverage.json lists the expanded details. Source URLs and their actual retrieval outcomes, including blocked originals and replacements, are in link-disposition.json. HTTP success alone does not validate content identity: the older TDS clustering URL redirects to an unrelated time-series article and is explicitly marked unusable as the original.

Original Lab excerpts are drawn through lab_code; no source PDF/notebook or cached source code was edited. validation.json records exact quoted-cell parity, source/HTML parity and augment idempotence. independent-math-verification.json records recomputation. Random data used for mathematical identity checks are internal only and not added to teaching pages.

The live m524 conda environment is Python 3.11.15 / sklearn 1.6.1. New explanatory API links use version 1.6 where practicable. There are no newly invented runnable classroom examples in these chapters.

Validation: tools/validate.py --page unsupervised_learning passed with no failures. Ch12 exceeds the advisory SIZE threshold; no substantive content was removed to satisfy a size quota. Browser rendering and deployment verification are performed by the root agent across all six chapters.

Important correctness refinements: MAR is not a guarantee of unbiased low-rank imputation; complete linkage can be affected by outliers; Gaussian mixture does not inherently reject noise; t-SNE uses global Q normalization and negative-gradient updates; source and reconstructed-data numerical summaries are distinguished.
