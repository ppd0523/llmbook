---
title: Canon EDSDK 카메라 제어 매뉴얼
version: 1.1
updated: 2026-08-12
---

# Canon EDSDK 카메라 제어 매뉴얼

이 문서는 Windows에서 `EDSDK.dll`을 사용하는 제어 소프트웨어를 기획·검증하거나,
그 동작을 이해해야 하는 처음 접하는 기술 담당자를 위한 기능 중심 매뉴얼이다. 구현 언어,
라이브러리 로딩, 함수 선언, 예제 코드는 다루지 않는다. 대신 EOS 200D, EOS 200D Mark II,
EOS 850D를 USB로 연결했을 때 촬영·파일 전송·라이브 뷰·자동초점(AF)·원격 초점 구동을
어떤 상태와 순서로 제어해야 하는지 설명한다.

EDSDK(EOS Digital Camera SDK)는 캐논 EOS/일부 PowerShot을 호스트 컴퓨터에서 제어하는
SDK이며, 현재 공개 호환성 목록에는 세 기준 기종이 모두 포함되어 있다. 모델은 지역에 따라
다른 이름을 쓴다. EOS 200D는 Kiss X9/Rebel SL2, EOS 200D Mark II는 Kiss X10/Rebel
SL3/EOS 250D, EOS 850D는 Kiss X10i/Rebel T8i와 같은 기종이다.
[캐논 호환성 목록](https://developercommunity.usa.canon.com/resource/1670450894000/CDC_EDSDKRAW_Compat_List)과
[EDSDK 릴리스 노트](https://asia.canon/en/campaign/developerresources/camera/cap/edsdk-eos-digital-camera-sdk-release-note)를
2026-08-12에 확인했다.

## 이 매뉴얼로 할 수 있는 일

- 카메라 검색부터 세션 종료까지의 안전한 제어 순서를 설계한다.
- 정지 사진을 촬영하고 PC 또는 카드에 저장한 뒤 전송 완료를 처리한다.
- 라이브 뷰 이미지를 연속 취득해 자체 미리보기 또는 웹캠 입력 파이프라인의 영상원으로 쓴다.
- 라이브 뷰에서 AF를 한 번 실행하거나 렌즈를 가까운 쪽·먼 쪽으로 단계 이동한다.
- 노출, 화이트 밸런스, 화질, 저장 위치 같은 촬영 설정을 읽고 가능한 값만 변경한다.
- 지원하지 않는 기능, 카메라 상태 충돌, 파일 전송 대기 같은 흔한 실패를 진단한다.

## 먼저 알아둘 경계

- 이 문서에서 “웹캠 영상원”은 EDSDK가 주는 라이브 뷰 JPEG 프레임을 앱이 표시·전달하는
  흐름을 뜻한다. `EDSDK.dll`이 운영체제에 UVC 웹캠 장치를 등록하거나 HDMI 영상을
  직접 내보내지는 않는다. 화상회의 앱에 카메라를 웹캠으로 보이게 하려면 별도 가상 카메라
  또는 영상 파이프라인이 필요하다.
- EDSDK의 모든 상수·속성·명령이 세 카메라에서 같은 방식으로 동작한다고 가정하면 안 된다.
  실제 연결 뒤 해당 속성의 자료형과 허용 값 목록을 조회하고, 실패한 기능은 대체 경로로
  처리해야 한다.
- 카메라 메뉴, 촬영 모드, 장착 렌즈의 AF/MF 스위치, 메모리 카드, 배터리, 다른 캐논 앱의
  연결 상태도 결과에 영향을 준다. SDK 호출 성공만으로 원하는 광학 동작까지 보장되지는 않는다.

## 읽는 순서

1. [범위·호환성·제어 모델](./01-scope-and-compatibility.md)
2. [연결 세션과 이벤트](./02-session-and-events.md)
3. [정지 사진 촬영과 파일 전송](./03-still-capture-and-transfer.md)
4. [라이브 뷰와 웹캠 영상원](./04-live-view-and-webcam.md)
5. [자동초점과 원격 초점 구동](./05-autofocus-and-manual-focus.md)
6. [설정·동영상·문제 해결](./06-settings-video-and-troubleshooting.md)

[1장: 범위·호환성·제어 모델 →](./01-scope-and-compatibility.md)
