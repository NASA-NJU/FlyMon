# FlyMon Simulation

This is the simulation implementation part of flymon. We have implemented related measurement algorithms based on CMU-Groups. In addition, we constructed an automated testing framework to repeat the experiment.

## File Description

* `include/tbc` contains the simulation of the CMU-Groups and builds a set of table structures, which can be configured as many measurement algorithms (in `include/tbc_manager.h`).
* The other files in `include/` includes other measurement algorithms and utilts.
* `test/` contains test use cases to evaluate algorithms with [WIDE](http://mawi.wide.ad.jp/mawi/) traces. The main test cases are:
    * `TBC_BEAUCOUP_XXX` tests FlyMon-based BeauCoup.
    * `TBC_BLOOMFILTER` tests FlyMon-based BloomFilter.
    * `TBC_CMSketch` and `TBC_CUSketch` tests FlyMon-based Count-min Sketch and SuMax(Sum).
    * `TBC_HYPERLOGLOG` tests FlyMon-based HyperLogLog.
    * `TBC_MAX_TABBLE` tests FlyMon-based SuMax(Max).
    * `TBC_MRAC` tests FlyMon-based MRAC.
    * `BeauCoup` tests original BeauCoup algorithm.
* `test_xxx.py` are scripts to automate test measurement algorithms.

## Get Started

Below we show how to perform the test. Firstly, build the code.

```bash
cd /path/to/simuations
mkdir -p ./build
cd build; cmake ..; make -j 2; cd ..
```

> ⚠️ It needs to support C++17 on your system. Out gcc version is 8.4.0





## 

```bash
python test_xxxx.py
```

---

**NOTE** : for historical reasons, the Transformable Measurement Block (TBC) is referred to as composable measurement unit (CMU).