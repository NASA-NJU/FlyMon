<h1 align="center">
  <br>
  FlyMon
  <br>
</h1>

<h4 align="center">A reference implementation of SIGCOMM'22 Paper <a href="www.google.com" target="_blank">FlyMon</a>.</h4>

<p align="center">
  <a href="#key-features">Key Features</a> •
  <a href="#how-to-use">How To Use</a> •
  <a href="#hardware">Hardware Implementation</a> •
  <a href="#simulation">Simulation Framework</a> •
  <a href="#license">License</a>
</p>

## Key Features

* P4-16 based hardware implementation.
* Jinja2 templates used to generate P4 codes according to variable configurations (e.g., CMU-Groups, Memory Size, Candidate Key Set).
* Several built-in algorithms used to measure various flow attributes.
* A reference control plane framework realizing task reconfiguration, resource management, data collection.
* A simulation framework to fast explore algorithms' accuracy.


## How To Use

### Environment

We implement FlyMon based on P4-16, with the SDE Version 9.7.0. Other versions of SDE (e.g., 9.1.1) can also pass the compilation, but we are unsure if the control plane functions correctly in these older versions.

There are some dependencies for control plane functions. To install them.
```bash
pip install -r ./requirements.txt
```

### Get Started
Below are running steps of the codes.

![Roadmap](docs/roadmap.png)

**Step 1**. Generate a customized FlyMon dataplane and build them.

```bash
python flymon_compiler.py -n 1 
```

The above command will generate two types of files. a) P4-based data plane codes located in [p4src](p4src/). b) Json-based Data plane configurations used to help initialize the control plane interfaces.



## Simulation

### Single CMU-Group Implementation

The main branch is a reference implementation of single CMU-Group, which includes:
* P4-16 codes of the CMU-Group. We implement an additional task registration module and heavy key reporting module.
* A demo control plane which shows how to:
    * dynamically install measurement tasks.
    * dynamically allocate memory with different size.
    * collect deduplicated heavy keys and output to std-out.
    * configure the dynamic hash unit to generate an arbitrary compressed key in the compression stage (temporarily removed, see NOTE2 below). 

### Cross-stacking 9 CMU-Groups

To see the cross-stacking version of FlyMon, please checkout to the `stackable_cmug` branch.

### Strawman Implementation of CMU

To see the strawman solution (without optimizations on key-selection and attribute-operation), please checkout to the `strawman_solution` branch.

**NOTE#1** : for historical reasons, the compression unit (CU) is referred to as the shared compression stage. The execution unit (EU) is referred to as composable measurement unit (CMU). The transformable measurement unit (TMU) is referred to CMU-Group. We are working on refactoring the code to the correct component name.

**NOTE#2** : since INTEL [Open-Tofino](https://github.com/barefootnetworks/Open-Tofino/tree/master/p4-examples/p4_16_programs/tna_dyn_hashing) has not open-sourced the relevant code of the dynamic hash masking, we temporarily removed this part of the control plane code. Please update SDE to 9.7.0+ and get the sample code.
We  also remove `headers.p4` and `utils.p4`, which can be obtained at [Open-Tofino](https://github.com/barefootnetworks/Open-Tofino/tree/master/p4-examples/p4_16_programs/tna_dyn_hashing).

## Simulation

For the convenience of experimentation, we implemented a simulated version of FlyMon in C++ to test algorithms accuracy. Note that the simulation is not a simple implementation of the algorithms with c++. It also uses match-action tables to construct the measurement algorithms, just like the hardware implementation.
In addition, we constructed an automated testing framework to repeat the experiment. The simulation code is located in the [simulations](./simulations) directory.
