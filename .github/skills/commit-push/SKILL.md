---
name: commit-push
description: "Review pending Git changes, create a commit with a short, clean message, and push it to the current branch. Use when asked to commit and push workspace changes."
argument-hint: "Optionally provide a short commit message or name files to commit"
---

# Commit and Push

Review the current repository changes, commit the intended work with a concise
message, and push the commit to its current remote branch.

## Procedure

1. Inspect the repository root, current branch, upstream, worktree status, and
   staged and unstaged diffs. Review untracked file names and contents before
   staging them.
2. By default, include **all pending, non-ignored repository changes**:
   staged, unstaged, and untracked files. Do not omit changes just because they
   predate the current request or seem unrelated. Narrow the scope only when
   the user explicitly names files or asks to exclude changes.
   - Do not include secrets, credentials, or clearly sensitive personal data.
     If any are present or a file's contents cannot be safely assessed, stop and
     ask the user what to do.
   - Exclude transient caches and temporary build output that should not be
     committed; do not exclude an existing or updated deliverable (including a
     generated binary) merely because it was generated.
   - Do not discard, reset, amend, or stash changes as a shortcut.
3. Run relevant, available targeted checks for the selected changes. If a check
   fails, investigate and report it; do not silently claim success. Do not
   commit generated artifacts unless they are part of the requested work.
4. Stage the full pending change set unless the user explicitly narrowed it.
   Review the staged diff and check for secrets, unrelated edits, generated
   clutter, and whitespace errors before committing.
5. Create one commit with a concise, accurate subject: normally an imperative
   phrase of about 3-7 words, with no trailing period. Prefer a user-provided
   message when it accurately describes the changes. Follow any applicable
   repository or session requirements for commit trailers.
6. Push the new commit to the current branch's configured upstream. If no
   upstream is configured, determine the appropriate remote and branch from
   repository configuration; ask if that target is ambiguous. Never force-push
   or bypass repository protections.
7. Verify the commit hash, pushed branch, and resulting repository status. If
   the commit succeeds but the push fails, keep the commit intact and clearly
   report the failure and next step. Do not make a second commit just to hide a
   push failure.

## Report

Summarize the commit subject and hash, the branch pushed, checks performed, and
any files or changes intentionally left out. Keep the report brief.
