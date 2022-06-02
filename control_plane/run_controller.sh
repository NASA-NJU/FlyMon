PYEXE=`which python`
PYPYTH=$SDE/install/lib/python3.8/site-packages/bf-ptf
PYPYTH=${PYPYTH}:$SDE/install/lib/python3.8/site-packages/${USER}testutils
PYPYTH=${PYPYTH}:$SDE/install/lib/python3.8/site-packages/tofinopd
PYPYTH=${PYPYTH}:$SDE/install/lib/python3.8/site-packages/tofino
PYPYTH=${PYPYTH}:$SDE/install/lib/python3.8/site-packages
PYPYTH=${PYPYTH}:$SDE/install/lib/python3.8/site-packages/tofino/bfrt_grpc

sudo PYTHONPATH=${PYPYTH} $PYEXE controller_main.py
