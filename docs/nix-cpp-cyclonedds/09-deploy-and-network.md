# 9. 대상 장치 배포와 LAN 통신

## 학습 목표

- Nix가 없는 aarch64 Linux 장치에 실행 파일을 배포한다.
- 대상 장치 내부와 서로 다른 두 장치 사이의 DDS 통신을 확인한다.
- network interface와 discovery 문제를 분리해 진단한다.

이 장에서 "대상 장치"는 결과물을 실제로 실행할 aarch64 Linux 기계를 뜻한다. CMake의
target(빌드 단위)과는 다른 것이므로, 이 책에서는 장치를 가리킬 때 `target`이라는 표기를
쓰지 않는다.

## 9.1 배포 범위

대상 장치로 옮길 필수 파일은 두 개다.

```text
build/aarch64/app/dds_publisher
build/aarch64/app/dds_subscriber
```

SSH, 이동식 저장 장치, 장치 관리 시스템 등 환경에 맞는 방법으로 복사한다. 복사 방법에
따라 실행 권한이 보존되지 않을 수 있으므로 대상 장치에서 확인한다.

```console
device$ chmod +x dds_publisher dds_subscriber
```

Nix와 Conan, 컴파일러, CMake, Make는 대상 장치에 설치하지 않는다. Nix store나 Conan
cache도 복사하지 않는다. 8장의 정적 링크가 성립했다면 두 파일로 충분하다.

## 9.2 대상 장치 한 대에서 검증

대상 장치 터미널 A:

```console
device$ ./dds_subscriber 10 20 0
```

대상 장치 터미널 B:

```console
device$ ./dds_publisher 10 500 0 arm-device
```

이 검사는 아키텍처와 정적 링크, 그리고 장치의 기본 DDS 동작을 한 번에 확인한다. 한 대
안에서의 통신은 LAN을 거치지 않으므로, 여기가 성공하면 이후 실패는 네트워크 계층으로
범위가 좁아진다. 반대로 이 단계가 실패하면 LAN을 보기 전에 실행 권한, CPU 아키텍처,
프로그램이 출력하는 로그를 먼저 점검한다.

실행 즉시 `Exec format error`나 "cannot execute binary file"이 나오면 네트워크 문제가
아니라 8.4의 ELF 검사로 돌아가야 하는 신호다.

## 9.3 x86_64와 aarch64 사이 통신

두 장치를 같은 LAN에 연결하고 같은 domain ID를 사용한다.

x86_64 개발 PC:

```console
$ nix develop
$ ./build/native/app/dds_subscriber 10 30 0
```

aarch64 대상 장치:

```console
device$ ./dds_publisher 10 500 0 arm-device
```

subscriber가 상대의 source 이름과 sample ID를 출력하면 CPU와 libc가 달라도 IDL wire
format으로 상호 운용된 것이다. 역할을 반대로 바꿔 x86_64에서 publisher를, 대상 장치에서
subscriber를 실행하는 검증도 함께 수행한다. 한 방향만 확인하면 한쪽의 수신 경로만 막혀
있는 상태를 놓친다.

여기서 확인해야 할 것은 두 가지다. 첫째, 양쪽이 서로를 발견했는가(discovery). 둘째,
발견한 뒤 샘플이 실제로 전달되었는가. subscriber가 아무 로그 없이 timeout으로 끝나면
첫째 단계에서 막힌 것이고, 9.4와 9.5의 순서로 좁힌다.

## 9.4 network interface 고정

장치에 Wi-Fi, Ethernet, VPN처럼 interface가 여러 개면 자동 선택이 원하는 LAN과 다를 수
있다. 먼저 실제 interface 이름과 주소를 확인한다.

```console
$ ip address
$ ip route
```

Cyclone DDS 0.10.2는 환경 변수 `CYCLONEDDS_URI`로 설정 XML을 전달받는다. 0.10.2의 설정
문서가 interface 지정에 사용하는 요소는 `General/Interfaces/NetworkInterface`이고,
`address` 속성에 그 장치의 IPv4 주소를 적는다. 다음 예의 `192.0.2.10`은 반드시 해당
장치의 실제 LAN IPv4 주소로 바꾼다.

```console
$ export CYCLONEDDS_URI='<CycloneDDS><Domain><General><Interfaces><NetworkInterface address="192.0.2.10"/></Interfaces></General></Domain></CycloneDDS>'
```

