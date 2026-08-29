# Member 7 Week 1 implementation and hand-off guide

This guide explains how to reproduce, understand, demonstrate, and integrate
the Week 1 Student Profile, personalised prompt, LLM generation, JSON, and
citation work.

## 1. Scope and non-scope

Member 7 owns:

1. A minimal `StudentProfile` for beginner, intermediate, and advanced levels.
2. A prompt combining the question, profile, and Top-K evidence.
3. An LLM adapter with timeout and provider-error handling.
4. A fixed three-field model response.
5. JSON parsing, schema validation, finite retry, and citation integrity.
6. A multi-dataset smoke run and one question shown at three levels.
7. Model, temperature, token, latency, retry, and failure records.

Week 1 does **not** claim retrieval accuracy, answer accuracy, or that one model
is better than another. Fixture output is always labelled as fixture output.

## 2. How data moves through the module

```text
StudentLevel
  -> Week1ProfileProvider
  -> StudentProfile

question + StudentProfile + RetrievalResult
  -> PromptBuilder
  -> LLMClient
  -> strict three-field JSON
  -> Pydantic validation
  -> citation allow-list validation
  -> GeneratedAnswer
```

When `RetrievalResult.hits` is empty, the generator does not call the LLM. It
returns `GeneratedAnswer(abstained=True)` because an ungrounded answer is worse
than a clear refusal.

## 3. Important files

| File | Purpose |
|---|---|
| `src/cs30/profile/provider.py` | Builds the three profiles |
| `src/cs30/generation/prompt.py` | Level guidance and evidence prompt |
| `src/cs30/generation/schema.py` | Exact three-field JSON schema and parser |
| `src/cs30/generation/client.py` | Mock and OpenAI Responses API clients |
| `src/cs30/generation/generator.py` | Retry, validation, citation checks, trace |
| `src/cs30/generation/batch.py` | Continues after an individual failure |
| `src/cs30/generation/demo.py` | Combined-dataset and three-level smoke artifacts |
| `tests/test_generation.py` | Behaviour and failure-path tests |

## 4. Set up the repository

Use Python 3.11 or newer from the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

On Windows PowerShell, activate with:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

## 5. Run the automated checks

```bash
python -m pytest
ruff check .
```

The task-7 tests cover:

- all three profiles;
- all question choices reaching the prompt;
- exact JSON fields;
- valid citation ids;
- invalid JSON followed by a successful retry;
- an invented citation followed by a successful retry;
- a provider timeout or failure;
- finite retry exhaustion;
- batch continuation after one failed item;
- no-evidence abstention without an LLM call;
- Responses API request shape and usage extraction.

## 6. Produce the Week 1 smoke artifacts

Run without a key:

```bash
python -m cs30.generation.demo --provider mock
```

On this workspace the default combines all available datasets. Expected summary:

```json
{
  "completed": 72,
  "failed": 0
}
```

The 72 rows consist of 20 original fixture questions, Member 3's 24 packaged
SciQ questions and 8 packaged free questions, and 20 local SciQ rows. Exact
duplicate ids or question text are retained only once. Every result records
its dataset source. If the ignored local SciQ file is absent, the portable
packaged run contains 52 rows. The 8 packaged free questions contain no source
evidence and therefore deliberately abstain until the real retriever lands.

Inspect:

- `artifacts/task7/batch_72_results.json`
- `artifacts/task7/three_level_sample.json`

Every result records the answer, citation, model, temperature, token counts,
attempt count, latency, and validation failure types. The artifacts directory
is ignored by Git and should not be used as a formal evaluation dataset.

### Run with 20 real SciQ questions and temporary evidence

The local Week 1 adapter can read a Hugging Face dataset-server rows response:

```bash
python -m cs30.generation.demo --provider mock --dataset local-sciq \
  --sciq-json data/raw/sciq/train_first_20.json \
  --output-dir artifacts/task7-sciq
```

The questions and choices are real SciQ rows. Their `support` field is wrapped
as a single `fixture://sciq-support/train` retrieval hit. This is a temporary,
explicitly labelled substitute for Member 6 and is not evidence of retrieval
quality. The temporary adapter puts the correct answer at A so the structural
mock remains grounded; formal evaluation must use Member 3's agreed choice
ordering and Member 6's retrieved chunks.

## 7. Run one real local-model smoke request for free

Install Ollama, start it, and download the open-weight model once:

