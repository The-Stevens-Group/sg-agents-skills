# sg-agents-skills

Shared agent skills for the Stevens Group. See `README.md` for what's here and how it installs.

## Rules for changes

- **This repo is public.** Never commit passwords, IP addresses, member usernames or firewall details.
- **One skill tree.** All skills live in `plugins/stevens/skills/`. Claude Code, Codex and `npx skills` all read that one folder, so don't add a second copy for any agent.
- **Skills must work in every agent.** Don't name tools that only one agent has, and don't rely on frontmatter other agents can't ignore. `disable-model-invocation` is one example, because Codex rejects it.
- **No plugin version.** Leave `version` out of both `plugin.json` files, so installs follow commits without a version bump.
- **`dragonair.md` is the source for dragonair facts.** `machine-setup/dragonair/install.sh` copies it to `/data/local_libs/SLURM.md`. When a limit changes, update that file and the short rules in `machine-setup/dragonair/agent-rules.md`, then run the script again.

Before opening a PR, run `python3 scripts/validate.py`.
