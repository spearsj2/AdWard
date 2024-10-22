cmake_minimum_required(VERSION 3.5)

project(PiHoleQtApp)

set(CMAKE_CXX_STANDARD 11)

find_package(Qt6 COMPONENTS Widgets Network REQUIRED)

set(SOURCES main.cpp mainwindow.cpp piholeapi.cpp)
set(HEADERS mainwindow.h piholeapi.h)

add_executable(${PROJECT_NAME} ${SOURCES} ${HEADERS})

target_link_libraries(${PROJECT_NAME} Qt6::Widgets Qt5::Network)
