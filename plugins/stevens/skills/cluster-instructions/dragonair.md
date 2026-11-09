# Dragonair

Dragonair (`dragonair.dpag.ox.ac.uk`, also `lin-mms009`) is the Stevens Group's shared GPU machine. It is a single Slurm node, so the machine you log in to is also where jobs run.

| | |
|---|---|
| **Available to jobs** | 56 CPU threads (28 cores), about 449 GB RAM, 2 × RTX PRO 6000 (96 GB each) |
| **Partition** | `main`, the default |
| **Code and environments** | `/home/$USER` |
| **Datasets, checkpoints and logs** | `/data/$USER` |

## The rule

**Anything that uses a GPU, or more than a few CPU cores, goes through Slurm.**

Nothing stops a direct run, which is why this matters. Slurm can't see direct work, so it may give someone else the same GPU, and either job can then run out of GPU memory. Agents should always use Slurm for this work.

| Work | Use |
|---|---|
| Training, inference, long runs | `sbatch` |
| Trying things by hand on a GPU | `gpu-shell` |
| Notebooks | `slurm-jupyter` |
| Editing, git, installing packages, small scripts, `nvidia-smi` | Run directly |

Each person's login sessions, including VS Code, tmux and nohup, share a limit of 8 CPUs and 48 GB of RAM, and processes can be killed at 64 GB. Slurm jobs don't count towards this limit.

## Submit a job

```bash
mkdir -p /data/$USER/slurm-logs   # once: a job fails if its log directory is missing
sbatch --parsable --gres=gpu:1 -c 8 --mem=64G -t 4:00:00 -J myjob \
  -o /data/$USER/slurm-logs/%x-%j.out --wrap "python train.py"
```

`--parsable` prints only the job ID. Your active Python environment carries over into the job. Without `-o`, output goes to `slurm-<jobid>.out` in the directory you submitted from.

| Flag | Meaning | Default if omitted |
|---|---|---|
| `--gres=gpu:N` | Number of whole GPUs | No GPU |
| `-c N` | CPU threads | 1 core (2 threads) |
| `--mem=64G` | RAM. The job is killed if it goes over | 7 GB per CPU thread |
| `-t H:MM:SS` | Time limit. The job is stopped when it is reached | 4 hours, maximum 3 days |

For anything you want to repeat, use a script and submit it with `sbatch train.sbatch`:

```bash
#!/bin/bash
#SBATCH -J myjob
#SBATCH --gres=gpu:1
#SBATCH -c 8
#SBATCH --mem=64G
#SBATCH -t 4:00:00
#SBATCH -o /data/%u/slurm-logs/%x-%j.out
set -euo pipefail
source ~/myenv/bin/activate
python train.py "$@"
```

## Work interactively

These need a terminal, so agents should normally use `sbatch` instead.

```bash
gpu-shell                      # 1 GPU, 8 CPUs, 64 GB, 4 hours
gpu-shell 2 16 128G 8:00:00    # GPUs, CPUs, memory, time
```

The shell holds its GPU until you type `exit`. It also ends if your connection drops, unless you started it inside `tmux`.

```bash
slurm-jupyter                  # 1 GPU, 8 CPUs, 64 GB, 8 hours; same arguments as gpu-shell
```

This needs `jupyterlab` in your active environment. It prints a URL and the job ID. Forward the port, open the URL, and run `scancel <jobid>` when you finish.

## Check on jobs

```bash
squeue                         # everyone's jobs
squeue -u $USER                # your jobs
squeue --json                  # machine-readable queue
sacct -j <jobid> -X -n -o state   # one job's state, including after it ends
sacct -X -S today              # your jobs from today
scontrol show job <jobid>      # full details of one job
scancel <jobid>                # cancel a job. Only cancel your own
sshare -a                      # fair-share standings
curl -s localhost:8080/api/state   # jobs, node, gpus, shares, usage_7d, rogue
```

In `/api/state`, `rogue` lists GPU processes running outside Slurm.

The job board at `http://localhost:8080` shows the same information as a web page. To open it from your own computer, run this there, not on dragonair, and leave it running:

```bash
ssh -L 8080:127.0.0.1:8080 <your-username>@dragonair.dpag.ox.ac.uk
```

## Limits

- **Time:** 4 hours by default, 3 days at most. Save checkpoints for anything that might run longer.
- **Jobs per person:** 10 running and 200 queued. Extra jobs wait in the queue, so don't resubmit them.
- **Priority:** fair share decides who goes next, so the less you have used recently, the sooner your jobs start. Past usage counts half as much after each week. Time in the queue also raises priority, and small jobs get a slight preference.
- **Running jobs are not interrupted:** priority only decides what starts next.

These can change. To read the current values:

```bash
sacctmgr -n -P show qos normal format=maxjobspu,maxsubmitpu   # running|queued per person
scontrol show partition main
```

## Use the GPUs fairly

There are only two GPUs, so they are the scarcest resource here.

- Use one GPU unless the work has been shown to need two.
- Set realistic time limits. Shorter jobs can start sooner because they fit into gaps.
- Exit `gpu-shell` and cancel idle notebooks. An idle session blocks a whole card.
- If you are an agent, limit how many jobs you submit at once.

## GPU details

- **Whole GPUs only:** a job can't request part of a GPU. `--gres=shard:N` and `--gpumem` are not available on this machine.
- **Numbering:** inside a job, its GPUs are numbered from 0. Outside jobs, Slurm's numbering can differ from `nvidia-smi`, which is harmless because each job still gets its own card.
- **Work outside the queue:** Ollama (`localhost:11434`) and containers started with `docker run` run outside Slurm. The queue doesn't reserve resources for them or limit them.

## Troubleshooting

| What you see | What it means | What to do |
|---|---|---|
| `Invalid account or account/partition combination specified` | You have not been added to Slurm | Ask the IT admin to add you |
| `Requested node configuration is not available` | The request can never fit, for example 3 GPUs or 600 GB of RAM | Request less |
| `More processors requested than permitted` | The request is more than the 56 CPU threads | Request fewer |
| `Requested time limit is invalid` | The limit is over 3 days | Request less, and use checkpoints |
| `Invalid generic resource (gres) specification` | The GPU request isn't valid here, for example shards | Use `--gres=gpu:N` |
| Pending with reason `Resources` | The CPUs, memory or GPUs it needs are in use | Wait |
| Pending with reason `Priority` | Other queued jobs go first | Wait |
| Pending with reason `QOSMaxJobsPerUserLimit` | You already have 10 jobs running | Wait, or cancel one |
| Job state `OUT_OF_MEMORY` | It went over `--mem` | Request more memory |
| Job state `TIMEOUT` | It reached its `-t` limit | Request more time, or resume from a checkpoint |
| Job state `FAILED` | Your command exited with an error | Read the job's output file |
| Login session is slow, or a process was killed | It reached the login-session limits | Run the work through Slurm |
| CUDA out of memory, although the job has its own GPU | Something outside Slurm may be using that GPU | Check `rogue` in `/api/state` or the job board, then contact the user shown or the IT admin |

## Connect from another computer

Connect to the MSD VPN first if you are outside the MSD network. Then:

```bash
ssh <your-username>@dragonair.dpag.ox.ac.uk
```

In VS Code, use the **Remote - SSH** extension with the same host. The editor runs in your login session and doesn't use the queue, so start GPU work from its terminal.

To get access, ask the IT admin for a Linux account and to be added to Slurm. You can log in without Slurm access, but you can't submit jobs.
