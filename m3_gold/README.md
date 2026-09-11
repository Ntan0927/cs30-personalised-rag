# M3 Gold Evidence v0.1

This directory contains the local contract for W5 M3 Gold Evidence annotation.

## Files

- `gold_v0_1.jsonl`: final M3 Gold v0.1 JSONL for this W5 package.
- `gold_v0_1.schema.json`: JSON Schema for one JSONL record.
- `candidate_pool_v0_1.review_labeled.csv`: M3 manual review record for accepted candidates.
- `dev_test_split_plan_v0_1.md`: deterministic proposed Dev/Test split plan.
- `personalisation_candidate_list_v0_1.csv`: provisional M3 personalisation candidate screen.
- `personalisation_candidate_list_v0_1.md`: narrative summary of the personalisation screen.
- `validate_gold.py`: dependency-free validator for schema-adjacent checks and OpenStax char-span audits.

## Record Semantics

`gold_core_evidence_sets` is an OR-of-ANDs:

- Outer list: alternative sufficient evidence paths.
- Inner list: spans that must be jointly retrieved for that path.

`partial_evidence` is related but insufficient evidence. It must not be counted as a complete Gold hit.

`gold_answer` is the option id (`A`, `B`, `C`, or `D`), not the raw answer text. The correct answer text remains in `gold_answer_text`.

In the current local OpenStax parse, each parsed chapter has its own canonical
`text` field while sharing the same `document_id`. Consumers must use
`document_id + chapter_id + char_start + char_end` to replay a span exactly.
Each span also carries `block_id` so M4 can map Gold evidence to chunks without
reconstructing block membership from character offsets alone.

`annotation_status` is `m3_initial` for this package. The
`candidate_pool_v0_1.review_labeled.csv` file records M3's manual accept
decisions, but it is not an independent M2 provenance review.

## First-Step Contract

M1/M8 should be able to load each JSONL object using these stable fields:

- `question_id`
- `source_split`
- `question`
- `options`
- `gold_answer`
- `gold_answer_text`
- `answerable`
- `gold_core_evidence_sets`
- `partial_evidence`
- `question_difficulty`
- `question_type`
- `concept_group`
- `personalisation_eligibility`
- `eligibility_reason`
- `split`
- `corpus_version`
- `parser_version`
- `gold_annotation_version`
- `annotation_status`
- `review_record_id`
- `source`

Run:

```sh
python3 m3_gold/validate_gold.py \
  --corpus-root data/processed/openstax \
  m3_gold/gold_v0_1.jsonl
```

If the parsed OpenStax corpus lives elsewhere, pass that directory with
`--corpus-root` or set `CS30_OPENSTAX_ROOT`. The validator also falls back to a
local `Openstax/` directory when the repository-standard processed corpus path
is not present.
