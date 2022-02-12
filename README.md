# FlyMon Hardware Reference Implementation

This is a reference implementation of FlyMon. The functions include:
* A set of jinja2 template P4 code used to generate data plane codes according to user-defined FlyMon configs.
* A demo control plane which shows how to:
    * An example to install table rules to switch CMU to the frequency attribute.
    * An example to dynamically arrange the SRAM into several parts.
    * Collect bloom-filtered heavy-key digest information and output to std-out.
    * Config the dynamic hash unit to generate an arbitrary key in the compression stage (temporarily removed, see NOTE below). 
* To see the cross-stacking version of FlyMon, please checkout to the `stackable_cmug` branch.
* To see the strawman solution, please checkout to the `strawman_solution` branch.

For historical reasons, the compression unit (CU) is referred to as the shared compression stage. The execution unit (EU) is referred to as composable measurement unit (CMU). The transformable measurement unit (TMU) is referred to CMU-Group. We are working on refactoring the code to the correct component name.

**NOTE** : since INTEL [Open-Tofino](https://github.com/barefootnetworks/Open-Tofino/tree/master/p4-examples/p4_16_programs/tna_dyn_hashing) has not open-sourced the relevant code of the dynamic hash masking, we temporarily removed this part of the control plane code. Please update SDE to 9.7.0+ and get the sample code.
We  also remove `headers.p4` and `utils.p4`, which can be obtained at [Open-Tofino](https://github.com/barefootnetworks/Open-Tofino/tree/master/p4-examples/p4_16_programs/tna_dyn_hashing).



