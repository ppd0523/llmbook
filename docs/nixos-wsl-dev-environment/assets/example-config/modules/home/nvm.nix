{
  inputs,
  lib,
  ...
}:
let
  nvmRoot = ".local/share/nvm";
in
{
  # Manage only nvm's program files as immutable links. The parent directory
  # stays writable, so nvm can install Node versions below $NVM_DIR/versions.
  home.file."${nvmRoot}/nvm.sh".source = inputs.nvm-src.outPath + "/nvm.sh";
  home.file."${nvmRoot}/nvm-exec" = {
    source = inputs.nvm-src.outPath + "/nvm-exec";
    executable = true;
  };
  home.file."${nvmRoot}/bash_completion".source = inputs.nvm-src.outPath + "/bash_completion";

  programs.zsh.initContent = lib.mkAfter ''
    export NVM_DIR="$HOME/${nvmRoot}"
    [[ -s "$NVM_DIR/nvm.sh" ]] && source "$NVM_DIR/nvm.sh"
    [[ -s "$NVM_DIR/bash_completion" ]] && source "$NVM_DIR/bash_completion"

    autoload -U add-zsh-hook

    load-nvmrc() {
      local nvmrc_path requested_version installed_version
      nvmrc_path="$(nvm_find_nvmrc)"

      if [[ -n "$nvmrc_path" ]]; then
        requested_version="$(command cat "$nvmrc_path")"
        installed_version="$(nvm version "$requested_version")"

        if [[ "$installed_version" == "N/A" ]]; then
          nvm install
        elif [[ "$(nvm current)" != "$installed_version" ]]; then
          nvm use --silent
        fi
      else
        nvm deactivate --silent >/dev/null 2>&1 || true
      fi
    }

    add-zsh-hook chpwd load-nvmrc
    load-nvmrc
  '';
}
