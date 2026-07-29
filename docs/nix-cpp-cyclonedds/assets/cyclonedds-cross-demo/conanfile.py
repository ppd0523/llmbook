from conan import ConanFile
from conan.tools.cmake import cmake_layout


class CycloneDDSCrossDemoConan(ConanFile):
    name = "cyclonedds-cross-demo"
    version = "1.0.0"
    package_type = "application"

    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain", "VirtualBuildEnv", "VirtualRunEnv"

    default_options = {
        "cyclonedds/*:shared": False,
        "cyclonedds/*:with_ssl": False,
        "cyclonedds/*:with_shm": False,
        "cyclonedds/*:enable_security": False,
        "cyclonedds/*:enable_discovery": True,
        "spdlog/*:shared": False,
        "spdlog/*:header_only": False,
        "spdlog/*:use_std_fmt": False,
        "fmt/*:shared": False,
    }

    def requirements(self):
        self.requires("cyclonedds/0.10.2")
        self.requires("spdlog/1.17.0")

    def layout(self):
        cmake_layout(self)
