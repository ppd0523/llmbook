# Project development shell example

Copy `flake.nix` and `.envrc` to the root of a project, then create and commit
its lock file.

```console
$ git add flake.nix .envrc
$ nix flake lock
$ git add flake.lock
```

Enter the shell manually with `nix develop`, or approve this repository's
`.envrc` once with `direnv allow` and let direnv load it automatically.

The subdirectories are complete language-oriented variants used by the
LazyVim workshop:

- `python`: uv, `.python-version`, basedpyright, Ruff, and Python LazyVim extras
- `nodejs`: NVM, `.nvmrc`, local TypeScript/vtsls, and Prettier extras
- `rust`: rustup, `rust-toolchain.toml`, rust-analyzer, rustfmt, and Rust extras

Each variant deliberately leaves the language runtime out of `flake.nix`.
The Flake owns native project dependencies, while the language manager and
language lock file own the runtime and packages.

Every language directory also has a project-owned `.lazy.lua` and
`.lazy-lock.json`. The former selects the LazyVim extras for that repository;
the latter is populated by `:Lazy sync` and must be committed after the first
successful editor startup. The shared Home Manager configuration only
provides the LazyVim base and enables trusted local specs.

The complete beginner-oriented explanation is in
[Chapter 7](../../07_nix_develop/chapter.md) of the guide.
