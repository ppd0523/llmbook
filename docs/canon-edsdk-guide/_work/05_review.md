---
title: 기술 검증
version: 1.0
status: complete
owner: agent
updated: 2026-08-12
target_reader: EDSDK를 처음 접하는 기술 담당자
topic: Canon EDSDK 기능 중심 카메라 제어
---

# 기술 검증

## 검증 결과

| 주장 | 근거 | 상태 |
|---|---|---|
| 세 기준 기종의 EDSDK 호환성 | 공식 호환성 목록, 릴리스 노트 | 확인 |
| EDSDK는 USB 유선 제어이며 원격 촬영·전송·설정·라이브 뷰를 제공 | 공식 CAP Overview | 확인 |
| Host/Both 저장은 완료/취소 통지가 필요 | 2016 API Reference의 SaveTo 설명 | 확인, 최신 SDK 문서 대조 필요 |
| 셔터 누름 상태는 Off로 해제해야 함 | 2016 API Reference의 PressShutterButton 설명 | 확인, 최신 SDK 문서 대조 필요 |
| EVF PC 출력 설정 후 속성 변화 뒤 프레임 다운로드 | 2016 API Reference의 Live View 예시 | 확인, 최신 SDK 문서 대조 필요 |
| DoEvfAf와 DriveLensEvf의 역할 분리 | 2016 API Reference와 공개 헤더 | 확인, 최신 SDK 문서 대조 필요 |
| UVC 웹캠 장치 생성은 EDSDK의 직접 기능이 아님 | EVF JPEG 스트림 API의 범위와 공식 기능 개요에서의 라이브 뷰 설명 | 합리적 추론으로 명시 |

## 수정 사항

- 최신 API 문서가 아닌 2016 참조서를 사용한 모든 기능은 “구버전 참조서”, “실제 패키지·기종 시험 우선” 조건을 명시했다.
- `TakePicture`를 기준 세 기종의 기본 촬영 방식으로 권하지 않고, 셔터 버튼 제어를 권장했다.
- 터치 AF·동영상·원격 초점 구동을 전 기종 공통 보장으로 쓰지 않고 속성·허용값·명령 시험으로 확인하게 했다.

## 남은 위험

- 실제 EDSDK 배포본과 EOS 200D/200D Mark II/850D·장착 렌즈로 실행하는 하드웨어 검증은 이 문서 작성 환경에서 수행하지 못했다.
- 최신 SDK의 정확한 오류 코드·추가 속성·펌웨어별 제약은 배포 패키지의 최신 API 문서가 우선이다.
