cmake_minimum_required(VERSION 3.20)
project(telemetry_engine LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

find_package(pybind11 CONFIG REQUIRED)

include_directories(include)

add_library(telemetry_core STATIC src/kalman_filter.cpp)

pybind11_add_module(telemetry_engine_cpp python/binding.cpp)
target_link_libraries(telemetry_engine_cpp PRIVATE telemetry_core pybind11::module)
