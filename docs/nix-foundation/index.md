---
title: "Nix 첫걸음: NixOS·개발 셸·Home Manager를 위한 기초"
version: 1.3
updated: 2026-07-30
baseline: Nix 2.34, NixOS/Nixpkgs 26.05, Home Manager 26.05
---

# Nix 첫걸음: NixOS·개발 셸·Home Manager를 위한 기초

Nix를 처음 보면 패키지 관리자, 프로그래밍 언어, 운영체제, 설정 도구가 모두 같은
이름 주위에 모여 있어 어렵게 느껴진다. 이 자료는 Nix 문법을 전부 외우게 하는 대신
다음 세 작업을 이해하는 데 꼭 필요한 공통 토대를 만든다.

- NixOS에서 시스템 설정을 읽고 안전하게 적용하기
- `nix shell`과 `nix develop`로 임시·프로젝트 개발 환경 사용하기
- Home Manager로 사용자 패키지와 설정 관리하기

## 대상과 전제 조건 {#prerequisites}

Nix 지식은 전혀 필요하지 않다. 터미널에서 `cd`, `ls`, 편집기 정도를 사용할 수 있고
패키지나 환경 변수라는 말을 들어 보았다면 시작할 수 있다. 예제 셸은 Bash 계열을
기준으로 하며 NixOS, Linux의 Nix, NixOS-WSL에서 실행할 수 있다.

Nix가 설치된 환경에서 다음을 확인한다.

```console
$ nix --version
nix (Nix) 2.34.x
```

이 자료의 `nix shell`, `nix develop`, Flake 예제에는 `nix-command`와 `flakes` 기능이
필요하다. 이미 명령이 동작하면 설정을 중복해서 추가하지 않는다. NixOS에서는 시스템
설정에 다음 옵션을 넣고 rebuild한다.

파일: `/etc/nixos/configuration.nix` (일부)

```nix
{
  nix.settings.experimental-features = [
    "nix-command"
    "flakes"
  ];
}
```

NixOS가 아닌 환경의 사용자별 설정은 다음과 같다.

파일: `~/.config/nix/nix.conf` (일부)

```ini
experimental-features = nix-command flakes
```

!!! note
    Nix 2.34 기준 새 `nix` CLI와 Flake는 공식 문서에서도 experimental로 표시된다.
    이 자료는 현재 저장소의 다른 책과 연결하기 위해 이 인터페이스를 사용하고,
    오래된 자료를 읽는 데 필요한 legacy 명령은 비교표로만 설명한다.

## 학습 목표

전 과정을 마치면 다음 질문에 답할 수 있다.

1. Nix, Nixpkgs, NixOS, Flake, Home Manager는 각각 무엇인가?
2. `/nix/store`의 긴 경로와 심볼릭 링크는 왜 필요한가?
3. 평가, 빌드(또는 다운로드), 활성화는 어떻게 다른가?
4. Nix 코드의 속성 집합, 목록, 함수, `let`, `import`를 어떻게 읽고 실행하는가?
5. `nix shell`, `nix develop`, `nix-shell` 중 무엇을 선택해야 하는가?
6. NixOS와 Home Manager의 `{ config, pkgs, ... }:`는 왜 함수인가?
7. package, option, module, profile, generation, Flake를 어떻게 구분하는가?
8. 설정 변경을 적용하기 전에 어떻게 검증하고, 실패하면 어떻게 돌아가는가?

## 권장 학습 순서

| 장 | 주제 | 권장 시간 | 결과 |
|---|---|---:|---|
| 1 | 생태계와 정신 모형 | 35분 | 이름과 책임 구분 |
| 2 | Nix 언어 읽기와 실행 | 110분 | 값·파일·함수·scope 평가와 설정 코드 해석 |
| 3 | Store와 세대 | 45분 | 불변 저장소와 롤백 이해 |
| 4 | 패키지 검색과 셸 | 90분 | package를 찾고 임시·프로젝트 환경 선택 |
| 5 | 모듈 시스템 | 55분 | option과 module 해석 |
| 6 | NixOS와 Home Manager | 45분 | 설정의 소유 계층 결정 |
| 7 | 통합 실습 | 60분 | 작은 개발 셸 직접 생성 |
| 8 | 문제 해결·용어·다음 단계 | 30분 | 스스로 조사하는 기준 마련 |

한 번에 끝내기보다 한 장씩 읽고 모든 `직접 해보기`를 실행하는 편이 좋다.

1. [Nix 생태계와 하나의 작업 흐름](./01-ecosystem-and-mental-model.md)
2. [Nix 언어를 읽는 최소 문법](./02-language-basics.md)
3. [Store, derivation, profile, generation](./03-store-builds-and-generations.md)
4. [패키지 사용과 세 종류의 셸](./04-shells-and-packages.md)
5. [NixOS·Home Manager의 모듈 시스템](./05-module-system.md)
6. [NixOS와 Home Manager에 연결하기](./06-nixos-and-home-manager.md)
7. [안내식 통합 실습](./07-guided-lab.md)
8. [문제 해결, 용어집, 다음 학습](./08-troubleshooting-and-next-steps.md)

## 이 자료에서 의도적으로 미루는 것

다음은 기초 사용에 필요하지 않아 후속 자료로 넘긴다.

- 직접 패키지를 만드는 `stdenv.mkDerivation`의 세부 단계
- overlay, override, `callPackage`, cross compilation
- Flake output 설계와 여러 시스템 지원
- NixOS 설치, 디스크 파티션, 보안 hardening
- secret 배포, 원격 빌드, binary cache 운영

## 읽는 동안 지킬 원칙

- Store 안의 파일을 직접 고치지 않는다. 원본 Nix 설정을 바꾸고 다시 빌드한다.
- 예제의 package 버전보다 “어떤 입력에서 어떤 출력이 왔는가”를 본다.
- `build`와 `switch`를 구분한다. 먼저 빌드하고 성공한 결과만 활성화한다.
- 인터넷 예제의 `nix-shell`, channel, Flake 문법을 한 구성에 무작정 섞지 않는다.
- `system.stateVersion`과 `home.stateVersion`을 업그레이드 번호처럼 올리지 않는다.

## 공식 기준 자료

- [nix.dev 첫 단계](https://nix.dev/tutorials/first-steps/)
- [Nix 언어 입문](https://nix.dev/tutorials/nix-language.html)
- [Nix 2.34 Reference Manual](https://nix.dev/manual/nix/2.34/)
- [NixOS 26.05 Manual](https://nixos.org/manual/nixos/stable/)
- [Home Manager Manual](https://nix-community.github.io/home-manager/)

[문서 목록으로 돌아가기](../index.md)
