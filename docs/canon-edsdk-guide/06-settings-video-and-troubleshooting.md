# 설정·동영상·문제 해결

## 설정은 읽고, 허용값을 확인하고, 바꾼다

EDSDK 속성은 카메라에 가능한 값을 묻지 않고 임의로 설정하면 실패할 수 있다. 촬영 모드,
렌즈, 플래시, 라이브 뷰, 동영상 모드, 펌웨어가 어떤 값이 허용되는지 바꾼다. 따라서 모든
설정 화면은 다음 규칙을 따른다.

1. 연결 직후 현재 값과 자료형을 읽는다.
2. 설정할 수 있는 항목 목록을 읽어 UI의 선택지를 구성한다.
3. 사용자가 고른 값을 설정한다.
4. 속성 변경 이벤트를 받은 뒤 값을 다시 읽어 실제 반영값으로 UI를 갱신한다.
5. 지원하지 않음·잘못된 상태 오류라면 값을 되돌리고 이유를 설명한다.

| 목적 | 대표 속성 | 주의 |
|---|---|---|
| 노출 | `Tv`, `Av`, `ISOSpeed`, 노출 보정 | 촬영 모드가 허용하는 값만 설정한다. |
| 색 | White Balance, Color Temperature, Picture Style | 자동 WB·사용자 정의 값은 카메라 설정에 영향을 받는다. |
| 촬영 방식 | `AEMode`, Drive Mode, Metering Mode, `AFMode` | 모드 다이얼과 충돌하면 값이 거절되거나 바뀔 수 있다. |
| 결과 파일 | `SaveTo`, 이미지 화질·크기·종횡비 | PC 저장은 전송 완료 처리가 필수다. |
| 메타데이터 | Artist, Copyright, Owner, 날짜/시간 | 촬영 전 적용 시점과 카메라 내부 시계 정책을 정한다. |
| 상태 | BatteryLevel, AvailableShots, LensName, LensStatus | 값이 없거나 읽기 전용일 수 있으므로 표시 실패를 정상 상태로 처리한다. |

