# CS-30 System Architecture and Literature Mapping

**Project:** Personalised AI Learning Assistant using Retrieval-Augmented Generation and Large Language Models
**Version:** v1.3 (architecture freeze candidate, self-contained)
**Date:** 2026-08-23
**Status:** Not frozen. All items marked P0 in §9 must be resolved before freezing.
**Chinese source:** `系统架构与文献映射.md`

> This document is self-contained; no other file is required to read it.

---

## 0. Revision History

### 0.1 Changes in v1.3

| # | Change |
|---|---|
| 1 | **Layer B (learner profile) design merged into this file** as §4. This document no longer depends on the separate profile design document |
| 2 | Profile schema gains an explicit `global_level` field, consistent with the frozen matrix in §7.1 using a global level |
| 3 | Specified that `level: unknown` yields `λ_eff = 0`, automatically disabling personalisation |
| 4 | Added §4.6 **Educational Equity and Escape Hatches** (absent from the original design) |
| 5 | Former §4–§8 renumbered to §5–§9 |

### 0.2 Changes in v1.2

| # | Change | Type |
|---|---|---|
| 1 | **Removed `gold` from abstention inputs**; all signals are now available at inference time | Label-leakage fix |
| 2 | Split "automatic correctness" into **Answer-choice Accuracy / Explanation Correctness / Groundedness** | Definition fix |
| 3 | **Froze the experimental matrix** with exact call counts and human-evaluation volumes | Consistency fix |
| 4 | Scoring formula now uses `λ_eff` directly | Implementation clarity |
| 5 | Added **re-scoring rule for KG-expanded candidates** | Gap fill |
| 6 | Tightened three literature claims (gold evidence / BERTScore / EduAdapt) | Avoids over-claiming |
| 7 | Flagged the Unanswerable-set construction logic as pending | Known defect |

---

## 1. End-to-End Pipeline

```text
[A0. DATASET PREPARATION]
  OpenStax textbooks                   SciQ question bank
      |                                    |
  select textbook + version            subject classification
      |                                    |
  parse / clean / chapterise           match to OpenStax chapters
  keep source, page, char_start/end         |
      |                                Evidence Alignment
      |                                (support -> OpenStax char span)
      |                                     |
      |                          +----------+----------+
      |                     support aligned      support unaligned
      |                          |                     |
      |                    Answerable Set       [!] see §3.1 pending note
      |                          |
      |                 chapter / concept-group isolation
      |                 Dev / Test  (random splitting prohibited)
      |
[A. OFFLINE KNOWLEDGE BASE]
  A1 Chunking
      |
  A2 Topic / chapter metadata injection
      |
  A3 Evidence Role annotation (6 classes, project-defined taxonomy)
      |
  +----------+-----------+--------------------+
  A4 BM25    A5 Dense    A6 Restricted KG

[B. LEARNER PROFILE]  full design in §4
  B1 Level input
     |- Option B: self-selected (default)
     |- Option A: transcript (optional, requires authorisation)
      |
  B2 Proficiency Estimator --> profile
      ^                        (global_level + optional topic-level + confidence)
  B3 Profile Update <-- Mini Quiz       |
                                        |
[C. ONLINE QUESTION ANSWERING]          |
  Student question                      |
      |                                 |
  C1 Query processing (coreference resolution / rewriting, optional)
      |
  C2 Hybrid Retrieval: BM25 + Dense -> RRF fusion
      |
  C2.5 Topic Resolution  <- from chapter/topic metadata of Top-K hits
      |    confidence sufficient -> read that topic's level ----+
      |    confidence low        -> fall back to global/neutral-+
      |                                                        |
  C3 KG Expansion (cross-topic / multi-hop only)               |
      |   new candidates re-scored by BM25/Dense -> RRF        |
      |                                                        |
  C4 Level-Aware Reranking <----------------------------------+
      |
  C5 Calibrated Abstention (multi-signal, all inference-time)
      |
  C6 Personalised Prompt <-- profile
      |
  C7 LLM Generation (fixed JSON output schema)
      |
  C8 Citation Integrity Check (string matching, zero LLM cost at runtime)
      |
  Grounded Answer + Verifiable Sources

[D. EVALUATION]
  D1 Retrieval        Hit@K / Recall@K / MRR against aligned gold spans
  D2 Answer           Answer-choice Accuracy (full set, automatic)
                      Explanation Correctness (human sample)
                      Six-dimension blind rating (human sample)
  D3 Level fit        Readability metrics (full set) + blind rating (sample)
  D4 Hallucination    Axis A / Axis B, atomic claim verification (sample)
  D5 Abstention       Abstention Accuracy + False Abstention Rate
  D6 Longitudinal     LLM student simulator (exploratory only)
```

---

## 2. Modules, Provenance and Optimisations

