cmake_minimum_required(VERSION 4.0.1)

project(FMCL VERSION 4.0.0)

find_package(Boost REQUIRED CONFIG COMPONENTS filesystem thread json container log system process)
include_directories(${Boost_INCLUDE_DIRS})
link_libraries(${Boost_LIBRARIES})

add_subdirectory(lib)

file(GLOB_RECURSE KERNEL_SOURCES CONFIGURE_DEPENDS "kernel/*.cpp")

add_executable(FMCL)
target_include_directories(FMCL PUBLIC "kernel")
target_include_directories(FMCL PUBLIC ${FMCLLib_INCLUDE_DIRS})
target_sources(FMCL PUBLIC ${KERNEL_SOURCES})
target_link_libraries(FMCL FMCLLib)