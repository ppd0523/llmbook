# 6. DDS와 IDL 이해하기

## 학습 목표

- DDS의 핵심 개체와 데이터 흐름을 설명한다.
- IDL이 C++ 프로그램에 연결되는 과정을 이해한다.
- 예제의 QoS와 실행 순서를 설명한다.
- publisher와 subscriber의 명령행 인자를 읽는다.

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

type descriptor는 자료형의 필드 구성을 Cyclone DDS runtime이 읽을 수 있는 형태로 적어 둔
자료다. 통신 상대가 같은 자료형을 쓰는지 판단하는 근거이기도 하다.

C++ 애플리케이션이지만 Cyclone DDS C API를 사용하므로 생성물도 C 코드다. 이 책은
`cyclonedds-cxx` 바인딩을 사용하지 않는다. `string<64>`는 C에서 `char source[65]`로
매핑된다. 64자와 문자열 종단 문자 하나를 합한 크기다.

## 6.3 생성 코드를 저장소에 넣는 이유

네이티브 빌드에서는 x86_64용 `idlc`를 실행할 수 있다. 교차 빌드에서는 그렇지 않다. Conan이
Cyclone DDS를 교차 빌드할 때 함께 만드는 `idlc`는 host 플랫폼용, 즉 aarch64 바이너리다. 이
파일을 x86_64 개발 PC에서 실행하면 `Exec format error`가 발생한다.

따라서 흐름을 둘로 분리한다.

```text
x86_64 idlc 실행 → generated/Telemetry.c, .h 생성 → Git에 함께 기록
                                                     ↓
                                  네이티브·aarch64 빌드에서 컴파일
```

5.5의 `regenerate_idl` target이 기본 빌드에 포함되지 않는 이유가 이것이다. 생성은
네이티브 셸에서 사람이 한 번 수행하고, 빌드는 기록된 결과를 컴파일하기만 한다. IDL을
바꾸면 생성물도 다시 만들고 같은 변경으로 기록해야 한다.

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

`tutorial_Telemetry_desc`가 6.2에서 말한 type descriptor다. topic 이름 `"Telemetry"`와
이 descriptor 두 가지가 subscriber와 맞아야 한다.

전송할 때는 IDL이 만든 구조체를 채우고 `dds_write`를 호출한다.

```cpp
tutorial_Telemetry sample{};
sample.sample_id = index;
sample.timestamp_ms = unix_time_ms();
std::snprintf(sample.source, sizeof(sample.source), "%s", source.c_str());
dds_write(writer, &sample);
```

`source`는 고정 크기 배열이므로 `std::snprintf`로 길이를 제한해 채운다.

## 6.5 subscriber의 핵심

subscriber는 같은 topic으로 reader를 만든다. `dds_take`가 반환한 sample은 Cyclone DDS가
빌려준 메모리(loaned sample)이므로, 처리가 끝난 뒤 반드시 `dds_return_loan`으로 돌려준다.

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

`valid_data`를 먼저 보는 이유는 `dds_take`가 데이터 없이 상태 변화만 알리는 sample도
반환할 수 있기 때문이다.

## 6.6 QoS와 실행 순서

예제는 reliability를 `RELIABLE`로 지정하지만 durability는 기본값인 `VOLATILE`이다.
`RELIABLE`은 양쪽이 서로를 발견한 뒤의 전달을 보장할 뿐이고, `VOLATILE`은 발견 이전에
보낸 샘플을 보관하지 않는다는 뜻이다. 따라서 subscriber가 발견되기 전에 보낸 과거 샘플을
나중에 다시 받을 수 있다고 가정하면 안 된다. 학습 실습에서는 subscriber를 먼저 시작하고
publisher를 실행한다.

DDS Security와 shared memory는 이 책의 범위에서 제외한다. 4.2에서 두 옵션을 끈 것과 같은
결정이다. 네트워크 discovery와 UDP 통신에 집중한다.

## 6.7 두 프로그램의 명령행 인터페이스

7장부터는 두 실행 파일을 인자와 함께 실행한다. 인자는 모두 위치 인자이며 생략하면
기본값을 쓴다.

`dds_publisher`:

| 위치 | 이름 | 뜻 | 기본값 |
|---|---|---|---|
| 1 | `count` | 보낼 샘플 개수 | 10 |
| 2 | `interval_ms` | 샘플 사이 간격(밀리초) | 500 |
| 3 | `domain_id` | DDS domain ID | `DDS_DOMAIN_DEFAULT` |
| 4 | `source` | 샘플의 `source` 필드에 넣을 이름 | `publisher` |

`dds_subscriber`:

| 위치 | 이름 | 뜻 | 기본값 |
|---|---|---|---|
| 1 | `expected_count` | 받기를 기다릴 샘플 개수 | 10 |
| 2 | `timeout_seconds` | 기다릴 최대 시간(초) | 20 |
| 3 | `domain_id` | DDS domain ID | `DDS_DOMAIN_DEFAULT` |

두 프로그램의 첫 두 인자는 이름이 다르다. publisher의 첫 인자는 보낼 개수, subscriber의
첫 인자는 기다릴 개수다. 실습에서 값을 맞추어 주면 subscriber가 다 받고 정상 종료한다.
세 번째 인자 `domain_id`는 양쪽이 같아야 하며, 앞의 인자를 생략한 채 뒤의 인자만 줄 수는
없다.

`DDS_DOMAIN_DEFAULT`는 domain ID를 프로그램이 정하지 않고 설정 파일의 값을 따르겠다는
뜻이다. 설정 파일이 없으면 기본 domain을 쓴다. 인자를 주지 않은 publisher와 subscriber가
서로 통신하는 것은 둘 다 같은 기본값을 따르기 때문이다.

subscriber는 기다린 개수를 모두 받으면 `received all 10 samples` 형태의 줄을 남기고 0으로
종료하고, 제한 시간 안에 다 받지 못하면 `timed out: received N of M samples`를 남기고
실패로 종료한다. 7장과 9장의 통신 확인은 이 종료 조건을 판정 기준으로 쓴다.

## 직접 확인

1. publisher와 subscriber의 topic 이름 중 한쪽만 바꾸고 현상을 관찰한다.
2. 서로 다른 domain ID로 실행한 뒤 같은 값으로 맞춘다. 세 번째 인자를 주려면 앞의 두
   인자도 함께 적어야 한다.
3. `Telemetry.idl`에 온도 필드를 추가하고 어떤 파일을 함께 갱신해야 하는지 적는다.

## 요약

- domain, topic 이름, 자료형이 일치해야 DDS 데이터가 흐른다.
- `idlc` 생성물은 네이티브 호스트에서 만들고 저장소에 포함한다.
- 예제는 Cyclone DDS C API와 reliable·volatile QoS를 사용한다.
- 두 프로그램은 위치 인자로 샘플 수, 시간, domain ID를 받는다.
