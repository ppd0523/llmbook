"""Installation metadata for the Ball-on-Plate Isaac Lab extension."""

from pathlib import Path

from setuptools import find_packages, setup


PACKAGE_ROOT = Path(__file__).parent

setup(
    name="ball_on_plate_lab",
    version="0.1.0",
    description="Isaac Lab 3.0 Ball-on-Plate learning task",
    packages=find_packages(),
    include_package_data=True,
    package_data={"ball_on_plate_lab": ["assets/**/*", "config/*.toml"]},
    python_requires=">=3.12",
    install_requires=["gymnasium"],
    zip_safe=False,
)
