# 9. target 배포와 LAN 통신

## 학습 목표

- Nix가 없는 aarch64 Linux에 실행 파일을 배포한다.
- target 내부와 서로 다른 장치 사이의 DDS 통신을 확인한다.
- network interface와 discovery 문제를 분리해 진단한다.

## 9.1 배포 범위

target으로 옮길 필수 파일은 두 개다.

```text
build/aarch64/app/dds_publisher
build/aarch64/app/dds_subscriber
```

SSH, 이동식 저장 장치, 장치 관리 시스템 등 환경에 맞는 방법으로 복사한다. target에서
실행 권한을 확인한다.

```console
target$ chmod +x dds_publisher dds_subscriber
```

Nix와 Conan, compiler, CMake, Make는 target에 설치하지 않는다.

## 9.2 target 한 대에서 검증

target 터미널 A:

```console
target$ ./dds_subscriber 10 20 0
```

target 터미널 B:

```console
target$ ./dds_publisher 10 500 0 arm-device
```

이 검사는 아키텍처와 정적 링크, target의 기본 DDS 동작을 한 번에 확인한다. 이 단계가
실패하면 LAN보다 먼저 실행 권한, CPU 아키텍처와 로그를 점검한다.

## 9.3 x86_64와 aarch64 사이 통신

두 장치를 같은 LAN에 연결하고 같은 domain ID를 사용한다.

x86_64 개발 PC:

```console
$ nix develop
$ ./build/native/app/dds_subscriber 10 30 0
```

aarch64 target:

```console
target$ ./dds_publisher 10 500 0 arm-device
```

역할을 반대로 바꿔도 된다. 서로의 source와 sample ID가 보이면 CPU와 libc가 달라도
IDL wire format으로 상호 운용된 것이다.

## 9.4 network interface 고정

장치에 Wi-Fi, Ethernet, VPN처럼 interface가 여러 개면 자동 선택이 원하는 LAN과
다를 수 있다. 먼저 실제 interface와 주소를 확인한다.

```console
$ ip address
$ ip route
```

Cyclone DDS 0.10.2에서는 환경 변수로 설정 XML을 전달할 수 있다. 다음 예의
`192.0.2.10`은 반드시 해당 장치의 실제 LAN IPv4 주소로 바꾼다.

```console
$ export CYCLONEDDS_URI='<CycloneDDS><Domain><General><NetworkInterfaceAddress>192.0.2.10</NetworkInterfaceAddress></General></Domain></CycloneDDS>'
```

각 장치에는 자기 주소를 지정해야 한다. 이 값은 상대 장치 주소가 아니다.

## 9.5 discovery가 되지 않을 때

기본 discovery는 multicast를 이용한다. 다음 순서로 범위를 좁힌다.

1. 양쪽 domain ID가 같은지 확인한다.
2. 양쪽 IP가 같은 LAN에서 서로 도달 가능한지 확인한다.
3. VPN과 불필요한 interface를 잠시 제외하거나 interface를 명시한다.
4. 호스트와 target의 firewall가 DDS의 UDP multicast와 unicast를 허용하는지 확인한다.
5. 공유기나 가상 네트워크가 multicast를 차단하지 않는지 확인한다.

WSL2의 기본 NAT 네트워크는 물리 LAN multicast discovery를 그대로 전달하지 않을 수
있다. 로컬 x86_64 실습은 WSL 내부에서 할 수 있지만, 실제 LAN 상호 운용 검증은
mirrored networking 설정이나 일반 Linux 호스트에서 수행하는 편이 명확하다.

## 9.6 최종 인수 기준

- target에서 publisher와 subscriber가 각각 정상 시작한다.
- target 내부에서 10개 샘플을 모두 받는다.
- x86_64 subscriber가 aarch64 publisher의 10개 샘플을 받는다.
- 역할을 바꿔도 통신한다.
- target에는 Nix store나 Conan cache를 복사하지 않았다.

## 연습문제

1. 각 장치의 실제 LAN 주소를 기록하고 `CYCLONEDDS_URI`를 설정한다.
2. domain ID를 7로 바꿔 양방향 통신한다.
3. target 한 대 검증과 LAN 검증이 각각 어떤 문제를 분리하는지 설명한다.

## 요약

- target에는 두 정적 실행 파일만 배포한다.
- 먼저 target 내부 통신, 그다음 LAN 상호 운용을 검증한다.
- discovery 문제는 domain, 주소, interface, firewall, multicast 순으로 좁힌다.
