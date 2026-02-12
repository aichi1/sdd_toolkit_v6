# SDD Core Workflow

## Command Sequence (MUST follow this order)
```
/init-task → /run-phase N → /finalize → /retrospective
```

## /init-task
- Creates: docs/ (What), skills/ (How), CLAUDE.md, metadata.json
- Requires: empty or new project directory
- Completion: all docs/ have content (not template stubs), all SKILL.md exist

## /run-phase
- Input: phase number (`1`), range (`1-3`), or `all`
- Flags: `--review-only`, `--no-validation`, `--checkpoint`, `--batch`
- Flow per phase:
  1. Builder generates deliverables → `outputs/phase-{N}/`
  2. Pre-check via `scripts/validate-outputs.py --phase {N}`
  3. Fast-path (if pre-check PASS + ≤5 criteria + ≤3 files) or full Validator
  4. PASS → next phase | NEEDS_REVISION → fix cycle (max 2 auto) | FAIL → escalate
- Default multi-phase: Smart mode (auto-advance on PASS, pause on issues)

## /finalize
- Archives to `~/.sdd-knowledge/docs-archive/`
- Extracts/updates starters
- Generates finalization-report.md
- Warns if Critical Issues remain

## /retrospective
- Structured Q&A + metrics
- Saves: ./retrospective.md + ~/.sdd-knowledge/retrospectives/*.json
- Updates summary.json

## Phase Dependencies
- Phase N requires Phase N-1 completed (unless explicitly independent)
- Skip allowed only with user approval → status: `completed_with_issues`

## Error Handling
- Missing prerequisite phase → prompt to run it first
- 3x NEEDS_REVISION → stop auto-fix, escalate to user
- Builder timeout (>10min) → save partial, ask user
- Validator timeout → mark `not_validated`

## Detail Reference
Full workflow details, execution patterns, and troubleshooting: `docs/rules-reference/sdd-workflow-detail.md`
