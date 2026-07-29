# 10. 문제 해결과 재현성 점검

## 학습 목표

- 오류가 발생한 계층을 구분한다.
- 흔한 증상에서 우선 확인할 항목을 찾는다.
- 프로젝트의 완료 기준을 스스로 점검한다.

## 10.1 계층부터 찾기

이 프로젝트의 흐름은 길지만 각 도구의 책임은 분명하다.

```text
Nix 셸
  └─ Conan install
       └─ CMake configure
            └─ Make build
                 └─ ELF 검사
                      └─ target 실행
                           └─ DDS discovery와 데이터 교환
```

가장 먼저 실패한 단계의 전체 로그를 본다. 뒤 단계의 현상으로 앞 단계의 원인을
추측하면 진단이 복잡해진다.

## 10.2 증상별 빠른 점검표

| 증상 | 우선 확인 |
|---|---|
| Conan이 CMake 4를 거부한다 | `nix develop`의 CMake가 3.x인지 확인 |
| `platform_tool_requires`를 찾지 못한다 | Conan을 Nix 셸 밖에서 실행하지 않았는지 확인 |
| compiler 경로가 비어 있다 | `nix develop`을 다시 열고 profile의 환경 변수 확인 |
| 교차 빌드가 x86_64 compiler를 쓴다 | `profile:host=host-aarch64-musl`인지 확인 |
| `Exec format error`와 `idlc`가 함께 보인다 | 교차 빌드에서 IDL 생성을 실행하지 말고 기록된 생성물 사용 |
| `CycloneDDS::ddsc`를 찾지 못한다 | 올바른 Conan toolchain 파일로 configure했는지 확인 |
| `Telemetry.h`가 없다 | `generated/`가 함께 checkout되었는지 확인 |
| 링크에 shared library가 남는다 | Conan의 `shared=False`와 `-static`, musl compiler 확인 |
| 프로그램은 실행되지만 sample이 없다 | domain, topic, IDL, 실행 순서 확인 |
| 같은 장치에서는 되지만 LAN에서는 안 된다 | interface, firewall, multicast, WSL 네트워크 확인 |

## 10.3 CMake 3.x를 따로 고정한 이유

주 Nixpkgs 26.05의 기본 CMake는 4.x지만 `cyclonedds/0.10.2` Conan recipe의 build
tool 요구 범위는 CMake 4 미만이다. 그래서 Flake는 compiler와 Conan은 26.05에서,
CMake 3.31은 25.05에서 가져온다.

이 선택은 임의의 전역 CMake를 숨겨 쓰는 우회가 아니다. 두 nixpkgs revision 모두
`flake.lock`으로 고정되며 Conan profile은 Nix가 제공한 CMake 버전을
`platform_tool_requires`로 선언한다.

## 10.4 cache와 build 폴더 분리

네이티브와 교차 결과는 절대 같은 폴더를 공유하지 않는다.

```text
build/native/conan   build/native/app
build/aarch64/conan  build/aarch64/app
```

profile이나 toolchain을 바꾼 뒤 오래된 CMake cache가 의심되면 해당 구성의
`app` 폴더만 삭제하고 configure를 다시 한다. 삭제 전에 현재 경로가 프로젝트 아래의
정확한 폴더인지 확인한다.

Conan package ID와 설정은 다음 명령으로 먼저 살펴볼 수 있다.

```console
$ conan graph info . \
    --profile:build=profiles/build-x86_64 \
    --profile:host=profiles/host-aarch64-musl
```

## 10.5 lockfile 갱신 원칙

dependency 버전을 의도적으로 올릴 때만 lockfile을 다시 만든다.

1. `conanfile.py`의 버전을 수정한다.
2. 네이티브와 aarch64 lockfile을 각각 다시 만든다.
3. 두 구성을 모두 새 폴더에서 빌드한다.
4. ELF와 DDS 통신 검증을 반복한다.
5. recipe와 lockfile 변경을 함께 검토한다.

`--build=missing`은 binary가 없을 때 source build를 허용하지만 dependency graph를
마음대로 최신화하라는 뜻은 아니다.

## 10.6 최종 체크리스트

- [ ] `nix develop`에서 CMake, Make, C/C++ compiler, Conan 버전이 재현된다.
- [ ] Nix 셸 밖의 전역 compiler와 CMake를 사용하지 않는다.
- [ ] Conan이 `cyclonedds/0.10.2`, `spdlog/1.17.0`을 제공한다.
- [ ] `conan-native.lock`, `conan-aarch64.lock`, `flake.lock`을 기록한다.
- [ ] IDL과 `generated/Telemetry.c`, `generated/Telemetry.h`가 함께 기록되어 있다.
- [ ] 네이티브 publisher/subscriber가 10개 샘플을 교환한다.
- [ ] aarch64 실행 파일의 `Machine`이 AArch64다.
- [ ] aarch64 실행 파일에 `INTERP`와 `NEEDED`가 없다.
- [ ] Nix 없는 target에서 두 실행 파일이 동작한다.
- [ ] x86_64와 aarch64가 LAN에서 양방향 통신한다.

## 다음 단계

기본 과정을 통과한 뒤에는 다음 주제를 별도 변경으로 확장할 수 있다.

- DDS QoS를 IDL과 독립적으로 구성 파일에 분리
- unicast peer를 이용한 multicast 제한 네트워크 대응
- 자동화된 네이티브 테스트와 aarch64 artifact 생성
- Cyclone DDS 상위 버전으로 올릴 때 Conan recipe와 wire 호환성 검증
- DDS Security와 인증서 배포

## 요약

- 실패한 계층과 그 입력부터 확인한다.
- 네이티브와 교차 cache를 분리하고 lockfile 갱신을 의도적인 작업으로 다룬다.
- 빌드 성공만이 아니라 ELF, target 실행, LAN 통신까지 통과해야 완료다.
