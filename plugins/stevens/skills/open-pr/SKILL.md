---
name: open-pr
description: Open a GitHub pull request with a reviewer-focused summary, the repository's applicable checks, a strict maintainability review, and correctness and interface review passes.
argument-hint: "[base-branch (default: repository default)] [--draft]"
---

# Open PR

Prepare and open a PR for the user's authorized changes. Respect their constraints about
publishing, agents and checks. Opening a PR does not authorize merging or deployment.

## Establish the diff

Read the repository instructions and PR template. Check the current branch, working tree,
remote and existing PR. Use the user-named base, otherwise the repository's default branch.
Fetch that base and inspect the full diff from the merge base, plus surrounding code.

- Never open the default branch against itself.
- Commit in-scope changes after checks when the user has authorized that work. Do not
  silently exclude uncommitted changes or bundle unrelated files.
- Reuse an existing PR for this branch instead of opening a duplicate.
- Keep generated diff, review and check logs in a temporary directory outside the repo.

## Verify and review

Run the checks documented by this repository, including pre-commit when configured and
the actual test runner (a tests directory does not necessarily imply pytest). Do not
install unrelated test infrastructure. Use the sibling `cluster-instructions` skill if
checks require a scheduler; do not run workloads on a login node.

Run the sibling `thermo-nuclear-code-quality-review` against the diff. Also review
correctness and public interfaces/data handling as separate passes. Use independent
review agents only when available and authorized; otherwise label these as self-review.
Fix findings within scope, then rerun the affected checks. Preserve an accurate account
of remaining findings and omitted checks; never weaken a gate to make it pass.

A failed required check blocks a ready PR. Use a draft for unresolved blockers or explicitly
omitted required checks, if the user wants a reviewable draft. Do not treat a missing
optional test runner as evidence that checks passed.

## Describe the final change

Lead with the concrete problem and resulting behavior. Explain why the change is needed,
then include validation results, material risks and remaining review findings. Follow the
repository's template when present; keep the description proportional to the diff.
Do not claim that a self-review is independent. Omit abandoned approaches and chat history.

Write the exact description to a UTF-8 temporary file and use `gh pr create --body-file` or
`gh pr edit --body-file`, so backticks, dollar signs and newlines survive shell parsing.

## Publish and hand back

Push only within the user's authorization. Preserve an existing upstream; set it only on
the first push. Never force-push as part of opening a PR.

```bash
# When this feature branch has no upstream:
git push -u origin HEAD
# Once the exact description is saved in a temporary file:
gh pr create --base <base> --title "<title>" --body-file <description-file>
```

Use the host's PR-linking mechanism when available. Return the full PR URL and the state
of checks/reviews. Use the host's watch mechanism only when asked to monitor, or when
an authorized next action still waits on checks. Do not merge unless authorized.
