Here we include results of profiling the error models from the `tab_err` library.

We used a python memory profiler accessible (here)[https://pypi.org/project/memory-profiler/] and used wall clock timing before and after the call in the code used to profile runtime.

In the `plots` directory, there are 3D plots of both runtime and memory as a function of number of columns and number of rows. There is a separate runtime (or memory) surface for ech of the possible error models (assuming error rates in the set: {0.1, 0.25, 0.5, 0.75, 0.9}).

The memory and runtime profiling results can be obtained with commands such as `poetry run -- src/python time_numeric.py` and `poetry run -- src/python time_string.py`. The resulting files will be generated in the src directory under the names `numeric_times_new.csv` and `string_times_new` respectively.

Our results were obtained from the BHT Berlin compute cluster with CPU utilization of ~1000m on a [cpu from cl-worker11]. As seen in the 3d memory plots, usage never exeeded 32Gb as specified in our runtime environment.

To obtain the plots on new results (or old results though a path change will be needed in the visualize times notebook) simply navigate to the end of the visualize times notebook and run the two final python cells. The resulting plots should display in the notebook and will be generated in the plots directory under the same name as the existing plots except prefixed by "new_".


Paper Prose - super rough:

*Setup*

In creating the plots, we essentially applied the low level API of tab err to each possible combination of error mechanism and type to string and numeric data with error rates from the set {0.1, 0.25, 0.5, 0.75, 0.9}. We then varied the number of rows and number of columns of randomly generated data. These values ranged from 100 to 1,000,000 log scale for the number of rows and 2 to 10 by 2s for the number of columns. Note that a maximum of 2 columns would be affected at any one time, specifically in the case of the EAR error mechanism. After creating the data and the error models, we then applied the low level api, *create errors* function to the data, collecting the wall clock time and the memory using a memory profiler that records the peak memory usage of the process [profiler pypi link]. We repeated this analysis for 100 runs for each combination of error model and artificial dataset and show a few plots of the runtime/memory consumption of the library given 6 error models. Note that there are over 300 runtime and memory surfaces for each combination of error type, mechanism, and rate as a function of number of columns and number of rows available on the github should further analysis be desired. 


*Observations on Plots*

In the plots (log scale) we see that the Typo/Missing Value models increase in both runtime and memory [approximately quadratically - could be plain wrong] as we increase columns/rows exponentially. The green lines are the Typo error type and the blue lines are the Missing Value. The error mechanisms are denoted by the line style. The dotted lines are ECAR, the dashed lines are ENAR, and the solid lines are EAR.


*Conclusion*

When we increase the number of rows exponentially, the runtime also increases exponentially. The same trend can be seen in memory usage too, save a constant shift due to base process memory consumption.

