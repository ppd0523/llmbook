{ username, ... }:
{
  networking.hostName = "nixos-wsl";

  wsl = {
    enable = true;
    defaultUser = username;

    # Linux PATH를 결정적으로 유지한다. Windows 프로그램은 필요할 때
    # 명시적인 /mnt/c/... 경로로 계속 실행할 수 있다.
    interop.includePath = false;
  };

  # 설치 시점에 한 번 정한다. NixOS를 업데이트했다는 이유만으로 올리지
  # 않는다. 이 값은 패키지 릴리스가 아니라 호환성 마이그레이션을 제어한다.
  system.stateVersion = "26.05";
}
