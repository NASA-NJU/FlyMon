# FlyMon Control Plane Example

This is a sample code implementation of the FlyMon's control plane, which includes:
```
├── controller_main.py          # ./run_p4_test.py -t ./
├── tmu_task_examples.py        # includes several examples of measurement tasks
└── tmu_utils.py                # includes interfaces to install rules.
```

**NOTE** : since INTEL [Open-Tofino](https://github.com/barefootnetworks/Open-Tofino/tree/master/p4-examples/p4_16_programs/tna_dyn_hashing) has not open-sourced the relevant code of the dynamic hash masking, we temporarily removed this part of the control plane code. Please update SDE to 9.7.0+ and get the sample code.
