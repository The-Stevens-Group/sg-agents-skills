#!/usr/bin/env bash
# Gives every agent on dragonair the always-on rules and the group's skills,
# without anyone installing anything.
#
#   sudo machine-setup/dragonair/install.sh               install or update
#   sudo machine-setup/dragonair/install.sh --uninstall   remove everything it added
#   machine-setup/dragonair/install.sh --root DIR         write into DIR, to inspect or test
#
# Claude Code updates the plugin itself. Codex's copy of the skills updates only
# when this script runs again, so run it after pulling changes.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS="$HERE/../../plugins/stevens/skills"
MARKER=.installed-by-sg-agents-skills
ROOT=""
ACTION=install

while (($#)); do
    case "$1" in
        --uninstall) ACTION=uninstall ;;
        --root) ROOT="$2"; shift ;;
        *) echo "Unknown argument: $1" >&2; exit 2 ;;
    esac
    shift
done

if [[ -z "$ROOT" && "$(hostname -s)" != lin-mms009 ]]; then
    echo "This is for dragonair (lin-mms009), and this machine is $(hostname -s)." >&2
    exit 1
fi

CLAUDE_DIR="$ROOT/etc/claude-code"
CODEX_DIR="$ROOT/etc/codex"
GUIDE="$ROOT/data/local_libs/SLURM.md"
GUIDE_BACKUP="$GUIDE.pre-sg-agents-skills"

# Refuses to overwrite config that this script didn't write.
claim_dir() {
    if [[ -d "$1" && ! -e "$1/$MARKER" && -n "$(ls -A "$1")" ]]; then
        echo "$1 has files this script didn't install. Merge them by hand first." >&2
        exit 1
    fi
    install -d -m 755 "$1"
    touch "$1/$MARKER"
}

remove_claimed_dir() {
    if [[ -e "$1/$MARKER" ]]; then
        rm -rf "$1"
    fi
}

if [[ "$ACTION" == uninstall ]]; then
    remove_claimed_dir "$CLAUDE_DIR"
    remove_claimed_dir "$CODEX_DIR"
    if [[ -e "$GUIDE_BACKUP" ]]; then
        mv "$GUIDE_BACKUP" "$GUIDE"
    fi
    echo "Removed. Claude Code's cached plugin stays until each user removes it."
    exit 0
fi

umask 022
claim_dir "$CLAUDE_DIR"
claim_dir "$CODEX_DIR"

# Claude Code reads this for every user on the machine, in any repo.
install -m 644 "$HERE/agent-rules.md" "$CLAUDE_DIR/CLAUDE.md"
install -m 644 "$HERE/claude-managed-settings.json" "$CLAUDE_DIR/managed-settings.json"

# Codex has no system-wide AGENTS.md, so the rules go in its system config.
{
    printf "developer_instructions = '''\n"
    cat "$HERE/agent-rules.md"
    printf "'''\n"
} > "$CODEX_DIR/config.toml"
chmod 644 "$CODEX_DIR/config.toml"

rm -rf "$CODEX_DIR/skills"
install -d -m 755 "$CODEX_DIR/skills"
cp -R "$SKILLS/." "$CODEX_DIR/skills/"
chmod -R a+rX "$CODEX_DIR/skills"

# The always-on rules point here, so agents without the skills can still read it.
install -d -m 755 "$(dirname "$GUIDE")"
if [[ -e "$GUIDE" && ! -e "$GUIDE_BACKUP" ]]; then
    cp -p "$GUIDE" "$GUIDE_BACKUP"
fi
install -m 644 "$SKILLS/cluster-instructions/dragonair.md" "$GUIDE"

echo "Installed. New Claude Code and Codex sessions on dragonair will pick this up."
