#!/bin/bash

if [ ! -n "$1" ] ;then
    echo "you have not input test name"
    exit
fi

PROJECT_SOURCE_DIR=..
TEST=test_$1
TEST_NAME=${1^^}
TEST_SRC=${TEST_NAME^^}_SRC

mkdir -p ${PROJECT_SOURCE_DIR}/test/${TEST_NAME}
touch ${PROJECT_SOURCE_DIR}/test/${TEST_NAME}/${TEST}.cpp

echo "set(${TEST_NAME} ${TEST})" >> ${PROJECT_SOURCE_DIR}/CMakeLists.txt
echo "aux_source_directory(\${PROJECT_SOURCE_DIR}/test/${TEST_NAME} ${TEST_SRC})" >> ${PROJECT_SOURCE_DIR}/CMakeLists.txt
echo "add_executable( \${${TEST_NAME}} \${${TEST_SRC}})" >> ${PROJECT_SOURCE_DIR}/CMakeLists.txt
echo "target_link_libraries(\${${TEST_NAME}} \${LIB_TBC} \${LIB_BOBHASH} \${LIB_COMMON} \${LIB_HOWLOG})" >> ${PROJECT_SOURCE_DIR}/CMakeLists.txt