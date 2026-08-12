---
title: 자료 조사
version: 1.0
status: complete
owner: agent
updated: 2026-08-12
target_reader: EDSDK를 처음 접하는 기술 담당자
topic: Canon EDSDK 기능 중심 카메라 제어
---

# 자료 조사

## 출처와 검증 상태

| 출처 | 성격 | 확인한 주장 | 본문 반영 |
|---|---|---|---|
| [Canon CAP Overview](https://asia.canon/en/campaign/developerresources/camera/cap/cap) | 공식 현재 개요 | EDSDK USB 유선 제어, 원격 촬영·전송·설정·라이브 뷰, AF·초점 위치·라이브 뷰 표시 정보 | 확정 |
| [Canon 호환성 목록](https://developercommunity.usa.canon.com/resource/1670450894000/CDC_EDSDKRAW_Compat_List) | 공식 호환성 표 | EOS 200D/Kiss X9/SL2, EOS 200D II/250D/SL3/Kiss X10, EOS 850D/T8i/Kiss X10i 포함 | 확정 |
| [Canon EDSDK 릴리스 노트](https://asia.canon/en/campaign/developerresources/camera/cap/edsdk-eos-digital-camera-sdk-release-note) | 공식 변경 이력 | 200D II와 850D 계열 지원 추가, EVF PC Small 등 버전 의존 변경 | 확정 |
| [EDSDK API Programming Reference (2016)](https://downloads.triprism.com/public/%5B%20Steve%20%5D/forTyler/canon%203.4sdk/EDSDK_API%203.4.pdf) | 캐논 구버전 공개 참조서 | 초기화·세션·이벤트·SaveTo·SetCapacity·셔터·EVF·AF·DriveLens·동영상·DownloadComplete 흐름 | 조건부 확정: 최신 SDK 문서/헤더와 실제 기종 시험이 우선 |
| [pyedsdk 공개 헤더](https://github.com/andrewrk/pyedsdk/blob/master/edsdk/EDSDKTypes.h) | 오픈소스 헤더 사례 | AF/EVF/셔터 명령과 속성의 분리, 상수 명칭 | 보조 근거 |
| [Canon EOS Utility Remote Live View 안내](https://cam.start.canon/tc/S003/manual/html/UG-03_RemoteCamera_0070.html) | 공식 제품 안내 | AF 기능은 카메라별 주의사항 확인, 렌즈 AF 스위치 필요, 확대 보며 MF 가능 | 보조 근거 |

## 핵심 사실과 조건

- EDSDK의 PC 라이브 뷰는 EVF 이미지 객체·메모리 스트림으로 프레임을 내려받는 흐름이다. UVC 웹캠 장치 생성은 이 API의 역할이 아니다.
- Host/Both 저장에서 카메라는 앱의 `DownloadComplete` 또는 `DownloadCancel`까지 전송 데이터를 캐시한다.
- `PressShutterButton`의 반누름·완전 누름은 유지 상태이며 `Off`로 해제해야 한다.
- `DoEvfAf`와 `DriveLensEvf`는 라이브 뷰 조건에서 각각 AF와 상대 렌즈 구동을 담당한다.
- 기준 세 기종은 EDSDK 호환성 표에 있으나, 개별 렌즈·촬영 모드·펌웨어에서의 세부 명령 허용 여부는 연결 후 조회·시험해야 한다.

## 버전·위험 관리

- API 참조서의 판권·개정 시점은 2016이다. 최신 EDSDK 패키지에는 추가 상수·지원 기종·OS 제약이 있을 수 있으므로, 함수명·구조·기능 흐름의 근거로만 사용한다.
- 공개 GitHub 헤더는 SDK 배포본이 아니다. 상수명 대조를 위한 보조 자료로만 사용한다.
- 모델별 AF 위치 지정, EVF 해상도, 동영상 원격 제어, 저장 카드 필요 조건은 실제 배포 패키지의 최신 API 문서·헤더와 장비 시험에서 확정한다.

## 예제와 위험 요소

- Worked example: Host 저장으로 정지 사진을 촬영하고 전송 완료까지 처리하는 상태 흐름
- Worked example: PC 라이브 뷰를 시작해 최신 JPEG 프레임만 소비하고 종료하는 흐름
- 위험: 전송 요청 방치, 셔터 해제 누락, PC EVF 출력 비트 전체 덮어쓰기, 프레임 객체 누적, 렌즈별 초점 구동의 무조건 지원 가정
