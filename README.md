# FlyMon Hardware Reference Implementation

This is a reference implemetation of FlyMon. The functions include:
* A set of jinja2 template P4 code used generate data plane codes according to user-defined FlyMon' configs.
* A demo control plane which show how to:
    * [Temporarily Removed] Config the dynamic hash unit to generate arbitrary key in compression stage. 
    * An example to install table rules to switch CMU to the frequency attribute.
    * An example to dynamically arrange the SRAM into several parts.
    * Collect bloom-filtered heavy-key digest infomation and output to std-out.
The above codes cover most of the features refered in the paper, and we will add more tasks as soon as possible.

> [Note 1] Since INTEL [Open-Tofino](https://github.com/barefootnetworks/Open-Tofino/tree/master/p4-examples/p4_16_programs/tna_dyn_hashing) has not open source the relevant code of the dynamic hash masking, we temporarily removed this part of the control plane code. Please update SDE to 9.7.0+ and get the sample code.
> [Note 2] We delete headers.p4 and utils.p4, which can be obtained at [Open-Tofino](https://github.com/barefootnetworks/Open-Tofino/tree/master/p4-examples/p4_16_programs/tna_dyn_hashing).

For historical reasons, the compression unit (CU) is refered to the shared compression stage. The execution unit (eu) is refered to composable measurement unit (CMU). The transformable measurement unit (TMU) is refered to CMU-Group.

* To see the cross-stacking version of FlyMon, please checkout to the `stackable_cmug` branch.
* To see the strawman solution, please checkout to the `strawman solution` branch.

We will open source the full sample code, including the compiler for template code, when needed (and authorized).