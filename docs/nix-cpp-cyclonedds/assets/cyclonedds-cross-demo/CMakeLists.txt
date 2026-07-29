cmake_minimum_required(VERSION 3.23)

project(
  cyclonedds_cross_demo
  VERSION 1.0.0
  LANGUAGES C CXX
)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(CycloneDDS REQUIRED CONFIG)
find_package(spdlog REQUIRED CONFIG)

add_library(telemetry_type STATIC generated/Telemetry.c)
target_include_directories(telemetry_type PUBLIC "${CMAKE_CURRENT_SOURCE_DIR}/generated")
target_link_libraries(telemetry_type PUBLIC CycloneDDS::ddsc)

function(add_demo_executable target source)
  add_executable(${target} ${source})
  target_link_libraries(${target} PRIVATE telemetry_type spdlog::spdlog)
  target_compile_options(
    ${target}
    PRIVATE
      $<$<COMPILE_LANG_AND_ID:CXX,GNU>:-Wall;-Wextra;-Wpedantic>
  )
endfunction()

add_demo_executable(dds_publisher src/publisher.cpp)
add_demo_executable(dds_subscriber src/subscriber.cpp)

add_custom_target(
  regenerate_idl
  COMMAND
    idlc -l c -o "${CMAKE_CURRENT_SOURCE_DIR}/generated"
    "${CMAKE_CURRENT_SOURCE_DIR}/idl/Telemetry.idl"
  COMMENT "Regenerating the checked-in C type support with the native idlc"
  VERBATIM
)
