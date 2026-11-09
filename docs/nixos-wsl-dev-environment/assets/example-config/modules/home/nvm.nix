{
  inputs,
  lib,
  ...
}:
let
  nvmRoot = ".local/share/nvm";
in
{
  # nvm의 프로그램 파일만 불변 링크로 관리한다. 상위 디렉터리는 쓰기 가능한
  # 상태로 남으므로 nvm이 $NVM_DIR/versions 아래에 Node 버전을 설치할 수 있다.
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