캐논 CAP의 기능 목록은 Tv, Av, ISO, WB 등의 촬영 매개변수와 기록 화질·이미지 크기·종횡비,
배터리·저장 매체·장착 렌즈 정보를 주요 설정 범주로 제시한다.
[CAP Camera Settings 기능 목록](https://asia.canon/en/campaign/developerresources/camera/cap/cap)

## 동영상: 라이브 뷰와 녹화 파일을 혼동하지 않는다

동영상 촬영 모드의 라이브 뷰는 미리보기이고, 녹화된 동영상 파일은 카메라 카드에 기록되는
별도 결과물이다. 구버전 캐논 API 참조서는 원격 동영상 시작 전 저장 위치를 카메라로 설정하고
메모리 카드를 삽입해야 한다고 설명한다. 녹화 시작·정지는 `kEdsPropID_Record`로 제어하고,
종료 뒤 새 파일 객체 이벤트를 받아 PC로 전송한다.
[EDSDK API Programming Reference, 원격 동영상 절차](https://downloads.triprism.com/public/%5B%20Steve%20%5D/forTyler/canon%203.4sdk/EDSDK_API%203.4.pdf)

EOS 200D, 200D Mark II, 850D에서 동영상을 다룰 때에는 먼저 카메라를 동영상 촬영 모드로
전환하고, 카드 여유 공간·발열·녹화 시간 제한·현재 화질 설정을 확인한다. SDK가 모드 전환을
허용하는지와 원격 녹화가 가능한지는 실제 EDSDK 버전과 연결 상태에서 검증한다. 확실하지
않은 경우에는 사용자가 카메라의 모드 다이얼을 동영상으로 맞춘 뒤 라이브 뷰와 녹화 명령을
사용하게 하는 것이 안전하다.

## 기능별 승인 시험표

배포 전에 각 기준 기종과 사용 렌즈 조합에서 아래를 한 번씩 시험하고 결과를 남긴다.

| 시험 | 성공 기준 |
|---|---|
| 연결 | 모델명이 의도한 카메라이고 세션이 열린다. |
| 기본 촬영 | AF 또는 MF 조건에서 한 장을 찍고 저장 위치에 파일이 생긴다. |
| PC 전송 | Host/Both에서 파일 크기와 형식이 정상이고 완료·취소 처리가 끝난다. |
| 라이브 뷰 | 시작·프레임 반복 취득·종료 뒤 카메라 화면이 정상으로 돌아온다. |
| AF | 라이브 뷰 AF 요청 뒤 초점 결과를 사용자에게 확인할 수 있다. |
| 원격 초점 구동 | 가까이/멀리 각 단계가 렌즈에서 관찰 가능하고 끝 범위 오류가 나면 반복 요청을 멈춘다. |
| 설정 | Tv·Av·ISO·WB 중 작업에 필요한 값이 허용 목록을 통해 설정되고 재조회 값이 일치한다. |
| 복구 | USB 분리, 카메라 전원 종료, 앱 취소 뒤에도 재연결과 다음 촬영이 가능하다. |

## 빠른 문제 해결표

| 문제 | 가장 가능성 큰 원인 | 해결 순서 |
|---|---|---|
| `EDSDK.dll`은 있는데 카메라가 안 잡힘 | 패키지·비트 수·카메라 점유·USB 문제 | 해당 패키지의 지원 조건 확인 → 다른 캐논 앱 종료 → 직접 USB 연결 → 카메라 재시작 |
| 라이브 뷰 프레임이 없음 | PC 출력 장치 미설정, 속성 반영 전 요청 | `Evf_OutputDevice` 현재값 확인 → PC 비트 추가 → 속성 이벤트/첫 프레임 대기 |
| 화면이 시간이 갈수록 느려짐 | 프레임 큐 누적, 스트림 해제 누락 | 최신 프레임만 유지 → 프레임별 객체 해제 → 표시와 취득 분리 |
| 촬영 뒤 다음 촬영이 안 됨 | PC 전송 완료/취소 누락 | 전송 요청마다 Download 후 Complete 또는 Cancel을 보장 |
| AF가 안 됨 | 렌즈가 MF, 라이브 뷰 꺼짐, AF 방법 미지원 | 렌즈 AF 스위치 → 라이브 뷰 → 현재 AF 속성과 허용값 → 단발 AF 재시험 |
| 원격 초점 구동이 안 됨 | 렌즈·현재 상태 미지원 | 명령 오류를 표시하고 반복 중지 → 물리 초점 링 또는 지원 렌즈로 대체 |
| 동영상 파일이 PC에 없음 | 녹화는 카드에 저장되며 파일 이벤트를 처리하지 않음 | 카드 확인 → 녹화 종료 → 새 파일 객체 이벤트 수신 → 일반 파일 전송 흐름으로 다운로드 |

## 참고문헌과 확인 시점

1. Canon, [Camera API Package Overview](https://asia.canon/en/campaign/developerresources/camera/cap/cap), 2026-08-12 확인.
2. Canon, [EDSDK Release Note](https://asia.canon/en/campaign/developerresources/camera/cap/edsdk-eos-digital-camera-sdk-release-note), 2026-08-12 확인.
3. Canon, [EDSDK compatible camera list](https://developercommunity.usa.canon.com/resource/1670450894000/CDC_EDSDKRAW_Compat_List), 2026-08-12 확인.
4. Canon, [EDSDK API Programming Reference](https://downloads.triprism.com/public/%5B%20Steve%20%5D/forTyler/canon%203.4sdk/EDSDK_API%203.4.pdf), 2016. 공개 구버전 참조서이므로 최신 패키지의 API 문서와 헤더가 최우선이다.
5. andrewrk, [pyedsdk: EDSDKTypes.h](https://github.com/andrewrk/pyedsdk/blob/master/edsdk/EDSDKTypes.h), 2026-08-12 확인. 공개 헤더 사례로만 사용했다.

## 마무리

이 세 DSLR을 EDSDK로 제어할 때 핵심은 명령 하나가 아니라 **상태 전이와 완료 통지**다.
라이브 뷰는 PC 출력 대상 설정 뒤 프레임을 반복 취득하고, 사진은 저장 위치를 정한 뒤
파일 이벤트와 전송 완료까지 처리하며, 초점은 AF 실행과 상대 렌즈 구동을 구분한다. 이
세 흐름을 상태기계로 분리하면 촬영 부스, 제품 검사, 자체 미리보기, 웹캠 영상원 같은
응용에서도 예측 가능한 동작을 만들 수 있다.

[← 5장: 자동초점과 원격 초점 구동](./05-autofocus-and-manual-focus.md) · [목차](./index.md)
