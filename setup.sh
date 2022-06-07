# ! /bin/bash

mkdir -p ./build && cd ./build

cmake $SDE/p4studio/ \
      -DCMAKE_INSTALL_PREFIX=$SDE_INSTALL \
      -DCMAKE_MODULE_PATH=$SDE/cmake      \
      -DP4_NAME="flymon"               \
      -DP4_PATH=$FLYMON_DIR/p4src/flymon.p4 \
      -DP4FLAGS='--auto-init-metadata'

make flymon -j4 && make install
cd ..
