# Autoresearch Source Review

Timestamp: 2026-05-24 18:57 CDT.

Source checked:

- `https://github.com/karpathy/autoresearch`
- Local read-only clone: `tmp/autoresearch-check`
- Papers note: `https://papers.koval.lan/e1b5946c-f8fb-40b8-9345-d29451278e8d`
- Expanded Papers note: `https://papers.koval.lan/87076e7c-6c90-4b84-aa0b-ffc1392ff14e`

Useful pattern for the recursive-tools lane:

- The repo is intentionally small and bounded. The README identifies three important files: fixed preparation/evaluation code, one editable experiment file, and one Markdown program file.
- The agent edits only one source file during experiments. This keeps diff scope narrow and makes keep/discard decisions reviewable.
- The evaluation is fixed and metric-driven. `prepare.py` owns the evaluation/data path; the agent is told not to modify it.
- The run budget is fixed. Each experiment gets about five minutes, so result comparisons are made against the same wall-clock budget.
- `program.md` acts like lightweight org/agent code. The human programs the research loop by editing instructions, not by editing the experimental implementation directly.
- Results are logged to a simple uncommitted TSV with commit, metric, memory, status, and description.
- The branch advances only when the metric improves; losing or crashing experiments are discarded or logged as crashes.
- The prompt includes a simplicity criterion: keep simpler equal-performing code and reject tiny gains that add too much complexity.

Good ideas to steal:

- **Program-as-policy:** treat the Markdown instruction file as first-class system code. For KOVAL, each recursive pilot should have a compact `program.md`-style control file that states mutable files, immutable proof surfaces, metric, timeout, rollback rule, and reporting target.
- **One editable surface per run:** force each experiment to name exactly one mutable implementation surface. This is the cleanest way to stop recursive work from becoming broad refactor drift.
- **Immutable evaluator:** make the verifier/proof reader off-limits during a run. If the verifier needs changing, that is a separate proposal, not part of the same improvement attempt.
- **Fixed budget:** run every candidate under the same time, token, or operational budget. This makes the keep/discard decision comparable instead of vibes-based.
- **Keep/discard/crash ledger:** record failed attempts with short descriptions. The failures are useful training data for the next agent and prevent rediscovering the same dead ends.
- **Simplicity score:** an equal or tiny-positive result with less code should win; a tiny metric gain with much more complexity should lose. This maps directly to our recursive-tools stack where operational complexity is itself a cost.
- **Advance-only branch/worktree:** successful runs advance an isolated branch/worktree; losing runs are discarded inside that owned sandbox. This is compatible with KOVAL only if the worktree is created specifically for the harness.
- **Human edits the program, agent edits the implementation:** Robert or the AI Manager should tune the harness instructions and acceptance criteria; the worker agent should mutate only the approved implementation surface.
- **Wake-up report:** the output should be a compact ledger, not a transcript. For KOVAL this means `attempt_id`, source commit/state, hypothesis, changed surface, proof command, score, decision, and next idea.

Concrete KOVAL shape:

```text
recursive-run/
  program.md        # human/manager-owned harness instructions
  evaluator.md      # immutable proof contract and command
  attempts.tsv      # attempt_id, start_state, changed_surface, metric, complexity_delta, status, proof
  worktree/         # isolated branch/worktree owned by this harness
```

Candidate first pilot:

- Surface: one recursive-tools helper or one AI Health checker.
- Evaluator: existing proof command, for example `task_flow_truth_drift_check.py --fail-on-drift` or `claude_planner_proof_check.py`.
- Metric: pass/fail first, then fewer false positives, lower runtime, or clearer proof fields.
- Budget: one run per candidate, fixed timeout, no daemon/runtime mutation unless explicitly approved.
- Decision: `keep`, `discard`, `crash`, or `needs-approval`.

Recommended takeaways for KOVAL recursive tooling:

1. Add a narrow experiment-harness concept for future recursive pilots: one mutable implementation surface, one immutable verifier surface, and one Markdown/Task Flow program surface.
2. Treat each recursive improvement attempt as a measurable proposal/run pair with a fixed budget and a single canonical score.
3. Record keep/discard/crash decisions explicitly, not only final successes.
4. Keep the verifier immutable during a run. For KOVAL this maps to `/proof`, AI Health, Task Flow truth-drift checks, or a specific live readback depending on the lane.
5. Keep the current recursive-tools queue source-backed and permission-gated. Autoresearch assumes indefinite autonomous code mutation; KOVAL should use that only inside approved, low-blast-radius harnesses.

Not directly portable:

- The project assumes a single NVIDIA GPU and a toy LLM training workload.
- It optimizes one metric (`val_bpb`) in one code file. KOVAL's recursive tools involve multiple systems, email/approval state, live services, and proof surfaces.
- It uses `git reset` as part of the loop. That is not acceptable in shared dirty worktrees unless the harness owns an isolated branch/worktree.

Conclusion:

`karpathy/autoresearch` is useful as a design reference, not as code to import. The strongest transfer is the operating model: fixed verifier, fixed budget, one editable surface, explicit keep/discard/crash ledger, and Markdown instructions as the agent program.
