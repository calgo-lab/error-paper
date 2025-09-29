# Integrity Contstraint Baseline

In this section of the repository, we examine another error generation tool, namely BART. This tool is used for creating errors with functional dependencies in a fashion different than that of tab-err.

In `/postgresql-setup` there is a file `BART_Utilization_Documentation.txt` which explains how to set up BART in a cluster environment. Note that BART itself runs on an SQL backend so the relevant details are towards the end. Other details pertaining to the postgresql database are included for transparency. One must also clone the BART repository separately to utilize the tool.

In `/output` there are various .csv files associated with 3 separate BART runs as well as tab-err. This was done in order to do analysis.

In `/analysis` there are 3 jupyter notebooks. The first, `make-tab-err-datasets.ipynb` allows the user to create the datasets using tab-err. The second, `analysis-and-comparison.ipynb` explores the datasets perturbed by tab-err and BART. Thereinone can find error generation statistics as well as exploratory visualizations. The final notebook, `clean-analysis.ipynb` is a shortened version of `analysis-and-comparison.ipynb` that focuses on the plot included in the paper from these experiments.