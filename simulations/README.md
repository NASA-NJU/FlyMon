# FlyMon Simulation

This is the simulation implementation part of flymon. We have implemented related measurement algorithms based on CMU-Groups. In addition, we constructed an automated testing framework to repeat the experiments.

## Get Started

Below we show how to perform the tests. 

### Requirements

* gcc version 9.4.0
* cmake version 3.16.3
* python

### Download Traces

Our packet trace is download from [the MAWI Working Group of the WIDE Project](http://mawi.wide.ad.jp/mawi/). 
We preprocessed the trace according to the period (e.g., 15s and 30s) and kept only the information related to the flows (i.e., 5-tuple).
Here is a [guide](./data/README.md) to download these pre-processed traces.

### Build Project

You can use cmake to build our project easily.

> ⚠️ It needs to support C++17 on your system. Our gcc version is 8.4.0. You also need to check your CMAKE version.

```bash
cd ~/FlyMon/simulations
mkdir -p ./build
cd build; cmake ..; make -j; cd ..
```

After the project has been compiled, we can prepare it for testing. We give a simple test framework for repeating the experiments.

```bash
python test_all.py -d ./ -r 3 -m sample
```

The above script automatically executes all the accuracy test code.
The `-d` parameter means the work directory of the simulations.
The `-r` parameter means how many times each set of parameters is repeated.
The `-m` parameter indicates which sets of memory configurations to measure (i.e., mode).

This script provides two mode for testing : 

* The `all` mode tests the accuracy of the algorithms under all the memory configurations in the paper. It will cost about **25 hours** to complete. 
* The `sample` mode tests the accuracy under a sample of memory configurations. 

Look at the `test_all.py` to see the difference between their memory configurations.
 
When all tests are completed, you can view the results in the [result](./result/) directory. We also provide [a snapshot of the test results](./result_snapshot/) under all memory configurations (i.e., the `all` mode), which also contains the explanation of the CSV files' columns.

## File Description

> 🔔 For historical reasons, the Transformable Measurement Block (TBC) is referred to as Composable Measurement Unit (CMU).

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
* `scripts/test_xxx.py` are scripts to automate test measurement algorithms.