```bash
ollama run gpt-oss:20b
```

After it produces a response, run one project request:

```bash
python -m cs30.generation.demo --provider ollama --model gpt-oss:20b \
  --limit 1 --skip-three-level --output-dir artifacts/task7-ollama-smoke
```

No API key is required. Ollama listens on `http://localhost:11434` by default;
set `OLLAMA_BASE_URL` only when the service is hosted elsewhere. The adapter
passes the project's JSON schema to Ollama and retains the same local Pydantic
and citation allow-list validation used by every other provider.

Official references:

- [Ollama structured outputs](https://docs.ollama.com/capabilities/structured-outputs)
- [Ollama local API authentication](https://docs.ollama.com/api/authentication)
- [OpenAI gpt-oss-20b model](https://developers.openai.com/api/docs/models/gpt-oss-20b)

## 8. Run one real OpenAI smoke request (optional, paid)

Use a project key and a model the team is authorised to access. Do not commit
or paste the key into documentation.

macOS/Linux:

```bash
export OPENAI_API_KEY="your-project-key"
export LLM_MODEL="your-approved-model-id"
python -m cs30.generation.demo --provider openai --limit 1 --skip-three-level \
  --output-dir artifacts/task7-openai-smoke
```

Windows PowerShell:

```powershell
$env:OPENAI_API_KEY="your-project-key"
$env:LLM_MODEL="your-approved-model-id"
python -m cs30.generation.demo --provider openai --limit 1 --skip-three-level `
  --output-dir artifacts/task7-openai-smoke
```

After that single request succeeds, run the full combined-dataset batch plus
the three-level sample in a separate output directory:

```bash
python -m cs30.generation.demo --provider openai \
  --output-dir artifacts/task7-openai
```

The adapter uses the Responses API and Structured Outputs, but local Pydantic
and citation validation remain mandatory. Provider schema enforcement does not
replace application-level checks that a citation came from this retrieval run.

Official references:

- [Create a model response](https://developers.openai.com/api/reference/cli/resources/responses/methods/create)
- [Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs)

## 9. Connect Member 3's SciQ questions

Member 3 returns `SciQQuestion`. The frozen online port currently accepts a
string, so preserve the four choices with the supplied formatter:

```python
from cs30.generation import format_sciq_question

sciq = question_provider.get("stable_question_id")
question_for_generation = format_sciq_question(sciq)
```

Do not pass only `sciq.question`; the model would not see the four choices and
could not set `final_choice` meaningfully.

## 10. Connect Member 6's retrieval result

Member 6 must return the frozen `RetrievalResult` directly:

```python
retrieval = retriever.retrieve(sciq.question, top_k=5)
answer = generator.generate(question_for_generation, profile, retrieval)
```

Required hit fields are `chunk_id`, `text`, `chapter_id`, `source`, `score`,
and consecutive `rank`. Citation validation uses the actual `chunk_id` values
in this object, not a separately maintained source list.

## 11. Run the local online RAG pipeline

The portable combined retriever and Member 7 adapters are wired in
`build_real_deps()`. Ask an arbitrary question through Ollama with:

```bash
python -m cs30.pipeline --mode real --provider ollama --model gpt-oss:20b \
  --question "What is the difference between velocity and acceleration?" \
  --level beginner --top-k 3
```

The retriever returns the frozen `RetrievalResult` directly. If no sufficiently
related evidence is present, the generator abstains without calling Ollama.
Member 6's later dense retriever can replace the portable implementation behind
the same Protocol. The model wiring remains:

```python
import os

from cs30.generation import OpenAIResponsesClient, PersonalisedAnswerGenerator
from cs30.profile import Week1ProfileProvider

client = OpenAIResponsesClient(
    model=os.environ["LLM_MODEL"],
    temperature=config.generation.temperature,
)
generator = PersonalisedAnswerGenerator(
    client,
    max_retries=config.generation.max_retries,
)
```

The retriever and these two objects are placed in `PipelineDeps`. The
orchestration and frozen contracts do not change.

## 12. Pull Request checklist

Before asking for review:

```bash
git status
python -m pytest
ruff check .
git diff --check
```

Confirm:

- no `.env`, API key, logs, or generated artifacts are staged;
- fixture output is never called a real result;
- all citations are a subset of the actual retrieval hits;
- empty evidence causes abstention;
- the existing fixture pipeline still passes;
- the PR targets the team integration branch requested by the Leader.