| Module | Architectural source | What is adopted | This project's optimisation |
|---|---|---|---|
| **A0** Dataset preparation | — | Project-defined | Evidence Alignment; **chapter-level Dev/Test isolation to prevent leakage** |
| **A1** Chunking | — | No prior work publishes details | Retain char-level source spans so 300- and 500-token chunkings share one gold-truth set |
| **A2** Topic metadata | — | Project-defined | Chapter hierarchy written into each chunk, consumed by C2.5 |
| **A3** Evidence Role | Inspired by PersonaRAG-type work | The premise that personalising retrieval requires evidence to carry filterable attributes | **Project-defined taxonomy**; pilot annotation before freezing |
| **A4–A5** BM25 + Dense | **Lewis et al. 2020** | The retrieve-then-generate backbone | Lewis is dense-only; we add BM25 and **RRF fusion** |
| **A6** Restricted KG | **KG-RAG (Dong et al.)** | Concept extraction and relation-graph construction | The original builds a full KG; we build a **restricted KG with routing** |
| **B1** Level input | **LPITutor** + **PRAG-EDU** | LPITutor's learner level input; PRAG-EDU's transcript entry point | Both entry points coexist; the transcript path can be disabled without touching the core |
| **B2** Proficiency Estimator | **PRAG-EDU** | Transparent rule-based weighted estimator (no black-box classifier) | `confidence` must propagate downstream |
| **B3** Profile Update | **TutorLLM** | The architectural position of the knowledge-tracing loop | Mini Quiz replaces BERT-based KT — no learner response sequences are available |
| **C1** Query processing | — | Project-defined | Multi-turn coreference resolution; disabled for single-turn evaluation |
| **C2** Hybrid Retrieval | **Lewis et al. 2020** | Retrieval backbone | RRF fusion: BM25 for terminology, dense for paraphrase |
| **C2.5** Topic Resolution | — | Project-defined | Moved after retrieval, driven by existing metadata rather than a pre-retrieval black-box classifier |
| **C3** KG Expansion | **KG-RAG (Dong et al.)** | Post-retrieval concept-neighbour expansion | Adds routing; **all candidates re-scored uniformly**, no separate KG score |
| **C4** Level-Aware Reranking | Inspired by PersonaRAG-type work | The claim that personalisation should enter the retrieval stage | Normalised single-knob `λ_eff` with soft weighting — **designed by this project** |
| **C5** Calibrated Abstention | — | Absent from all three educational RAG comparators | Multi-signal calibration; **all inputs available at inference time** |
| **C6** Personalised Prompt | **LPITutor** + **PRAG-EDU** | LPITutor's prompt structure; PRAG-EDU's complexity-calibration signal | One level drives both C4 and C6 |
| **C7** Generation | **Lewis et al. 2020** | — | Low temperature (0–0.3), grounding constraint, fixed JSON output |
| **C8** Citation Integrity | **DeepTutor** | Citation-grounded output format | String-matching implementation; **not equivalent to support verification**, which belongs to D4 |
| **D1** Retrieval metrics | — | See §5 for claim boundaries | char-level gold spans bound to the course corpus |
| **D2** Answer evaluation | **LPITutor** | Six-dimension rating scale | Three-way split per §3.2; inter-annotator agreement added |
| **D3** Level fit | **EduAdapt** + **PRAG-EDU** | EduAdapt's grade-aware rubric (requires mapping, see §8) | Readability metrics plus blind rating, dual track |
| **D4** Hallucination | **Ji et al. 2023** | intrinsic / extrinsic distinction | Axis A against retrieved evidence, Axis B against the whole corpus; atomic claims annotated on a sample |
| **D5** Abstention metrics | — | Project-defined | Accuracy and false-abstention rate **must be reported together** |
| **D6** Student simulator | **DeepTutor** | LLM student simulator for interactive evaluation | Calibrated against a human-rated subset; **exploratory result only** |

---

## 3. Retrieval and Generation: Implementation Details

### 3.1 A0: OpenStax and SciQ Preparation

**Pending confirmation (P0).** The official project description specifies a supervisor-provided dataset in a higher-education setting, whereas SciQ consists of crowdsourced school-level multiple-choice science questions. Substituting public data is a scope change and requires supervisor approval.

**OpenStax side**

1. Select the textbook and record its **version number** (editions change)
2. Parse, clean and chapterise; retain `source / page / char_start / char_end`
3. Record `parser_version` and `document_hash` to guard against character-offset drift

**SciQ side**

1. Subject classification (SciQ carries no subject labels)
2. Match questions to OpenStax chapters
3. **Evidence Alignment**: locate each SciQ `support` passage as a char span in the OpenStax corpus
   - Method: embedding similarity for coarse location, fuzzy string matching for precise boundaries
   - **A subset of alignments must be manually verified** — misalignment invalidates every D1 figure
4. **Isolate Dev and Test by chapter or concept group; random splitting is prohibited.** Questions drawn from the same chapter are highly correlated, and random splitting causes content leakage.

