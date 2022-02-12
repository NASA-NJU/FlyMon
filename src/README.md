# FlyMon's Data Plane

This is a reference implementation of FlyMon's data plane. The files include:
```
./
├── compression_units.p4    # the shared compression stage.
├── dupkey_filter.p4        # a bloomfilter-based duplicated heavy hitter reporter.
├── execution_units.p4      # refer to composable measurement unit (CMU).
├── main.p4                 # please compile this file.
├── mdata.p4                # define some metadata.
├── reporting_units.p4      # report heavy key to the control plane.
└── task_registers.p4       # register task id.
```
The above implementation  only include one CMU-Group.
* Please checkout to the `stackable_cmug` branch to see the cross-stacking version of FlyMon, which includes 9 CMU-Groups. 
* Please checkout to the `strawman_solution` branch to see the strawman solution.

