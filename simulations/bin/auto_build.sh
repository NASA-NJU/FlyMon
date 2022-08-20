#! /bin/bash
#cmake .. -DCMAKE_CXX_FLAGS=-pg
cd ../build
cmake ..
make
cd -
exit 0