> **[!] Pending fix (not applied in this version): the Unanswerable-set construction is unsound.**
>
> The current flow treats "support could not be aligned" as equivalent to "unanswerable". That inference does not hold. Alignment can fail because SciQ used an earlier OpenStax edition, because the support came from a different textbook, because the wording was paraphrased, or because the matching algorithm failed. **The absence of the original support passage does not mean the knowledge base cannot answer the question**, and SciQ questions are not sourced from a single OpenStax textbook.
>
> The correct flow is: unaligned support → `Unresolved Pool` → search the entire OpenStax knowledge base → manual confirmation → if evidence exists, reclassify as Answerable; only if no evidence exists does it become `Verified Unanswerable`. Only `Verified Unanswerable` items may enter D5.
>
> Deferred by team decision; **must be corrected before freezing.**

### 3.2 D2: Three-Way Split and Fixed Output Schema

SciQ is multiple choice, so a correct option is available. But **selecting the right option does not mean the explanation is correct**:

```text
final_choice: B                 <- correct
explanation: flawed reasoning   <- still defective
```

D2 is therefore split into three layers with different evaluation methods and costs:

| Layer | Method | Coverage |
|---|---|---|
| **Answer-choice Accuracy** | Automatic comparison against the SciQ key | **Full set** |
| **Explanation Correctness** | Human sample, or claim-level assessment | Stratified sample |
| **Groundedness** | Delegated to D4 support verification | Stratified sample |

C7's output schema is fixed accordingly:

```json
{
  "final_choice": "B",
  "explanation": "...",
  "citations": ["chunk_17", "chunk_22"]
}
```

The fixed schema also allows C8 to be implemented purely by string matching.

**Note:** the ambiguous phrase "automatic correctness" must not appear anywhere in the report; write **Answer-choice Accuracy**.

### 3.3 A3 Evidence Role: A Project-Defined Taxonomy, Piloted Before Freezing

Six classes forming a 2-2-2 gradient:

```text
Beginner      -> definition,  example
Intermediate  -> comparison,  application
Advanced      -> derivation,  boundary
```

**Wording for the report:**

> We define a pedagogical evidence-role taxonomy informed by Bloom's taxonomy and by the structure of educational content.

It must not be presented as an established, theoretically validated scheme — the six roles do not map cleanly onto Anderson and Krathwohl's knowledge dimensions.

**Mandatory pilot before freezing:**

1. Pilot-annotate 100–200 chunks
2. Check for severe class imbalance
3. **Specifically test whether `comparison` and `application` are frequently confused**
4. Double-annotate 20%; report Cohen's κ or Krippendorff's α
5. If agreement is inadequate, revise the definitions and re-pilot
6. Only then freeze, and proceed to corpus-wide LLM annotation with a human-verified subset

Evaluation uses per-role precision / recall / F1 plus macro-F1 and micro-F1; accuracy alone is inadequate given class imbalance and multi-label assignment.

### 3.4 C4 Level-Aware Reranking Score

The original design was additive, but BM25 scores are unbounded while dense cosine similarity lies in [0, 1], so an identical weight differs by an order of magnitude between the two. The corrected form is a normalised single knob that **uses `λ_eff` directly in the main formula**:

```text
λ_eff = λ × confidence

final = (1 − λ_eff) · norm(retrieval_score)
      + λ_eff · role_match(level)
```

1. `λ = 0` disables retrieval-side personalisation, so the on/off switch is a value of a single parameter
2. Sweeping λ yields a dose-response curve, a stronger result than a binary comparison
3. `confidence` enters the main formula directly, so implementers cannot overlook it
4. **When `level` is `unknown`, `confidence` is recorded as 0, hence `λ_eff = 0`** and the system falls back to neutral ranking without a special-case branch

Soft weighting is the primary method; hard filtering is retained as an ablation.

### 3.5 Scoring KG-Expanded Candidates

KG neighbour expansion introduces candidates that initial retrieval did not return. Assigning them a separate KG score would reproduce the scale problem of §3.4 and would be difficult to calibrate.

**Uniform rule:**

```text
KG expansion produces new candidates
-> all candidates (original + new) re-scored by BM25 / Dense
-> RRF fusion
-> C4 Level-Aware Reranking
```

No new score scale is introduced, and the KG's role is confined to **enlarging the candidate pool** rather than directly manipulating the ranking.

### 3.6 C2.5 Topic Resolution: Moved After Retrieval

The original design ran a question-topic classifier **before** retrieval; an early revision removed it outright, which left the topic-level profile unreadable by C4. Topic is now resolved **after** retrieval from existing metadata:

```text
Question
-> C2 Hybrid Retrieval
-> read chapter / topic metadata of the Top-K hits
-> vote or weight to obtain the current topic and its confidence
   |- confidence sufficient -> read that topic's level
   |- confidence low        -> fall back to global level or neutral (no personalisation)
-> C4 Level-Aware Reranking
```

Advantages over a pre-retrieval classifier: it consumes metadata that already exists rather than training a new black box, and it has an explicit degradation path on failure.

**Two costs must be stated in the report:**

