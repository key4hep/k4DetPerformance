# Generating Performance Plots from Fullsim Outputs

To generate performance plots using the outputs from Fullsim, follow these steps. Ensure that you correctly adjust the paths and variables in the provided scripts as needed.

**Merge Reconstruction Outputs:** Start by merging the output from the reconstruction process. Before running the script, set the necessary variables within it to match your configuration.

```sh
python mergeRecOutputs.py
```

**Produce Root Tree with Desired Variables:** create a root tree with desired variables

```sh
fccanalysis run analysis_tracking.py
```

**Plot Fitted Distribution and Generate Performance Plot:** plot the fitted distribution for the chosen variables and generate the performance plot

```sh
python plots_tracking.py
```

To generate superimposed plots using the root outputs. Run the `SuperimposedCanvas.py` script:

```sh
python SuperimposedCanvas.py
```

## Ratio plots

Use `plots_tracking_sep.py` instead of `plots_tracking.py`, to create root outputs for each theta and momentum

```sh
python plots_tracking_sep.py
```

To generate ratio plots using the root outputs. Run the `SuperimposedCanvas_ratio.py` script, it will generate ratio plots for each variable (theta and momentum) and for Superimposed plots

```sh
python SuperimposedCanvas_ratio.py
```
