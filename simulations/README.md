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
cd /path/to/simuations
mkdir -p ./build
cd build; cmake ..; make -j; cd ..
```

After the project has been compiled, we can prepare it for testing. We give a simple parallelized test framework for repeating the experiments.

```bash
python test_all.py -d ./ -r 3
```

The above script automatically parallelizes the execution of all the accuracy test code.
The `-r` parameter means how many times each set of parameters is repeated.

It took about 3~5 hours to complete the above tests. When all tests are completed, you can view the results in the [results](./results/) directory. 
We prepared a snapshot of the results from our early experiments in the [result_snapshot](./result_snapshot) directory. 
The output results are saved in CSV format. 
We explain the meaning of the output in the first line of the csv files in the result snapshot.

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
