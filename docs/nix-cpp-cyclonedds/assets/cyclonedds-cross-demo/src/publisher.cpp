#include <dds/dds.h>
#include <spdlog/spdlog.h>

#include <chrono>
#include <cstdio>
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

std::int64_t unix_time_ms() {
  return std::chrono::duration_cast<std::chrono::milliseconds>(
             std::chrono::system_clock::now().time_since_epoch())
      .count();
}

} // namespace

int main(int argc, char **argv) {
  try {
    const int count = argc > 1 ? parse_positive(argv[1], "count") : 10;
    const int interval_ms =
        argc > 2 ? parse_positive(argv[2], "interval_ms") : 500;
    const std::uint32_t domain_id =
        argc > 3 ? parse_domain(argv[3]) : DDS_DOMAIN_DEFAULT;
    const std::string source = argc > 4 ? argv[4] : "publisher";

    const dds_entity_t participant =
        dds_create_participant(domain_id, nullptr, nullptr);
    require_entity(participant, "dds_create_participant");

    const dds_entity_t topic =
        dds_create_topic(participant, &tutorial_Telemetry_desc,
                         "Telemetry", nullptr, nullptr);
    require_entity(topic, "dds_create_topic");

    dds_qos_t *qos = dds_create_qos();
    dds_qset_reliability(qos, DDS_RELIABILITY_RELIABLE, DDS_SECS(2));
    const dds_entity_t writer = dds_create_writer(participant, topic, qos, nullptr);
    dds_delete_qos(qos);
    require_entity(writer, "dds_create_writer");

    spdlog::info("publisher ready: domain={}, count={}, interval={} ms",
                 domain_id, count, interval_ms);
    spdlog::info("start the subscriber first when using volatile durability");

    for (int index = 1; index <= count; ++index) {
      tutorial_Telemetry sample{};
      sample.sample_id = static_cast<std::uint32_t>(index);
      sample.timestamp_ms = unix_time_ms();
      std::snprintf(sample.source, sizeof(sample.source), "%s", source.c_str());

      require_status(dds_write(writer, &sample), "dds_write");
      spdlog::info("sent sample_id={} source={}", sample.sample_id, source);
      std::this_thread::sleep_for(std::chrono::milliseconds(interval_ms));
    }

    require_status(dds_delete(participant), "dds_delete");
    return EXIT_SUCCESS;
  } catch (const std::exception &error) {
    spdlog::error("publisher failed: {}", error.what());
    return EXIT_FAILURE;
  }
}
