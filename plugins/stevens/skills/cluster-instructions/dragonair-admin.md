# Dragonair administration

Use this only for admin tasks, and only if the user has asked for one. These commands need `sudo`.

## Add a user

Do this after their Linux account exists:

```bash
sudo sacctmgr -i add user <username> account=stevens
sudo install -d -o <username> -g stevensgroup -m 700 /data/<username>
```

## Change limits and recover the node

```bash
sudo sacctmgr modify qos normal set MaxJobsPerUser=10       # change a per-user limit
sudo scontrol update nodename=lin-mms009 state=resume       # return a drained node to service
systemctl status slurmctld slurmd slurmdbd slurm-portal     # check the services
```

If you change a limit, update `dragonair.md` in this skill as well.

## Job board

The job board is read-only and listens only on the machine itself:

- Port `8080` needs no password. Agents and tunnels use it.
- Port `8081` needs the shared group password. Any public web server must proxy only to this port.

To change the password, run `sudo slurm-portal-passwd`. This signs out every browser and needs no restart. Don't commit the password to this repo.

## Where things are

| What | Where |
|---|---|
| Slurm configuration | `/etc/slurm/` |
| Slurm logs | `/var/log/slurm/` |
| Job board | `/opt/slurm-portal/` |
| Login-session limits | `/etc/systemd/system/user-.slice.d/50-login-limits.conf` |
| Helper commands | `/usr/local/bin/gpu-shell`, `/usr/local/bin/slurm-jupyter` |
| Quick guide for users | `/data/local_libs/SLURM.md`, installed from `dragonair.md` |
