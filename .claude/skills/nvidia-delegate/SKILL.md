---
name: nvidia-delegate
description: "Use when the user asks to delegate work to NVIDIA NIM, DeepSeek, Kimi, or Nemotron, or when an expensive primary model should offload analysis, coding, repository implementation, or independent review."
---

# NVIDIA Delegate

## Principle

Use the primary model as planner and reviewer while an NVIDIA worker handles the high-volume work. Token savings only materialize when the worker acts directly and returns a compact result.

Keep these modes separate:

| Need | Mode | Tool access |
|---|---|---|
| Analyze or draft from context included in the prompt | `scripts/ask.py` | No |
| Read, edit, and test a repository | `opencode run` | Yes |

## Model Routing

Use models that are configured and verified with a real request. `GET /models` alone does not prove inference availability.

| Work | API model ID | OpenCode selector | Recommended mode |
|---|---|---|---|
| Default coding implementation | `moonshotai/kimi-k3` | `nvidia/moonshotai/kimi-k3` | `opencode run` |
| Difficult reasoning or implementation | `deepseek-ai/deepseek-v4-pro-0813` | `nvidia/deepseek-ai/deepseek-v4-pro-0813` | `opencode run` |
| Small or fast task | `deepseek-ai/deepseek-v4-flash-0731` | `nvidia/deepseek-ai/deepseek-v4-flash-0731` | `opencode run` |
| Independent review with a supplied diff or text | `nvidia/nemotron-3-ultra-550b-a55b` | `nvidia/nvidia/nemotron-3-ultra-550b-a55b` | `scripts/ask.py` |

Model availability changes. If an ID returns an inference error, stop recommending it until a smoke test succeeds.

## Agentic Delegation

For repository work:

1. Define the expected behavior, scope, exclusions, constraints, and acceptance tests.
2. Give the worker the repository path instead of pasting files it can inspect itself.
3. Run the selected model with the full OpenCode selector:

```powershell
opencode run --dir "<absolute-repository-path>" --model "nvidia/moonshotai/kimi-k3" "<self-contained brief with the output contract>"
```

4. The worker inspects, edits, and tests. It preserves unrelated changes and does not delegate again.
5. The primary model reviews the diff and runs independent verification before claiming completion.

Include this mandatory output contract in the brief:

```text
STATUS: done | blocked
CHANGED: <count>; <up to 5 key paths>
TESTS: <up to 3 commands and pass/fail>
RISKS: none | <up to 3 brief risks>
NEXT: none | <one required action>
```

The final worker response must stay within 12 lines and 250 words. It contains no preamble, code, diff, logs, internal reasoning, or repeated brief. A blocked worker explains the blocker in `NEXT`.

## Text Delegation

For work that needs no tools, use the API model ID and the helper included beside this skill:

```powershell
python "<skill-directory>\scripts\ask.py" "<api-model-id>" "<self-contained prompt with the output contract>"
```

The model cannot read files or infer conversation context. Include only relevant material and require:

```text
RESULT: <conclusion or deliverable>
EVIDENCE: <up to 5 references or bullets>
RISKS: none | <up to 3 brief risks>
NEXT: none | <one required action>
```

For long inputs, request findings and precise references rather than reproduction. Use Nemotron with a bounded supplied diff. If review requires repository inspection, use DeepSeek V4 Pro through `opencode run` with read-only instructions.

## Token Discipline

- Workers modify files directly instead of printing modified code.
- The primary model consumes the compact summary, necessary diff, and test results, not a transcript.
- Request decisions and short evidence, never chain-of-thought.
- If output violates the contract, request one compact reformulation only.
- Allow one reasonable model fallback after a failed delegation, then report the blocker.

## Safety

- Never use `--auto` without explicit authorization.
- Never run two editing workers in the same worktree concurrently.
- Never allow recursive delegation or a worker to launch another `opencode run`.
- Never print, prompt with, or log API keys.
- Never delegate destructive, publishing, payment, or irreversible operations without specific approval.

Tell the user briefly what was delegated and what the primary model independently verified.
