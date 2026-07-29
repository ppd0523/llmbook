#include <dds/dds.h>
#include <spdlog/spdlog.h>

#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <exception>
#include <stdexcept>
#include <string>
#include <thread>

#include "Telemetry.h"

namespace {

int parse_positive(const char *value, const char *name) {
  const int parsed = std::stoi(value);
  if (parsed <= 0) {
    throw std::invalid_argument(std::string{name} + " must be positive");
  }
  return parsed;
}

std::uint32_t parse_domain(const char *value) {
  const unsigned long parsed = std::stoul(value);
  if (parsed > 232) {
    throw std::out_of_range("domain_id must be in the range 0..232");
  }
  return static_cast<std::uint32_t>(parsed);
}

void require_entity(dds_entity_t entity, const char *operation) {
  if (entity < 0) {
    throw std::runtime_error(
        std::string{operation} + ": " + dds_strretcode(-entity));
  }
}

void require_status(dds_return_t status, const char *operation) {
  if (status < 0) {
    throw std::runtime_error(
        std::string{operation} + ": " + dds_strretcode(-status));
  }
}

} // namespace

int main(int argc, char **argv) {
  try {
    const int expected =
        argc > 1 ? parse_positive(argv[1], "expected_count") : 10;
    const int timeout_seconds =
        argc > 2 ? parse_positive(argv[2], "timeout_seconds") : 20;
    const std::uint32_t domain_id =
        argc > 3 ? parse_domain(argv[3]) : DDS_DOMAIN_DEFAULT;

    const dds_entity_t participant =
        dds_create_participant(domain_id, nullptr, nullptr);
    require_entity(participant, "dds_create_participant");

    const dds_entity_t topic =
        dds_create_topic(participant, &tutorial_Telemetry_desc,
                         "Telemetry", nullptr, nullptr);
    require_entity(topic, "dds_create_topic");

    dds_qos_t *qos = dds_create_qos();
    dds_qset_reliability(qos, DDS_RELIABILITY_RELIABLE, DDS_SECS(2));
    const dds_entity_t reader = dds_create_reader(participant, topic, qos, nullptr);
    dds_delete_qos(qos);
    require_entity(reader, "dds_create_reader");

    spdlog::info("subscriber ready: domain={}, expected={}, timeout={} s",
                 domain_id, expected, timeout_seconds);

    int received = 0;
    const auto deadline =
        std::chrono::steady_clock::now() + std::chrono::seconds(timeout_seconds);

    while (received < expected && std::chrono::steady_clock::now() < deadline) {
      void *samples[1] = {nullptr};
      dds_sample_info_t information[1]{};
      const dds_return_t count = dds_take(reader, samples, information, 1, 1);
      require_status(count, "dds_take");

      if (count == 0) {
        std::this_thread::sleep_for(std::chrono::milliseconds(20));
        continue;
      }

      if (information[0].valid_data) {
        const auto *sample =
            static_cast<const tutorial_Telemetry *>(samples[0]);
        spdlog::info("received sample_id={} timestamp_ms={} source={}",
                     sample->sample_id, sample->timestamp_ms, sample->source);
        ++received;
      }

      require_status(dds_return_loan(reader, samples, count),
                     "dds_return_loan");
    }

    require_status(dds_delete(participant), "dds_delete");

    if (received != expected) {
      spdlog::error("timed out: received {} of {} samples", received, expected);
      return EXIT_FAILURE;
    }

    spdlog::info("received all {} samples", received);
    return EXIT_SUCCESS;
  } catch (const std::exception &error) {
    spdlog::error("subscriber failed: {}", error.what());
    return EXIT_FAILURE;
  }
}
