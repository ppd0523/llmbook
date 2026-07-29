# 6. DDS와 IDL 이해하기

## 학습 목표

- DDS의 핵심 개체와 데이터 흐름을 설명한다.
- IDL이 C++ 프로그램에 연결되는 과정을 이해한다.
- 예제의 QoS와 실행 순서를 설명한다.

## 6.1 DDS는 메시지 브로커가 아니다

DDS(Data Distribution Service)는 데이터를 발행하는 프로그램과 구독하는 프로그램이
서로를 발견하고 통신하는 데이터 중심 미들웨어다. 예제에는 별도의 중앙 브로커가
없다.

```text
DomainParticipant
  └─ Topic: "Telemetry" + tutorial::Telemetry 자료형
       ├─ DataWriter ── 발행
       └─ DataReader ── 구독
```

통신하려면 양쪽의 다음 세 값이 같아야 한다.

1. domain ID
2. topic 이름
3. IDL로 정의한 자료형

이 중 하나라도 다르면 실행 파일은 정상 실행 중이어도 데이터를 받지 못한다.

## 6.2 IDL이 필요한 이유

[`Telemetry.idl`](./assets/cyclonedds-cross-demo/idl/Telemetry.idl)은 네트워크로 보낼
자료형을 언어와 독립적으로 정의한다.

```idl
module tutorial {
  @final
  struct Telemetry {
    unsigned long sample_id;
    long long timestamp_ms;
    string<64> source;
  };
};
```

Cyclone DDS의 `idlc`가 이 파일을 읽어 다음 C 코드를 만든다.

- `Telemetry.h`: `tutorial_Telemetry` 구조체와 type descriptor 선언
- `Telemetry.c`: 직렬화에 필요한 type descriptor 구현

C++ 애플리케이션이지만 Cyclone DDS C API를 사용하므로 생성물도 C 코드다. 이 책은
`cyclonedds-cxx` 바인딩을 사용하지 않는다.

## 6.3 생성 코드를 저장소에 넣는 이유

네이티브 빌드에서는 x86_64용 `idlc`를 실행할 수 있다. 교차 빌드 중에 Conan이 만든
aarch64용 `idlc`를 x86_64 호스트에서 실행하면 `Exec format error`가 발생한다.

따라서 흐름을 둘로 분리한다.

```text
x86_64 idlc 실행 → generated/Telemetry.c, .h 생성 → Git에 함께 기록
                                                     ↓
                                  네이티브·aarch64 빌드에서 컴파일
```

IDL을 바꾸면 생성물도 다시 만들고 같은 변경으로 기록해야 한다.

## 6.4 publisher의 핵심

publisher는 participant와 topic을 만든 다음 writer를 생성한다.

```cpp
const dds_entity_t topic =
    dds_create_topic(participant, &tutorial_Telemetry_desc,
                     "Telemetry", nullptr, nullptr);

dds_qset_reliability(qos, DDS_RELIABILITY_RELIABLE, DDS_SECS(2));
const dds_entity_t writer =
    dds_create_writer(participant, topic, qos, nullptr);
```

전송할 때는 IDL이 만든 구조체를 채우고 `dds_write`를 호출한다.

```cpp
tutorial_Telemetry sample{};
sample.sample_id = index;
sample.timestamp_ms = unix_time_ms();
std::snprintf(sample.source, sizeof(sample.source), "%s", source.c_str());
dds_write(writer, &sample);
```

## 6.5 subscriber의 핵심

subscriber는 같은 topic으로 reader를 만든다. `dds_take`가 반환한 loaned sample은
처리가 끝난 뒤 반드시 `dds_return_loan`으로 돌려준다.

```cpp
void *samples[1] = {nullptr};
dds_sample_info_t information[1]{};
const dds_return_t count =
    dds_take(reader, samples, information, 1, 1);

if (count > 0 && information[0].valid_data) {
  const auto *sample =
      static_cast<const tutorial_Telemetry *>(samples[0]);
  // sample 사용
}

dds_return_loan(reader, samples, count);
```

## 6.6 QoS와 실행 순서

예제는 reliability를 `RELIABLE`로 지정하지만 durability는 기본값인 `VOLATILE`이다.
따라서 subscriber가 발견되기 전에 보낸 과거 샘플을 나중에 다시 받을 수 있다고
가정하면 안 된다. 학습 실습에서는 subscriber를 먼저 시작하고 publisher를 실행한다.

DDS Security와 shared memory는 이 책의 범위에서 제외한다. 네트워크 discovery와
UDP 통신에 집중한다.

## 연습문제

1. publisher와 subscriber의 topic 이름 중 한쪽만 바꾸고 현상을 관찰한다.
2. 서로 다른 domain ID로 실행한 뒤 같은 값으로 맞춘다.
3. `Telemetry.idl`에 온도 필드를 추가하고 어떤 파일을 함께 갱신해야 하는지 적는다.

## 요약

- domain, topic 이름, 자료형이 일치해야 DDS 데이터가 흐른다.
- `idlc` 생성물은 네이티브 호스트에서 만들고 저장소에 포함한다.
- 예제는 Cyclone DDS C API와 reliable·volatile QoS를 사용한다.
