---
name: cluster-instructions
description: Detect which machine or HPC cluster you are on and load the correct job submission instructions. Covers the Stevens Group's shared GPU machine dragonair (lin-mms009), Imperial CX3/HX1, UCL MMM Young and Isambard AI. Use when the user asks to submit, run, queue, monitor or schedule a job, use a GPU, run training or other heavy work, connect to dragonair, or asks about Slurm, job limits or why a job is pending.
argument-hint: "[command-to-run (optional)]"
allowed-tools: Bash, Read, Grep, Glob, Write, Edit
---

# Cluster Instructions

Before submitting any jobs or running heavy commands, detect which machine you are on and follow the correct instructions.

**IMPORTANT**: Never run Python workloads, heavy CPU or GPU commands directly on a login node or a shared machine. Always submit via the scheduler unless you have confirmed you are on a compute node or inside a job.

## Step 1: Detect the machine

Run these checks in order:

```bash
# Check host and working directory path
hostname
hostname -f 2>/dev/null || true
pwd

# Check available scheduler
if command -v sbatch >/dev/null 2>&1; then
    echo "SLURM"
elif command -v qsub >/dev/null 2>&1 && command -v qconf >/dev/null 2>&1; then
    echo "SGE"
elif command -v qsub >/dev/null 2>&1; then
    echo "PBS"
else
    echo "UNKNOWN"
fi
```

| Host or path pattern | Machine | Scheduler | Instructions |
|---|---|---|---|
| Hostname `lin-mms009` or `dragonair.dpag.ox.ac.uk` | Stevens Group dragonair | SLURM | `dragonair.md` in this skill |
| `/rds/general/user/<user>/home/` | Imperial CX3 | PBS Pro | `cx3.md` in this skill |
| `/gpfs/home/<user>` | Imperial HX1 | PBS Pro | Use CX3 instructions (`cx3.md`) |
| `/lustre/home/<user>` + `sbatch` available + Young hostname | UCL MMM Young NG | SLURM | `mmm-slurm.md` in this skill |
| `/lustre/home/<user>` + `qsub`/`qconf` available + Young hostname | UCL MMM old Young | SGE / Grid Engine | `mmm-sge.md` in this skill |
| `/home/<project>/<user>.<project>/` + `/projects/<project>/` exists | Isambard AI | SLURM | `isambard.md` in this skill |

If none match, ask the user which machine they are on. If they want to use dragonair from another computer, the connection steps are in `dragonair.md`.

Detection order matters. A plain "SLURM exists" check is not enough, because dragonair, MMM Young NG and Isambard all expose SLURM. Use host and path first, then the scheduler.

## Step 2: Check if you are on a login node

- **Dragonair**: There is no separate compute node. Treat every shell as a login session unless `$SLURM_JOB_ID` is set, which means you are inside a job.
- **CX3**: Run `hostname`. If it contains `login`, you are on a login node — do not run compute commands directly. If it does NOT contain `login`, you are on a compute node and can run short Python commands directly.
- **MMM Young NG**: Hostnames like `login*.young.ucl.ac.uk` are login nodes. Use `sbatch` or `srun` via the MMM SLURM instructions.
- **MMM old Young**: Hostnames like `login*.ib.young.ucl.ac.uk` are login nodes. Use `qsub`; this is SGE, not PBS.
- **Isambard**: Assume login node unless inside an `srun` session or a batch job.

## Step 3: Load machine-specific instructions

Read the appropriate file from this skill's directory:

- **Dragonair**: Read `dragonair.md` — covers the Slurm rule, job templates, limits, fair use and troubleshooting. Read `dragonair-admin.md` only if the user asks for an admin task, such as adding a user.
- **CX3 / HX1**: Read `cx3.md` — covers PBS Pro queues, job templates, key patterns, common commands, and storage paths.
- **MMM Young NG**: Read `mmm-slurm.md` — covers SLURM partitions/QoS, GPU A100 requests, modules, and common commands.
- **MMM old Young**: Read `mmm-sge.md` — covers SGE queues, project/account flags, GPU requests, modules, and common commands.
- **Isambard**: Read `isambard.md` — covers SLURM job templates, GPU allocation (Grace Hopper Superchips), DDP setup, and common commands.

Follow those instructions for all job submission, script creation, and resource allocation decisions.

## Step 4: Submit or run the command

If `$ARGUMENTS` contains a command or script to run:

1. Determine if it needs a batch job (long-running, GPU, heavy CPU) or can run directly (quick debugging, <5 min).
2. For batch jobs: create a job script using the templates from the machine-specific instructions, then submit it. On dragonair, `sbatch --wrap` is fine for a single command.
3. For quick commands on a compute node: run directly.
4. For quick commands on a login node:
   - **Dragonair**: Small CPU-only checks can run directly. Anything that uses a GPU goes through `srun` or `sbatch`.
   - **CX3**: Use `qsub -I` for an interactive session.
   - **MMM Young NG**: Use `srun` with a partition/QoS from `mmm-slurm.md`.
   - **MMM old Young**: Use `qsub` with flags from `mmm-sge.md`; do not run tests directly on the login node.
   - **Isambard**: Use `srun` for an interactive session.

If no arguments are provided, just report which machine and node type you detected.
