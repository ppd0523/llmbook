# Portable NixOS development environment

This repository separates NixOS host configuration from a standalone Home
Manager user profile. It targets NixOS-WSL and can apply the same user profile
on native NixOS.

## First machine: create the configuration repository

This directory is a template, not an existing personal repository. On the
first machine, create an empty GitHub repository without a README, license, or
`.gitignore`, copy this directory to `~/.config/nixos`, and then initialize it:

```console
$ sudo nix-channel --update
$ nix-shell -p git openssh
$ cd ~/.config/nixos
$ git init -b main
$ git config --local user.name "<your-name>"
$ git config --local user.email "<your-email>"
$ git remote add origin git@github.com:<github-user>/nixos-config.git
$ git add .
$ nix --extra-experimental-features "nix-command flakes" flake lock
$ git add flake.lock
$ sudo nixos-rebuild build \
    --option experimental-features "nix-command flakes" \
    --flake .#wsl
$ sudo nixos-rebuild switch \
    --option experimental-features "nix-command flakes" \
    --flake .#wsl
$ nix run .#home-manager -- build --flake .#nixos
$ nix run .#home-manager -- switch --flake .#nixos
$ exec zsh
$ git commit -m "Bootstrap NixOS-WSL environment"
$ git push -u origin main
$ exit
```

Configure and test GitHub SSH authentication before the first push. The full
from-scratch sequence, including WSL installation and SSH key setup, is in
[Chapter 2](../../02_install_nixos_wsl/chapter.md) of the guide.

The initial channel update is only an image bootstrap step recommended by
NixOS-WSL; the rebuild itself uses the locked Flake inputs.

## Later machines: restore the committed repository

For a private repository, register the new machine's SSH public key with
GitHub before running the clone command. Never restore an SSH private key from
this repository.

```console
$ sudo nix-channel --update
$ nix-shell -p git openssh
$ git clone <your-repository-url> ~/.config/nixos
$ cd ~/.config/nixos
$ test -f flake.lock
$ sudo nixos-rebuild build \
    --option experimental-features "nix-command flakes" \
    --flake .#wsl
$ sudo nixos-rebuild switch \
    --option experimental-features "nix-command flakes" \
    --flake .#wsl
$ nix run .#home-manager -- build --flake .#nixos
$ nix run .#home-manager -- switch --flake .#nixos
$ exec zsh
$ exit
```

Do not run `nix flake lock` or `nix flake update` during restoration. The
repository being restored must already contain the `flake.lock` committed on
the first machine.

The bootstrap intentionally uses the channel-backed legacy `nix-shell` after
`sudo nix-channel --update`. A `github:` Flake URL can exhaust GitHub's
unauthenticated REST API limit, while a `git+https:` Flake URL requires an
external `git` executable that the initial image does not yet have. If the
first `nix flake lock` later reports an API rate-limit error, wait for the
limit to reset or pass a GitHub token through Nix's `access-tokens` option;
never commit that token.

## LazyVim and project-local plugins

`modules/home/lazyvim.nix` installs Neovim, lazy.nvim, and only the shared
LazyVim requirements. It enables lazy.nvim's trusted project-local spec
support. Each application repository owns its language extras in `.lazy.lua`
and the resolved plugin revisions in `.lazy-lock.json`; run `:Lazy sync` once
and commit the populated lock file. The complete variants are in the
[project development shell examples](../example-dev-shell/README.md).

The project directory also gets an isolated plugin cache. Language runtimes
and LSP executables still come from uv, NVM/npm, or rustup after direnv has
loaded that project's development shell.

## Routine update

```console
$ nix flake update
$ nix fmt
$ sudo nixos-rebuild build --flake .#wsl
$ home-manager build --flake .#nixos
$ sudo nixos-rebuild switch --flake .#wsl
$ home-manager switch --flake .#nixos
$ git add flake.lock
$ git commit -m "Update Nix inputs"
```

## Native NixOS

Copy the target host's generated hardware module into
`hosts/native/hardware-configuration.nix`, add it to Git, and preserve the
host's original `system.stateVersion`. The flake will then expose
`nixosConfigurations.native`. Before switching, also migrate that host's
bootloader, networking, graphics, and other machine policies from its existing
NixOS configuration. The native module in this template is not a complete
hardware installation profile by itself.
