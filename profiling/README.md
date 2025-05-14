Here we include results of profiling the error models from the `tab_err` library.

We used a python memory profiler accessible (here)[https://pypi.org/project/memory-profiler/] and used wall clock timing before and after the call in the code used to profile runtime.

In the `plots` directory, there are 3D plots of both runtime and memory as a function of number of columns and number of rows. There is a separate runtime (or memory) surface for ech of the possible error models (assuming error rates in the set: {0.1, 0.25, 0.5, 0.75, 0.9}).

The memory and runtime profiling results can be obtained with commands such as `poetry run -- src/python time_numeric.py` and `poetry run -- src/python time_string.py`. The resulting files will be generated in the src directory under the names `numeric_times_new.csv` and `string_times_new` respectively.

Our results were obtained from the BHT Berlin compute cluster with CPU utilization of ~1000m on a [cpu from cl-worker11]. As seen in the 3d memory plots, usage never exeeded 32Gb as specified in our runtime environment.

To obtain the plots on new results (or old results though a path change will be needed in the visualize times notebook) simply navigate to the end of the visualize times notebook and run the two final python cells. The resulting plots should display in the notebook and will be generated in the plots directory under the same name as the existing plots except prefixed by "new_".
