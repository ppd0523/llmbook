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

The complete beginner-oriented explanation is in
[Chapter 7](../../07_nix_develop/chapter.md) of the guide.
