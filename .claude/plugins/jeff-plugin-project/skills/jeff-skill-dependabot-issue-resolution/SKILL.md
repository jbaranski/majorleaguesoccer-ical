---
name: jeff-skill-dependabot-issue-resolution
description: Resolve all open Dependabot PRs by consolidating updates into a single feature branch, with ecosystem-specific ordering rules. Use when asked to "resolve dependabot PRs", "batch dependabot updates", or "consolidate dependabot issues".
---

Goal: Resolve all open Dependabot PRs in this project by consolidating their
dependency updates into a single feature branch, verifying the project still
passes its tests, and dropping any update that breaks the build.

**Before starting, copy this checklist and track each item as you work:**

```
## Setup
- [ ] Listed every open Dependabot PR and its linked issue (if any)
- [ ] Created branch chore/dependabot-batch-<date> off main

## Angular/npm (skip section if no Angular sub-project exists)
- [ ] Opened https://angular.dev/update-guide and confirmed the correct upgrade
      path from the current Angular version to the latest
- [ ] Ran `ng update @angular/core @angular/cli` following the guide's steps
- [ ] For every OTHER npm dependency being bumped by Dependabot: checked its
      required version range against the new Angular version's peer dependency
      constraints — any conflict must be treated as a skip (do NOT force the
      version); see "On failure or incompatibility" below
- [ ] Applied only the npm deps that are required to satisfy Angular's new
      peer dependency constraints (zone.js, typescript, test tooling, etc.)
- [ ] Confirmed `ng build` and full test suite pass before touching anything else
- [ ] Applied remaining standalone npm updates that are not Angular-constrained
- [ ] Confirmed `ng build` and full test suite still pass after standalone updates

## Other ecosystems (repeat block for each — Go, Python, etc.)
- [ ] <ecosystem>: applied all Dependabot version bumps from the relevant PRs
- [ ] <ecosystem>: full test suite passes

## For every dependency that was skipped or failed
- [ ] Posted a comment on the Dependabot PR stating: which constraint or test
      failed, the exact error or version conflict, and that it was excluded from
      this batch for independent follow-up
- [ ] Posted the same explanation on the linked issue (if one exists)

## Finalize
- [ ] Full test suite passes for all sub-projects with all applied updates
- [ ] Written report lists every dependency: updated vs. skipped, with reasons
- [ ] Closed the Dependabot PR and linked issue for every successfully updated dep
- [ ] Consolidated PR merged to main
```

---

## Setup

1. Identify all open Dependabot PRs (and their associated issues, if any).
2. Create a new feature branch off `main` (e.g. `chore/dependabot-batch-<date>`).
   All consolidated changes go here — do not commit directly to `main`.
3. Note that this repo may contain multiple independent sub-projects in
   different directories (e.g. an Angular frontend AND a Go/Python/etc. backend).
   Each ecosystem is an independent track. There is NO required ordering
   between tracks — the backend (Go modules, etc.) can be updated before, after,
   or alongside the frontend. The ordering rules below apply only WITHIN a track.

## Within the Angular/npm sub-project (if one exists)

The Angular-first rule is scoped to this sub-project only — it does not block or
gate updates in other directories/ecosystems.

**Do not skip the version compatibility check.** Before applying any update,
confirm it is compatible with the current (or newly updated) Angular version.
If a dependency's required version range conflicts with Angular's constraints,
treat it as a failure and follow the "comment and skip" steps below — do not
force the version.

1. Before touching ANY other npm dependency in this sub-project, update Angular
   itself first. Consult https://angular.dev/update-guide for the correct upgrade
   path to the latest version, and perform the update via `ng update` (core + CLI)
   following the guide's steps.
2. After Angular is updated, determine which other npm dependencies must change
   to satisfy Angular's version constraints (e.g. test tooling, zone.js,
   typescript, build/peer-dep requirements). Apply those — they are mandatory if
   the project would otherwise break against the new Angular version.
3. Only AFTER the above is stable, apply any remaining standalone npm updates
   that are independent of Angular. Do these LAST to avoid conflicts with the
   Angular update process.

## Within any other sub-project / ecosystem (Go, Python, etc.)

Coalesce the dependency bumps from the relevant Dependabot PRs into the feature
branch. No special ordering required.

## Verify

Run the full test suite (and build, if applicable) for each affected sub-project
with all the updates applied.

## On failure or incompatibility — comment, isolate, and exclude

If any test or build fails, OR if a dependency cannot be applied due to version
incompatibility (e.g. conflicts with Angular's peer dependency constraints):

1. Methodically determine which specific dependency update caused the failure
   (e.g. bisect by reverting bumps one at a time).
2. Exclude that single dependency from the batch (revert it to its prior version).
3. Post a comment on the corresponding Dependabot PR (and linked issue, if any)
   explaining why it was skipped: the incompatibility or failure encountered,
   the error message or constraint summary, and that the PR was excluded from
   this batch so it can be revisited independently.
4. Re-run the tests and continue with the remaining updates.
5. Repeat until the test suite passes with the largest possible set of updates.

## Report and finalize

1. Produce a clear report listing, per sub-project:
   - Dependencies successfully updated.
   - Dependencies that could NOT be updated, with the reason (which test/build
     broke, which version constraint was violated, or why, if known).
2. For each dependency that was successfully updated, close its corresponding
   Dependabot PR and any linked issue.
3. Merge the consolidated feature branch's PR into `main`.

Leave the Dependabot PRs for the excluded/failed dependencies open so they can
be revisited.