1. C4 now depends on C2's retrieval quality — poor retrieval yields poor topic resolution, applying personalisation at the wrong level
2. The "sufficient confidence" threshold is a new parameter and must be calibrated on Dev

**The main experiment uses a single global level** (see §4.5 and §7.1), with topic-level treated as an extension so that this coupling does not enter the primary comparison.

### 3.7 C5 Calibrated Abstention: Inference-Time Signals Only

**Critical constraint.** `gold` may be used only to **calibrate** the rule and to **evaluate** its output. It must never be a test-time feature: at run time the system cannot know whether it has hit gold evidence, and using it as an input constitutes label leakage.

Input signals:

```text
normalised top-1 score
top-1 minus top-2 margin
agreement between BM25 and dense result sets
Topic Resolution confidence
whether Top-K evidence spans multiple mutually supporting chunks
semantic coverage of the question by the evidence
        |
   abstain / answer
```

The margin signal matters particularly: a high top-1 with a close top-2 indicates ambiguity, whereas a high top-1 with a clear lead indicates a confident hit.

Legitimate uses of gold evidence are limited to:

```text
calibrating the abstention rule on Dev
evaluating abstention outcomes on Test
```

**BM25, dense and hybrid configurations must be calibrated separately; thresholds cannot be shared** (different score scales — the same reasoning as §3.4).

Metrics must be reported in pairs: Abstention Accuracy together with False Abstention Rate. Reporting only the former would reward a system that abstains on everything.

### 3.8 Index Selection

At this project's expected corpus scale (thousands to tens of thousands of chunks):

- **Use exact search** (e.g. FAISS `IndexFlatIP`) rather than approximate HNSW / IVF indexes
- Exact search incurs no recall loss, removes a set of tunable parameters (`M`, `ef_search`), and removes one confound from the report
- Reference scale: 7,000 chunks × 1,024 dimensions ≈ 29 MB; a brute-force query takes a few milliseconds
- Approximate indexes become necessary only at million-scale corpora, at which point metadata filtering (chapter or topic pre-filtering) should be added

### 3.9 Two Dense-Specific Pitfalls

1. **Query instruction prefix.** The bge family requires a fixed prefix on the query side, and Qwen3-Embedding has an equivalent instruct format. Omitting it causes a marked drop in performance. If an embedding model performs catastrophically in the fail-fast pilot, check this before drawing conclusions.
2. **API data governance.** If course material may not be sent to third-party services, dense retrieval must run locally, which turns a GPU from desirable into a hard requirement.

---

## 4. Layer B: Learner Profile Design

Two initialisation entry points exist. They differ only at initialisation; both produce the same profile object, after which the entire Layer C pipeline is shared.

### 4.1 Unified Profile Schema

```yaml
student_profile:
  student_id: anonymous_or_internal_id

  # global level, used by the main experiment
  global_level: intermediate
  global_confidence: 0.70
  global_source: self_report

  # per-topic levels, used by the extension experiment
  topics:
    programming:
      level: advanced
      confidence: 0.86
      source: transcript
      last_updated: 2026-08-23
    statistics:
      level: beginner
      confidence: 0.70
      source: self_report
      last_updated: 2026-08-23

  learning_goal: exam_preparation
```

| Field | Values | Notes |
|---|---|---|
| `level` | `beginner` / `intermediate` / `advanced` / `unknown` | Consumed by both C4 and C6 |
| `confidence` | 0–1 | **Feeds directly into C4's `λ_eff = λ × confidence`** |
| `source` | `transcript` / `self_report` / `diagnostic` / `interaction` | Used by the profile-source comparison experiment |
| `last_updated` | date | Written by B3 |
| `learning_goal` | see §4.2 | Affects the C6 prompt only, never C4 ranking |

**The `unknown` rule.** When information about a topic is insufficient, set it to `unknown` and let the student or a diagnostic quiz supply it — **never infer it**. `unknown` corresponds to `confidence = 0` and therefore `λ_eff = 0`, so the system automatically falls back to neutral ranking; no extra branch is needed in code.

**Relationship between `global_level` and `topics`.** The main experiment reads only `global_level` (see §4.5). `topics` is read only in the C2.5 topic-level extension experiment, and C2.5 falls back to `global_level` when its confidence is low.

### 4.2 Option B: Self-Selected Level (Default Entry Point)

Requires no real grades, is cheap to implement, carries low privacy risk, and is easier to use in reproducible research. **This is the default.**

```text
First use
    |
select level (global, or per topic)
    |
select learning goal
    |
(optional) Diagnostic Quiz
    |
Initial Profile
```

**Two granularities of level selection**

Minimal version — a single global level:

```text
Beginner / Intermediate / Advanced
```

Extended version — per topic:

```text
Programming       Advanced
Mathematics       Intermediate
Statistics        Beginner
Machine Learning  Intermediate
Deep Learning     Beginner
```

**Learning goals** (enter the C6 prompt only; they play no part in C4 ranking):

