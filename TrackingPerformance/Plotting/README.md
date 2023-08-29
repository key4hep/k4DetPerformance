### Generating Performance Plots from Fullsim Outputs

Follow these steps to generate performance plots using the fullsim outputs. Make sure to carefully adjust the paths and variables in the provided scripts:

```
fccanalysis run analysis_stage1.py 
```
```
fccanalysis run analysis_stage2.py 
```
```
fccanalysis final analysis_final.py 
```

After completing the analysis processes, proceed to generate combined plots using the root outputs. Run the combinedCanvas.py script:
```
python combinedCanvas.py
```
