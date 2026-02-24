# aifrontierpulse Build-in-Public Workflow

Last updated: 2026-02-21

## Goal
Use aifrontierpulse development as a personal-branding engine while documenting credible engineering progress.

## Publishing Cadence
- Weekly devlog: 1 post/week
- Milestone deep dive: at each major phase completion
- Micro-updates: optional snippets for X/LinkedIn

## Content Principles
- Show decisions, not just outcomes.
- Be explicit about failures and tradeoffs.
- Share concrete artifacts (schema, prompts, eval criteria, runtime metrics).
- Keep claims auditable with links to code/docs.

## Source of Truth for Blog Inputs
Each weekly blog draft should pull from:
1. `PROJECT_TRACKER.md`
2. `DECISIONS.md`
3. recent implementation diffs and validation logs
4. current open risks/blockers

## Weekly Post Structure
1. Why this week mattered
2. What was shipped
3. What changed in architecture
4. What failed / what was learned
5. Metrics snapshot
6. Next-week plan
7. Ask to readers (feedback request)

Use template:
- `content/blog/templates/weekly_build_log.md`

## Quality Gate Before Publishing
- No vague claims without evidence.
- Include at least 3 concrete technical artifacts.
- Include at least 1 unresolved risk.
- Include measurable next steps for next week.

## Distribution Plan
- Longform: Substack/Medium/personal site
- Shortform: LinkedIn + X thread summary
- Keep one canonical longform draft, then derive platform variants.

## Ownership
- Primary author: You
- Draft synthesis support: aifrontierpulse export pipeline (planned)