- Understand a concept quickly
- Prepare for an examination
- Learn practical applications
- Understand the mathematical derivation

**Diagnostic Quiz — demoted to demo-only**

The original design included a 5–10 item diagnostic quiz to calibrate self-assessment. This architecture **demotes it to a demonstration feature with no validity argument**, for three reasons:

1. It requires a fourth independent question set (Dev / Test / Smoke / Diagnostic), which is expensive to construct
2. From a psychometric standpoint, estimating a proficiency band from 5–10 items carries a large standard error, so its validity would itself need to be argued
3. **The main experiment uses fixed synthetic profiles (§4.5), so the diagnostic quiz contributes nothing to it**

If retained as a demo feature, two constraints are non-negotiable:

- Diagnostic items **must not come from the formal Test set**
- The diagnostic process **must not create evaluation leakage**

Confidence conventions:

```text
self-selection only          -> confidence ≈ 0.60,  source = self_report
self-selection + diagnostic  -> confidence ≈ 0.80,  source = self_report + diagnostic
```

**The system must never override the student's own selection.** Where the diagnostic result disagrees, it may only advise and let the student confirm:

> You selected Advanced, but the diagnostic result is closer to Intermediate. Adopt the suggested level?

**Risks of Option B**

- Students may over- or under-estimate their own level
- A single global level cannot express variation across topics
- An overly short diagnostic produces unstable estimates
- Diagnostic items overlapping the evaluation set would cause leakage

### 4.3 Option A: Transcript / Academic Profile (Optional Entry Point)

**Status: demoted to an optional feature. Not the default, and not recommended as a target for significant effort.**

Two reasons, the second decisive:

1. Real grades are sensitive personal information and the path is blocked by ethics approval
2. **PRAG-EDU (Computer Applications in Engineering Education, January 2026) has already published the same idea** — using historical module grades as a pedagogical signal to calibrate response complexity, together with a 250-item expert-validated benchmark. Repeating it would at best constitute replication; the novelty claim does not hold

**Preconditions for enabling (all must hold; otherwise fall back to Option B)**

- The client confirms transcripts are genuinely required
- The student gives explicit authorisation
- Privacy and ethics requirements are confirmed
- Access, retention period and deletion procedure are documented
- Raw transcripts are not sent to third-party LLM or embedding APIs without permission

**Flow**

```text
Transcript / Academic Profile
        |
authorisation, privacy and ethics check
        |
minimal field extraction (course name, grade, completion date)
        |
course -> topic mapping
        |
grade normalisation and weighting
        |
Topic Proficiency Score
        |
Beginner / Intermediate / Advanced
        |
write to profile (source = transcript)
```

**Course-to-topic mapping**

Use a transparent rule-based weighted estimator. **Do not train a black-box classifier in the absence of training data and human labels.**

```text
COMP1001 -> Programming: 0.8
         -> Algorithms:  0.2

DATA1001 -> Statistics:   0.6
         -> Data Science: 0.4
```

```text
Topic Score =
Σ (normalised course grade × course-to-topic weight)
÷
Σ (course-to-topic weight)
```

**Thresholds — resolve grading-scale normalisation first**

The original design gives thresholds that assume a percentage scale:

```text
0–49   -> Beginner
50–79  -> Intermediate
80–100 -> Advanced
```

> **[!] These thresholds hold only on a percentage scale.** They fail immediately under a 4.0 GPA scale, UK classifications (First / 2:1 / 2:2), or other banded systems. Before enabling Option A, a **grading-scale normalisation rule** must be defined; only then can thresholds be discussed. Final thresholds require team and client sign-off.

**Risks of Option A**

- Transcripts may not reflect current mastery of a specific concept
- Grades from different courses and grading systems may not be directly comparable
- Course-to-topic weights embed unverifiable human judgement
- Real grades are sensitive personal information
- Students must be able to view, correct or refuse the resulting profile

### 4.4 Comparison of the Two Options

| Dimension | Option A: transcript | Option B: self-selected |
|---|---|---|
| Profile source | Historical course grades | Student self-assessment |
| Default status | Optional, subject to approval | **Default** |
| Privacy risk | High | Low |
| Ethics approval | Possibly required | Usually not required |
| Implementation cost | Medium-high | Low |
| Novelty | **Low (already covered by PRAG-EDU)** | No novelty claimed; serves as an experimental vehicle |
| Cold start | Generated automatically | Requires student input |
| Principal error mode | Grades diverge from concept-level mastery | Self-assessment bias |
| Calibration | Diagnostic quiz / interaction | Diagnostic quiz / interaction |
| Downstream Layer C | Shared | Shared |

**Architectural consequence:** if Option A proves infeasible, only the Transcript Profile Builder is disabled; Layers C and D are entirely unaffected.

### 4.5 Profile Use in Experiments

**The main experiment uses fixed synthetic profiles, not real learner profiles.**

```text
Synthetic Beginner Profile      global_level = beginner,     confidence = 1.0
Synthetic Intermediate Profile  global_level = intermediate, confidence = 1.0
Synthetic Advanced Profile      global_level = advanced,     confidence = 1.0
```

