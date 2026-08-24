# Risk register

Owner: Leader. Reviewed weekly, before the client report.
Status key: `open`, `mitigated`, `closed`.

| # | Risk | Impact if it lands | Likelihood | Mitigation | Owner | Status |
|---|---|---|---|---|---|---|
| R1 | The supervisor-provided corpus has not arrived and its form is unknown (PDF, slides, web pages, Q&A, language, size, structure) | Parser, chunking strategy, and embedding choice may all need rework; week 1 work becomes throwaway | High | ADR-0001 treats OpenStax as an explicit temporary fixture; contracts are corpus-agnostic; ask the supervisor for a sample this week | Leader | open |
| R2 | GPU and model access unconfirmed | Blocks real embeddings, index building, and every multi-model comparison the brief requires | High | Fixture path keeps all other work unblocked; confirm access before week 2 planning | Leader | open |
| R3 | Contract v1.0 does not model non-text content (formulas, figures, tables) | If the real corpus is formula- and figure-heavy, `Chunk` needs an asset model and everything downstream regenerates | Medium | Decide only after the corpus is known; `Chunk.metadata` can record occurrences now at no contract cost — see §Non-text content below | Leader + M2/M4 | open |
| R4 | Fixture demo output is mistaken for real system performance | Client draws false conclusions about retrieval or model quality | Medium | `PipelineRun.mode`, a stderr banner, and CI enforce it; the client report must repeat the caveat verbatim | Leader + M8 | mitigated |
| R5 | OpenStax parsing quality: headers, footers, hyphenation, cross-page text, formulas | Broken char spans destroy traceability, the project's core selling point | Medium | Contract enforces `len(text) == char_end - char_start`; M2 keeps a known-issues list and hand-checks 10+ passages | M2 | mitigated |
| R6 | Week 1 demo questions get cited as a formal evaluation set | Invalidates every later claim in the report | Medium | Named "demo questions" everywhere; ADR and README state week 1 reports no metrics | M3 + Leader | mitigated |
| R7 | No dependency lock file | Environments drift; "works on my machine" during the client demo | Medium | CI tests 3.11/3.12/3.13 in editable mode and runs a separate non-editable smoke test outside the checkout; add a lock file in week 2 | M8 | open |
| R8 | All commits go straight to `main`, contradicting the repository's own rule | Contract changes land without review; integration conflicts surface late | Medium | Enable branch protection on `main`; CODEOWNERS already routes contract changes to the Leader | Leader | open |
| R9 | Personalisation stays "one extra prompt line" | The distinguishing contribution collapses into a baseline; the report has nothing to compare | Medium | `StudentProfile` already carries `topic_levels` and `confidence`; design the evaluation of personalisation before building more of it | Leader + M7 | open |

## Non-text content (R3), in more detail

Character spans are offsets into one linear text string. A figure or a formula
has no natural offset unless it is represented *in* that string. Two options,
to be decided once the real corpus is known:

- **Placeholder in text (preferred).** The parser emits a marker such as
  `[[FIGURE:fig_3_2]]`, or inline LaTeX, inside `OpenStaxDocument.text`. Char
  spans keep working unchanged, chunks keep their surrounding context, and the
  caption or LaTeX is retrievable text.
- **Separate asset list.** `Chunk` gains `assets: list[ChunkAsset]` carrying
  modality, storage URI, caption, and LaTeX. Cleaner separation, but the link
  between a figure and its paragraph must then be maintained by hand.

In practice these combine: a placeholder keeps the span intact, and the asset
list holds the real resource. **Week 1 needs neither.** The division of labour
asks member 2 only to *record* formula, table, and figure problems, and the
week 1 acceptance bar is text-only chunks. Until the corpus is known, record
occurrences in `Chunk.metadata` (string values only, e.g.
`{"has_figure": "true", "figure_ref": "3.2"}`) and leave the contract alone.
