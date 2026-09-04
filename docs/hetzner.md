# Hetzner

You run on a Hetzner server with full access.

- Management also logs in to this server with public-key authentication.
- This is your computer. You can use it for what you want. You run as `admin` with full `sudo` privileges, so you can install what you need.
- All outgoing traffic is open. For incoming traffic, only port 22 is open. If you must host a website, ask management to open the firewall.
- `git`, `curl`, and `gh` are installed and authenticated where applicable.

## Environment

Company secrets are in `/home/admin/.env`. This file is outside both repos, so Git cannot commit it. It must have mode `600`.

The login setup in `/home/admin/.profile` sources `$HOME/.env` and exports its variables during an interactive SSH login. Non-interactive processes do not run `.profile`. Cron jobs and systemd services do not receive the `.env` variables. Source `$HOME/.env` in your scripts.

Product secrets belong in the applicable product directory under `/home/admin/krimskrams-product/`. Do not add product secrets to the company `.env` file.
