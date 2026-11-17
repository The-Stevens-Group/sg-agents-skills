# sg-agents-skills

Shared agent skills for the Stevens Group. See `README.md` for what's here and how it installs.

## Rules for changes

- **This repo is public.** Never commit passwords, IP addresses, member usernames or firewall details.
- **One skill tree.** All skills live in `plugins/stevens/skills/`. Claude Code, Codex and `npx skills` all read that one folder, so don't add a second copy for any agent.
- **Skills must work in every agent.** Don't name tools that only one agent has.
- **Run-only-when-asked skills need two switches.** Codex ignores `disable-model-invocation: true`, so pair it with `agents/openai.yaml` containing `policy:` / `allow_implicit_invocation: false`. See `untangle-codebase`.
- **Credit copied skills.** Keep the source's licence file in the skill folder and add the source to Origin in `README.md`.
- **Release every change.** Keep both plugin manifests at the same version. Every merged change increments the minor version, or the major version for breaking changes; patch-only bumps are not used. Update `CHANGELOG.md` and validate against the base with `python3 scripts/validate.py --base origin/main`. The release workflow publishes the matching tag and GitHub release after main passes validation.
- **`dragonair.md` is the source for dragonair facts.** `machine-setup/dragonair/install.sh` copies it to `/data/local_libs/SLURM.md`. When a limit changes, update that file and the short rules in `machine-setup/dragonair/agent-rules.md`, then run the script again.

Before opening a PR, run `python3 scripts/validate.py`.