주소 대신 interface 이름으로 지정할 수도 있다. `name` 속성을 쓰면 DHCP로 주소가 바뀌어도
설정을 고치지 않아도 된다.

```console
$ export CYCLONEDDS_URI='<CycloneDDS><Domain><General><Interfaces><NetworkInterface name="eth0"/></Interfaces></General></Domain></CycloneDDS>'
```

각 장치에는 **자기 주소 또는 자기 interface 이름**을 지정한다. 이 값은 상대 장치의
주소가 아니다. 개발 PC와 대상 장치에 같은 값을 복사해 넣는 것이 흔한 실수다.

오래된 예제나 사내 설정 파일에서 `General/NetworkInterfaceAddress` 형태를 만날 수 있다.
이 요소는 0.10.2에서도 받아들여지지만 deprecated로 처리되어 `General/Interfaces`로
옮기라는 경고를 출력한다. 그런 설정을 만나면 위의 `Interfaces/NetworkInterface` 형태로
바꾸고, 바꾼 뒤 경고가 사라지는지 확인한다.

## 9.5 discovery가 되지 않을 때

기본 discovery는 UDP multicast를 이용한다. 확인 비용이 낮고 원인이 잦은 순서대로 좁힌다.

1. 양쪽 domain ID가 같은지 확인한다. 실행 인자만 보면 되므로 가장 먼저 본다.
2. 양쪽 IP가 같은 LAN에 있고 서로 도달 가능한지 `ping`으로 확인한다.
3. VPN이나 컨테이너용 가상 interface를 잠시 내리거나, 9.4의 방법으로 interface를
   명시한다.
4. 양쪽 장치의 방화벽이 DDS의 UDP multicast와 unicast를 허용하는지 확인한다.
5. 공유기나 가상 네트워크가 multicast를 차단하지 않는지 확인한다. 두 장치를 같은 스위치나
   같은 무선 대역에 두고 다시 시도하면 이 항목을 빠르게 가를 수 있다.

1번과 2번이 통과했는데도 실패한다면 문제는 프로그램이 아니라 네트워크 경로에 있다.
3번부터는 한 번에 하나씩만 바꾸고, 바꿀 때마다 9.3의 검증을 다시 실행해야 어떤 변경이
효과가 있었는지 알 수 있다.

Windows의 WSL2에서 실습하는 경우, 기본 NAT 네트워크는 가상 네트워크를 한 단계 거치므로
물리 LAN의 multicast discovery가 그대로 오갈 것으로 기대하기 어렵다. 이 조건에 해당하는지는
WSL 안에서 `ip address`로 얻은 주소가 물리 LAN 대역과 같은지 보면 판단할 수 있다. 다른
대역이라면 WSL 내부의 x86_64 실습까지만 수행하고, 장치와의 LAN 상호 운용 검증은 mirrored
networking 설정이나 일반 Linux 호스트에서 하는 편이 원인 분리에 유리하다.

## 9.6 최종 인수 기준

- 대상 장치에서 publisher와 subscriber가 각각 정상 시작한다.
- 대상 장치 내부에서 10개 샘플을 모두 받는다.
- x86_64 subscriber가 aarch64 publisher의 10개 샘플을 받는다.
- 역할을 바꿔도 통신한다.
- 대상 장치에는 Nix store나 Conan cache를 복사하지 않았다.

## 직접 확인

1. 각 장치의 실제 LAN 주소와 interface 이름을 기록하고, 두 방식으로 각각
   `CYCLONEDDS_URI`를 설정해 본다.
2. domain ID를 7로 바꿔 양방향 통신한다.
3. 대상 장치 한 대 검증과 LAN 검증이 각각 어떤 문제를 분리하는지 설명한다.
4. subscriber가 timeout으로 끝났을 때, 9.5의 다섯 항목 중 실행 인자만 보고 판정할 수 있는
   항목이 무엇인지 고른다.

## 요약

- 대상 장치에는 두 정적 실행 파일만 배포한다.
- 먼저 대상 장치 내부 통신, 그다음 LAN 상호 운용을 검증한다.
- interface는 `General/Interfaces/NetworkInterface`의 `address` 또는 `name`으로 지정하고,
  각 장치에 자기 값을 넣는다.
- discovery 문제는 domain, 도달 가능성, interface, 방화벽, multicast 순으로 좁힌다.
