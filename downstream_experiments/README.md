# Downstream Effect of Errors

In these experiments, we look at the effect of the `tab_err` library errors on machine learning model performance, when perturbing the test set. This simulates covariate shift.

To summarize the setup, we select a dataset, error rate, error mechanism, and two error types (one string and one numeric so that all columns will be affected). We kept the model constant throughout, using a tree based method (HistGradientBoostedX). The output is a dataframe with 10 cross-validation scores for the given metric in the specified experimental setup.

The datasets we run the experiments on are the classification datasets pulled from the TreeBasedMethods paper with the restriction imposed, due to computational resource constraints, that no dataset have more than 100,000 rows and no more than 100 columns. There are 15 classification datasets.

In the visualizations, we see that there is an effect of error type and mechanism on the distribution of cross validated model performance scores as shown in \[clf_wrongunit\] where the variances and medians are different and \[clf_outlier\] where there is little difference in distributions. 

## To get results, per experiment

1. In `datasets` directory, run `python3 download_datasets.py`

2. In `generate_results`, run python3 <experiment-name>.py

3. Run notebook cells to obtain visualizations.

The results from our experiments are in the results section. 