Rationale: variables stay controlled, the experiment is reproducible, and the question of whether a profile is *accurate* is fully decoupled from whether the personalisation mechanism *works*. The three levels in the frozen matrix (§7.1) refer to exactly these three fixed profiles.

**Profile-source comparison is a separate small pilot** and is not crossed with the main matrix:

| Experiment | Content |
|---|---|
| Profile Initialisation Pilot | Compare profiles produced by transcript, self-selection, and self-selection plus diagnostic |
| Longitudinal Simulation (optional) | Validate the B3 Mini Quiz update mechanism using synthetic student trajectories |

Both are extension experiments and do not enter the formal matrix of §7.1.

### 4.6 Educational Equity and Escape Hatches

The core mechanism of this system is to **systematically adjust which evidence types a learner is shown, based on a proficiency label**. This carries an educational risk that the original risk register — which covered only technical and privacy concerns — did not address.

**The risk.** A learner labelled Beginner is systematically denied `derivation` and `boundary` evidence. Educational psychology provides substantial evidence that low expectations produce self-fulfilling effects. **Option B has the same problem**: once a student selects Beginner, without intervention they never encounter more advanced material.

**Required mitigations**

1. Students can **switch level at any time**, with immediate effect
2. Provide a **single-request depth override** (e.g. "show me the derivation") that yields Advanced-band evidence without altering the stored profile
3. Profile results must be **visible to the student, correctable, and refusable**
4. **Abstention (C5) and personalisation (C4) must never compound** into "you are a Beginner, so this material is withheld" — C5's criterion is evidence sufficiency alone and must be independent of level

**This risk and its mitigations must be discussed explicitly in the report.** In an educational-AI review context, raising and addressing it is a strength; omitting it is a conspicuous gap.

---

## 5. Boundaries of the Contribution Claims

The following are increments relative to **the comparators selected for this project**. Each claim must be scoped; none may be stated as a universal claim.

**1. Char-level gold evidence bound to the course corpus, with independent retrieval evaluation**

> Among the educational RAG systems compared in this project (LPITutor, PRAG-EDU), we found no char-level gold evidence bound to a course corpus, nor independent retrieval-side evaluation.

It must **not** be written as "no prior work provides gold evidence" — general-purpose benchmarks such as KILT already supply human-annotated gold provenance and evaluate retrieval and downstream performance separately.

**2. Abstention mechanism with paired metrics**

None of the above educational RAG comparators includes an abstention design.

**3. Personalisation applied at both C4 and C6, with the two independently switchable**

Each comparator covers only one side.

---

## 6. Implementation Order

```text
Phase 0  Dataset preparation
         A0: OpenStax parsing + SciQ alignment + chapter-isolated Dev/Test
         <- nothing downstream can begin until this is complete

Phase 1  Minimal working system
         A1 -> A5 -> C2 (dense only) -> C6 -> C7 (fixed JSON)
         = the LPITutor configuration; lightest engineering; this is the baseline

Phase 2  Evaluation capability
         D1 + D2 (Answer-choice Accuracy) -> add A4 (BM25) -> upgrade C2 to Hybrid RRF

Phase 3  Personalisation
         A2 + A3 (pilot -> freeze -> bulk annotation) -> B1 (Option B) / B2 -> C4 -> D3

Phase 4  Reliability
         C5 (multi-signal abstention) -> C8 (citation integrity) -> D4 + D5

Phase 5  If time permits (retain extension status)
         A6 + C3 (KG) -> C2.5 (topic-level) -> B3 + D6
         -> only with explicit authorisation: B1 Option A (transcript entry point)
```

**Two bottlenecks**

- **A0 blocks everything.** The quality of Evidence Alignment determines whether D1 is trustworthy; it needs dedicated staffing and manual spot-checking.
- **A3 is the bottleneck of the personalisation chain.** Pilot, freeze and bulk annotation must all complete before Phase 3 begins.

**Do not build indexes until A1 is final.** Two embedding models × two chunk sizes = four indexes; every change to parsing or cleaning invalidates all four.

---

## 7. Experimental Matrix and Budget

### 7.1 Frozen Matrix

This is the single authoritative matrix; any other figure elsewhere defers to it. The three levels correspond to the three fixed synthetic profiles of §4.5.

**Experiment 1 — Personalisation (primary)**

```text
primary model × 180 questions × 12 conditions
(4 combinations × 3 levels)
= 2,160 calls
```

**Experiment 2 — Model comparison (satisfies the official Llama / Qwen / Gemma / GPT requirement)**

```text
3 additional models × 60 stratified questions × 6 conditions
(conditions A and D × 3 levels)
= 3 × 360 = 1,080 calls

The primary model's results on those 60 questions are reused from
Experiment 1; they are not re-run.
```

**Total**

```text
2,160 + 1,080 = 3,240 calls
≈ 3,240 × 3,300 tokens ≈ 10.7 M tokens
```

