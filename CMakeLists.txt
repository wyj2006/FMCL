cmake_minimum_required(VERSION 4.0.1)

project(FMCL VERSION 4.0.0)

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY_DEBUG "Debug")
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY_RELEASE "Release")

set(CMAKE_C_STANDARD 23)

find_package(Python3 COMPONENTS Interpreter Development)
include_directories(${Python3_INCLUDE_DIRS})
link_libraries(${Python3_LIBRARIES})

add_subdirectory(zip)
include_directories(zip/src)
link_libraries(zip)

add_executable(FMCL)
target_sources(FMCL PUBLIC
    kernel/main.c
)
add_custom_command(
    TARGET
        FMCL
    POST_BUILD
    COMMAND
        ${CMAKE_COMMAND} -E copy_if_different 
            $<TARGET_FILE:Python3::Module> $<TARGET_FILE_DIR:FMCL>
)