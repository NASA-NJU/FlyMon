# ! /bin/bash

if [ $SDE ];then
	echo "SDE = $SDE"
else
	echo "ERROR! SDE IS NOT SET"
      exit 1
fi

if [ $SDE_INSTALL ];then
	echo "SDE_INSTALL = $SDE_INSTALL"
else
	echo "ERROR! SDE_INSTALL IS NOT SET"
      exit 1
fi

if [ $FLYMON_DIR ];then
	echo "FLYMON_DIR = $FLYMON_DIR"
else
	echo "ERROR! FLYMON_DIR IS NOT SET"
      exit 1
fi

mkdir -p ./build && cd ./build

cmake $SDE/p4studio/ \
      -DCMAKE_INSTALL_PREFIX=$SDE_INSTALL \
      -DCMAKE_MODULE_PATH=$SDE/cmake      \
      -DP4_NAME="flymon"               \
      -DP4_PATH=$FLYMON_DIR/p4src/flymon.p4 \
      -DP4FLAGS='--auto-init-metadata'

make flymon -j4 && make install
cd ..
