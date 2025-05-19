# Downstream Effect of Errors

*Experimental Setup*

In these experiments, we look at the effect of the `tab_err` library errors on machine learning model performance, when perturbing the test set. This simulates target shift.

To summarize the setup, we select a dataset, error rate, error mechanism, and two error types (one string and one numeric so that all columns will be affected). We kept the model constant throughout, using a tree based method (HistGradientBoostedClassifier - works well out of the box cite paper). The output is a dataframe with 10 cross-validation scores for the given metric in the specified experimental setup.

The datasets we run the experiments on are the classification datasets pulled from the TreeBasedMethods paper with the restriction imposed, due to computational resource constraints, that no dataset have more than 100,000 rows and no more than 100 columns. There are 15 classification datasets.


### Notes on the boxplots:

We define "difference in model performance" as: The distributions of the cross validation scores of the evaluation metric of the two scenarios are not identical (as in iid).


*Observations of Results*

The F1 scores of models evaluated on ENAR errored data have the largest variance in the majority of the examined plots. 
The F1 scores of models evaluated on ECAR errored data have the smallest variance in the majority of the examined plots. 
The F1 scores of models evaluated on EAR errored data have variance between the ECAR and ENAR cases in the majority of examined plots.

After running pairwise non-parametric KS tests on the cross validated F1 scores of all selected datasets, we find that at the significance level of $\alpha = 0.05$, there are statistically significant differences in the cross validated F1 score distributions of different error mechanisms.

While the differences in variance between the distributions of F1 scores was more prevalent, an illustrative example of a difference in measures of centrality is the case of dataset_id 44162 with an error rate of 0.25. Here one sees the difference in medians (verify this with a statistical test @ alpha=0.05, too why not).



*Conclusion?*

A difference in variance of cross validation scores indicates that some error mechanisms have a larger effect on the model performance than others. If there is large variance, the model behaves less consistently when the given mechanism is applied. If there is little variance, the model behaves more consistently when the given mechanism is applied. The little variance case is desirable due to the increased confidence in estimates of average model performance. This change in consistency of performance, when all other controllable variables are held constant, is indicative of an effect from the change in error mechanism. That is, different error mechanisms, through difference in model performance consistency, have an effect on overall model performance in downstream machine learning tasks.

Moreover, the variance of model performance on data errored with the ECAR mechanism tends to be smaller indicating that the tree based model used is more robust to the ECAR error mechanism. This could indicate that there is a need to develop models robust to the corruption by the other error mechanisms as they also occur in data.

## To get results, per experiment

1. In `datasets` directory, run `python3 download_datasets.py`

2. In `generate_results`, run python3 <experiment-name>.py

3. Run notebook cells to obtain visualizations.

The results from our experiments are in the results section. 
