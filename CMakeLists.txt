cmake_minimum_required(VERSION 3.5)

project(AdWardQtApp)

set(CMAKE_CXX_STANDARD 11)

find_package(Qt6 COMPONENTS Widgets Network REQUIRED)

set(SOURCES main.cpp mainwindow.cpp adwardapi.cpp)
set(HEADERS mainwindow.h adwardapi.h)

add_executable(${PROJECT_NAME} ${SOURCES} ${HEADERS})

target_link_libraries(${PROJECT_NAME} Qt6::Widgets Qt5::Network)
