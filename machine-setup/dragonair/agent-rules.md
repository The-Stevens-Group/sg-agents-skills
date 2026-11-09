# Dragonair: shared machine rules

You are on dragonair, the Stevens Group's shared GPU machine. Other people's work runs here.

- Run anything that uses a GPU or more than a few CPU cores through Slurm, never directly. This includes training, inference and test suites that use a GPU, even if the user just says to run a command such as `python train.py`.
- Submit with `sbatch --parsable --gres=gpu:1 -c 8 --mem=64G -t 4:00:00 -J <name> -o /data/$USER/slurm-logs/%x-%j.out --wrap "<command>"`. Run `mkdir -p /data/$USER/slurm-logs` first. Leave out `--gres` if the job needs no GPU, and request only what the job needs.
- Check a job with `sacct -j <jobid> -X -n -o state`. Only cancel your own jobs.
- These are fine to run directly: editing, git, installing packages, small scripts and `nvidia-smi`. Login sessions are limited to 8 CPUs and 48 GB of RAM.
- Keep datasets, checkpoints and logs in `/data/$USER`, and code and environments in `/home/$USER`.
- Read `/data/local_libs/SLURM.md` for limits, job templates and troubleshooting.
