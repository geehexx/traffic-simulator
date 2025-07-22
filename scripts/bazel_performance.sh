#!/bin/bash
# Bazel Performance Optimization Script
# This script sets up optimal environment variables for Bazel performance

# Set JVM options for better performance
export BAZEL_JVM_OPTS="-Xmx4g -XX:+UseG1GC -XX:+UseStringDeduplication"

# For fast builds, use more memory
export BAZEL_JVM_OPTS_FAST="-Xmx8g -XX:+UseG1GC -XX:+UseStringDeduplication"

# Function to run Bazel with performance optimizations
bazel_fast() {
    export BAZEL_JVM_OPTS="$BAZEL_JVM_OPTS_FAST"
    bazel "$@" --config=fast
}

# Function to run Bazel with caching
bazel_cache() {
    export BAZEL_JVM_OPTS="$BAZEL_JVM_OPTS"
    bazel "$@" --config=cache
}

# Function to run Bazel with debugging
bazel_debug() {
    export BAZEL_JVM_OPTS="$BAZEL_JVM_OPTS"
    bazel "$@" --config=debug
}

# Function to run performance monitoring
bazel_profile() {
    export BAZEL_JVM_OPTS="$BAZEL_JVM_OPTS"
    bazel run //scripts:bazel_performance_monitor -- "$@"
}

# Main function
main() {
    case "$1" in
        "fast")
            shift
            bazel_fast "$@"
            ;;
        "cache")
            shift
            bazel_cache "$@"
            ;;
        "debug")
            shift
            bazel_debug "$@"
            ;;
        "profile")
            shift
            bazel_profile "$@"
            ;;
        "monitor")
            shift
            bazel run //scripts:bazel_performance_monitor -- "$@"
            ;;
        *)
            echo "Usage: $0 {fast|cache|debug|profile|monitor} [bazel-args...]"
            echo ""
            echo "Commands:"
            echo "  fast     - Run with fast profile (16 jobs, 8GB memory)"
            echo "  cache    - Run with local disk cache"
            echo "  debug    - Run with debug output"
            echo "  profile  - Run performance monitoring"
            echo "  monitor  - Run full performance analysis"
            echo ""
            echo "Examples:"
            echo "  $0 fast build //..."
            echo "  $0 cache test //..."
            echo "  $0 profile --target=//src/traffic_sim:traffic_sim"
            echo "  $0 monitor --benchmark-only"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