**Rationale.** Personalisation is this project's research focus and is studied in depth on one model; cross-model comparison is an externally mandated breadth requirement and is run at the two endpoints of the frozen configuration (plain RAG and the full system). The two have different goals and need not be fully crossed.

**Excluded from this matrix:** Profile Initialisation Pilot, the KG-specific experiment, the topic-level extension, and the Longitudinal Simulation (see §4.5 and Phase 5 of §6).

### 7.2 Evaluation Allocation

| Scope | Volume | Method |
|---|---|---|
| All answers | 3,240 | Answer-choice Accuracy, readability metrics, C8 citation integrity, D1 retrieval metrics |
| Human blind rating | **360**, stratified from the primary model | Six-dimension rating + D3 level fit + D4 atomic claims |
| Double annotation | **20% of those 360 (72 items)** | Cohen's κ / Krippendorff's α |

Stratified sampling must span question types, levels and conditions, and **the sampling plan must be fixed before the Test set is unsealed.**

At five minutes per item, 360 items is roughly 30 hours plus about 6 hours for double annotation — within the capacity of an eight-person team.

### 7.3 Retrieval Consumes No LLM Tokens

| Module | LLM tokens |
|---|---|
| C1 Query processing | Small; skippable in single-turn settings |
| C2 / C2.5 / C4 / C5 | Zero |
| C3 KG Expansion | Zero to small |
| **C6 + C7 Generation** | **≈ 95% of the total** |
| C8 Citation integrity | Zero (string matching) |

A single exchange is approximately 2,900 input + 400 output ≈ 3,300 tokens.

### 7.4 Five Cost Controls

1. **Retrieval-side tuning invokes no LLM.** Chunk size, embedding choice, Top-K, fusion weights and λ are all tuned in the retrieval-only layer.
2. **Cache retrieval results.** The 12 conditions require only 6 distinct retrieval result sets (3 levels × 2 switch states).
3. **Use a token budget rather than a fixed candidate count.** Standardise on 1,500 retrieved tokens.
4. **Implement C8 by string matching; run claim verification on samples only.**
5. **Disable C1 during evaluation.**

### 7.5 Index Construction Cost

```text
7,000 chunks × 500 tokens = 3.5 M tokens
× 4 index sets = 14 M tokens through the embedding model
Local GPU: minutes per set; CPU: one to two orders of magnitude slower
```

A one-off cost, but upstream changes force a full rebuild — see the ordering constraint in §6.

---

## 8. Literature

### Architectural Sources

| Reference | Module |
|---|---|
| Lewis P., et al. Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. NeurIPS 2020, 33:9459–9474 | Backbone |
| LPITutor: an LLM based personalized intelligent tutoring system using RAG and prompt engineering. PeerJ Computer Science 11:e2991, 2025 | B1 / C6 / D2 |
| Nguyen V. D., et al. Towards Personalized AI Education: Context-Aware Retrieval-Augmented Generation With Grade-Level LLM Adaptation (PRAG-EDU). Computer Applications in Engineering Education 34(1), 2026. doi:10.1002/cae.70153 | B1 / B2 / C6; also the basis for demoting Option A |
| Dong C., et al. How to Build an Adaptive AI Tutor for Any Course Using Knowledge Graph-Enhanced Retrieval-Augmented Generation. arXiv:2311.17696 | A6 / C3 |
| Zhao B., et al. DeepTutor: Towards Agentic Personalized Tutoring. arXiv:2604.26962 · github.com/HKUDS/DeepTutor (Apache 2.0) | C8 / D6 |
| Li Z., et al. TutorLLM: Customizing Learning Recommendations with Knowledge Tracing and Retrieval-Augmented Generation. arXiv:2502.15709 | B3 (architectural position only) |
| Welbl J., Liu N. F., Gardner M. Crowdsourcing Multiple Choice Science Questions (SciQ). arXiv:1707.06209 | A0 question source (citation to be verified) |

### Sources of Inspiration (Not of Implementation)

**Correct wording for A3 and C4:**

> This project is informed by two lines of PersonaRAG work regarding the principle that personalisation should enter the retrieval stage. The Level-Aware Reranking mechanism — based on evidence roles, proficiency confidence and soft weighting — is our own design rather than a reimplementation of either algorithm.

| Reference | Note |
|---|---|
| Sanyal D., et al. Investigating Pedagogical Teacher and Student LLM Agents. EMNLP 2025. doi:10.18653/v1/2025.emnlp-main.675 | Educational setting; primarily generates personalised reasoning plans followed by multi-step retrieval — **not a post-retrieval weighting formula** |
| Zerhoudi S., Granitzer M. PersonaRAG. arXiv:2407.09394 | General-purpose user-personalised RAG; user-centric agents and document ranking |
| Anderson L. W., Krathwohl D. R. A Taxonomy for Learning, Teaching, and Assessing, 2001 | **Inspiration** for the A3 taxonomy, not an equivalent mapping |
| Gaita (Wong L., Johns Hopkins University, 2024) | Reference for the `learning_goal` and prior-knowledge fields in §4.1. Degree type unconfirmed; recommend a general citation |

