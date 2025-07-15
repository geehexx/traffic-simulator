workspace(name = "traffic_simulator")

# Use built-in Python rules for Bazel 7.1.1
load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

# Python rules - use a version compatible with Bazel 7.1.1
http_archive(
    name = "rules_python",
    sha256 = "a30abdfc7126d497a7698c29c46ea9901c6392d6ed315171a6df5ce433aa4502",
    strip_prefix = "rules_python-0.6.0",
    url = "https://github.com/bazelbuild/rules_python/archive/0.6.0.tar.gz",
)

# Python toolchain
load("@rules_python//python:repositories.bzl", "py_repositories")
py_repositories()

# Pip dependencies
load("@rules_python//python:pip.bzl", "pip_parse")
pip_parse(
    name = "pip_runtime",
    requirements_lock = "//third_party/pip:runtime_requirements.txt",
)
pip_parse(
    name = "pip_dev",
    requirements_lock = "//third_party/pip:dev_requirements.txt",
)
