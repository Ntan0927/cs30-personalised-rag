# Member 8 - demo interface

This module consumes `PipelineRun`.

## Week 1 acceptance

- A new member can start the system from the README.
- The client can pick a level, ask a question, and see answer and sources.
- No real key reaches the repository.

## Notes

Always surface `PipelineRun.mode`. A fixture run must never be presented
as a real result, and an abstained answer must be shown as a refusal
rather than as an empty answer.