### Evaluation and Theoretical Grounding

| Reference | Use and claim boundary |
|---|---|
| Ji Z., et al. Survey of Hallucination in Natural Language Generation. ACM Computing Surveys 55(12), Art. 248, 2023. doi:10.1145/3571730 | The intrinsic / extrinsic distinction underlying D4's two axes |
| EduAdapt: A Question Answer Benchmark Dataset for Evaluating Grade-Level Adaptability in LLMs. arXiv:2510.17389 · github.com/NaumanNaeem/EduAdapt | **Its grade-aware rubric and evaluation dimensions can be adapted, but must be mapped onto this project's three proficiency bands; raw benchmark scores are not directly comparable** (EduAdapt covers Grades 1–12 across nine science subjects) |
| Kalyuga S., Ayres P., Chandler P., Sweller J. The Expertise Reversal Effect. Educational Psychologist 38(1):23–31, 2003 | Theoretical grounding for C4; supplies a testable directional hypothesis — support effective for novices (examples, definitions) may become redundant for more knowledgeable learners |
| Pashler H., McDaniel M., Rohrer D., Bjork R. Learning Styles: Concepts and Evidence. Psychological Science in the Public Interest 9(3):105–119, 2008 | Justifies rejecting the learning-styles construct in favour of a measurable proficiency dimension |
| Petroni F., et al. KILT: a Benchmark for Knowledge Intensive Language Tasks. NAACL 2021 | Establishes that gold provenance with separated retrieval/downstream evaluation has precedent; used to bound our contribution claims (see §5) |
| Mladenov P., et al. Exploring Personalized Learning Support through Retrieval Augmented Generation: A Feasibility Study. SwissText 2024:144–147 | Cognitive-level stratification of question types |

**Wording for BERTScore / ROUGE-L:**

> BERTScore and ROUGE-L measure textual or semantic similarity to a reference answer, but are not sufficient on their own to demonstrate that an answer is appropriate to a learner's proficiency level.

Do not write "invalid"; that formulation is easily rebutted.

### To Be Verified

| Item | Issue |
|---|---|
| KG-RAG implementation details | An early revision stated "the original uses Qwen2.5"; this has been removed. The paper exists in multiple versions (arXiv v1, revised, IEEE), and another account reports DeepSeek-V3 for triple extraction with Alibaba `text-embedding-v2`. **Verify against the specific version cited.** |
| Wong L. Gaita: A RAG System for Personalized Computer Science Education. Johns Hopkins University, 2024 | Degree type unconfirmed (cited as PhD; search results indicate Master's) |
| SciQ formal citation | To be verified |
| OpenStax textbooks | Record exact titles and version numbers |

### To Be Added (Technical Layer; Sources Not Individually Verified)

- Cormack G. V., et al. Reciprocal Rank Fusion. SIGIR 2009 — RRF in C2
- Robertson S., Zaragoza H. The Probabilistic Relevance Framework: BM25 and Beyond, 2009 — A4
- Es S., et al. RAGAS: Automated Evaluation of Retrieval Augmented Generation — Layer D framework
- Asai A., et al. Self-RAG. ICLR 2024 — C5 abstention
- Artstein R., Poesio M. Inter-Coder Agreement for Computational Linguistics. Computational Linguistics, 2008 — inter-annotator agreement

---

## 9. Items Required Before Freezing

| Priority | Item | Blocks |
|---|---|---|
| **P0** | **Rework Unanswerable construction into the Unresolved Pool flow** (§3.1 pending note) | Validity of D5 abstention evaluation |
| **P0** | **Supervisor approval for OpenStax + SciQ** | The official description specifies a supervisor-provided dataset in a higher-education setting; SciQ is school-level crowdsourced multiple choice. Without approval the whole of A0 may be void |
| **P0** | Source of level-differentiated reference answers for D3 | SciQ supplies only a correct option, not banded pedagogical explanations. Authoring them is expensive; relying on blind relative comparison yields weaker conclusions |
| P0 | Whether corpus material may be sent to third-party APIs | Whether dense retrieval must run locally; whether a GPU is a hard requirement |
| P0 | Compute / API budget | Whether the matrix in §7.1 is executable |
| P1 | Evidence Role pilot annotation results | Whether the taxonomy can be frozen and bulk annotation can begin |
| P1 | Manual verification accuracy of Evidence Alignment | Whether D1 is trustworthy |
| P1 | Calibration of the C2.5 confidence threshold | Whether the topic-level extension experiment is viable |
| P1 | If Option A is enabled: grading-scale normalisation rule | The §4.3 thresholds do not hold on non-percentage scales |
| P2 | Availability of PRAG-EDU's 250-item benchmark | Withheld for privacy/ethics reasons; must be requested from the authors |
| P2 | LPITutor data availability statement | Check the original article |
