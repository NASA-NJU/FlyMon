# FlyMon Hardware Reference Implementation

This is a reference implementation of FlyMon. The repository includes P4 hardware implementations and CPU simulations for algorithms accuracy.

## P4 Implemenatation
We implement FlyMon based on P4-16, with the SDE Version 9.7.0. We opensource three versions of Flymon:

**Single CMU-Group**

The main branch is a reference implementation of single CMU-Group, which includes:
* P4-16 codes of the CMU-Group. We implement an additional task registration module and heavy key reporting module.
* A demo control plane which shows how to:
    * dynamically install measurement tasks.
    * dynamically allocate memory with different size.
    * collect deduplicated heavy keys and output to std-out.
    * configure the dynamic hash unit to generate an arbitrary compressed key in the compression stage (temporarily removed, see NOTE2 below). 

**Cross-stacking 9 CMU-Groups**

To see the cross-stacking version of FlyMon, please checkout to the `stackable_cmug` branch.

**Strawman Implementation of CMU**

To see the strawman solution (without optimizations on key-selection and attribute-operation), please checkout to the `strawman_solution` branch.

**NOTE#1** : for historical reasons, the compression unit (CU) is referred to as the shared compression stage. The execution unit (EU) is referred to as composable measurement unit (CMU). The transformable measurement unit (TMU) is referred to CMU-Group. We are working on refactoring the code to the correct component name.

**NOTE#2** : since INTEL [Open-Tofino](https://github.com/barefootnetworks/Open-Tofino/tree/master/p4-examples/p4_16_programs/tna_dyn_hashing) has not open-sourced the relevant code of the dynamic hash masking, we temporarily removed this part of the control plane code. Please update SDE to 9.7.0+ and get the sample code.
We  also remove `headers.p4` and `utils.p4`, which can be obtained at [Open-Tofino](https://github.com/barefootnetworks/Open-Tofino/tree/master/p4-examples/p4_16_programs/tna_dyn_hashing).

## Simulation

For the convenience of experimentation, we implemented a simulated version of FlyMon in C++ to test algorithms accuracy. Note that the simulation is not a simple implementation of the algorithms with c++. It also uses match-action tables to construct the measurement algorithms, just like the hardware implementation.
The simulation code is located in the [simulations](./simulations) directory.
