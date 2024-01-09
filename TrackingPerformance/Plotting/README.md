### Generating Performance Plots from Fullsim Outputs

To generate performance plots using the outputs from Fullsim, follow these steps. Ensure that you correctly adjust the paths and variables in the provided scripts as needed.

**Merge Reconstruction Outputs:** Start by merging the output from the reconstruction process. Before running the script, set the necessary variables within it to match your configuration.
```
python mergeRecOutputs.py
```

**Produce Root Tree with Desired Variables:** create a root tree with desired variables
```
fccanalysis run analysis_tracking.py 
```

**Plot Fitted Distribution and Generate Performance Plot:** plot the fitted distribution for the chosen variables and generate the performance plot
```
python plots_tracking.py 
```

To generate combined plots using the root outputs. Run the combinedCanvas.py script:
```
python combinedCanvas.py
```
