workspace(name = "traffic_simulator")

# Use built-in Python rules for Bazel 7.1.1
load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

# Python rules - use a version compatible with Bazel 7.1.1
http_archive(
    name = "rules_python",
    sha256 = "be04b635c7be4604be1ef20542e9870af3c49778ce841ee2d92fcb42f9d9516a",
    strip_prefix = "rules_python-0.35.0",
    url = "https://github.com/bazelbuild/rules_python/releases/download/0.35.0/rules_python-0.35.0.tar.gz",
)

# Python toolchain
load("@rules_python//python:repositories.bzl", "python_register_toolchains")
python_register_toolchains(
    name = "python3_12",
    python_version = "3.12",
)

# Note: Using simplified dependency management
# Test dependencies are installed in virtual environment
