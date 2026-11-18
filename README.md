# sg-agents-skills

Shared agent skills for the Stevens Group, for Claude Code, Codex and other coding agents.

| Skill | What it does |
|---|---|
| `cluster-instructions` | Detects the machine you're on and loads its job instructions. Covers dragonair, Imperial CX3/HX1, UCL MMM Young and Isambard AI |
| `thermo-nuclear-code-quality-review` | Runs a very strict maintainability review of a branch or PR |
| `grill-me` | Interviews you to stress-test a plan or design |
| `socratic-tutor` | Teaches you a topic by asking questions, one at a time, until you've mastered it. Say "teach me X" or "quiz me on X" |
| `untangle-codebase` | Refactors a whole codebase so pieces that change together sit together. Long and thorough, so it only runs when you call it |

The package now also includes `claude`, `cleanup`, `doi2bib`, `edison`, `handoff`,
`monitor-jobs`, `notion-upload`, `open-pr`, `polish-pr` and `submit-wandb-job`.
They replace the corresponding Softnano skills under the `stevens` namespace.

## Install

On dragonair, you may not need to do anything. See [On dragonair](#on-dragonair).

**Claude Code**

```
/plugin marketplace add The-Stevens-Group/sg-agents-skills
/plugin install stevens@stevens-group
```

Skills appear as `/stevens:<skill>`.

**Codex**

```bash
codex plugin marketplace add The-Stevens-Group/sg-agents-skills
codex plugin add stevens@stevens-group
```

Skills appear as `$stevens:<skill>`.

**Cursor, OpenCode and other agents**

```bash
npx skills add The-Stevens-Group/sg-agents-skills -g
```

## On dragonair

A skill only helps once an agent decides to load it, and an agent told to run `python train.py` may not see that as submitting a job. So `machine-setup/dragonair/install.sh` puts short always-on rules on the machine itself:

| Agent | Always-on rules | Skills |
|---|---|---|
| Claude Code | `/etc/claude-code/CLAUDE.md` | Plugin turned on for everyone in `/etc/claude-code/managed-settings.json` |
| Codex | `developer_instructions` in `/etc/codex/config.toml` | Copied to `/etc/codex/skills/` |
| Others | Add `machine-setup/dragonair/agent-rules.md` to your project's `AGENTS.md` | `npx skills`, as above |

The script also installs the dragonair guide at `/data/local_libs/SLURM.md`. An admin runs it with `sudo`, and again after pulling changes, because Codex's copy of the skills only updates then.

A user's own Codex config can override `developer_instructions`.

## Automatic PR review

This repo's own review is turned off on GitHub until there's an API key. Turn it back on with `gh workflow enable "Thermo-nuclear review"`.

To review a repo's PRs automatically, copy [`.github/workflows/thermo-nuclear.yml`](.github/workflows/thermo-nuclear.yml) into its `.github/workflows/` folder. The repo also needs an `ANTHROPIC_API_KEY` secret, set on the repo or the org.

- **When it runs:** when a PR is opened, reopened, marked ready for review or pushed to. It skips drafts, so people can iterate in draft at no cost.
- **What it does:** it posts its findings as a PR comment. It doesn't block merging.
- **What it skips:** PRs from forks, because GitHub withholds secrets from them, and PRs from bots.
- **Why a file in each repo:** an org ruleset could cover every repo without one, but rulesets ignore `types` and never run on `ready_for_review`, so a draft could be marked ready and merged unreviewed.

## Add a skill

1. Add `plugins/stevens/skills/<skill-name>/SKILL.md`, with `name` and `description` in the frontmatter.
2. Run `python3 scripts/validate.py`.
3. Bump both plugin manifests by a minor version (or major for breaking changes), and update `CHANGELOG.md`. Every change needs a release, including documentation changes.
4. Run `python3 scripts/validate.py --base origin/main`, then open a PR. After merge, CI publishes the matching tag and GitHub release. See [`AGENTS.md`](AGENTS.md) for the rules.

## Origin

`cluster-instructions`, `thermo-nuclear-code-quality-review` and `grill-me` were copied from [softnanolab/softnano-plugins](https://github.com/softnanolab/softnano-plugins) at commit `fa058b6`. `thermo-nuclear-code-quality-review` and `grill-me` are unchanged. `cluster-instructions` adds dragonair and removes SoftNano's own accounts, aliases and workstation.

`untangle-codebase` is by Maze, from [caldoai/skills](https://github.com/caldoai/skills/blob/main/skills/untangle-codebase/SKILL.md) at commit `f3cf477`, under the MIT licence in its folder. It's unchanged apart from `agents/openai.yaml`, which stops Codex loading it automatically.

`socratic-tutor` is by Jane Street, from [janestreet/agent_skills](https://github.com/janestreet/agent_skills/tree/main/socratic-tutor) at commit `469868f`, under the MIT licence in its folder. It's unchanged.

## Licence

The Stevens Group's own work here is under the [MIT licence](LICENSE), so anyone can use, copy and change it. Skills copied from elsewhere keep their authors' terms:

- `untangle-codebase` and `socratic-tutor` are MIT, with each author's licence in the skill's folder.
- The skills from softnano-plugins came from a repository with no licence. The MIT licence covers the Stevens Group's changes to them, not the original text. That needs the softnano authors' permission.

## Moving from Softnano

Install `stevens@stevens-group` before disabling `softnano@softnanolab-plugins` in each
agent. All thirteen Softnano skill names are available, plus `untangle-codebase`.
Use `/stevens:<skill>` in Claude Code and `$stevens:<skill>` in Codex. Disable the old
plugin rather than loading both namespaces; cached files may remain for rollback.
Restart or start a new session to refresh the skill catalog. Each user should migrate
their own settings; this does not change another user's active session or jobs.

The ten additional workflows were migrated from the installed Softnano 2.1.0 package.
SG adaptations replace old namespace/cache paths, remove host-specific tool requirements,
route scheduler detection through `cluster-instructions`, and keep handoff secrets out
of command output. The source repository currently has no top-level licence file;
this migration preserves its attribution and does not assert a new licence for it.
