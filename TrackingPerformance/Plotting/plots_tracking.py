import ROOT
import numpy as np
import os

ROOT.gStyle.SetOptFit(1111)
# Define marker styles and colors
marker_styles = [ROOT.kOpenTriangleUp, ROOT.kOpenSquare, ROOT.kOpenDiamond, ROOT.kOpenCross, ROOT.kOpenCircle]
colors = [ROOT.kBlue, ROOT.kRed, ROOT.kMagenta, ROOT.kGreen, ROOT.kBlack] 
ROOT.gROOT.SetBatch(True)  # Run ROOT in batch mode to avoid displaying the plot
canvas_width = 900  # Width of the canvas in pixels
canvas_height = 800  # Height of the canvas in pixels
plot_margin_left = 0.15  # Margin from the left side of the canvas
plot_margin_bottom = 0.15  # Margin from the bottom of the canvas
plot_width = 0.09  # Width of the plot within the canvas
plot_height = 0.09  # Height of the plot within the canvas

# Lists of parameters
ParticleList = ["mu"]#, "e", "pi"]
ThetaList = ["10", "20", "30", "40", "50", "60", "70", "80", "89"]
#MomentumList = ["1", "10", "100"]
MomentumList = ["1", "2", "5", "10", "20", "50", "100", "200"]
DetectorModel = ["CLD_o3_v01"]  #["FCCee_o1_v04"]  ["CLD_o2_v05"]  ["CLD_o3_v01"]
Nevts = "10000"

stackMomentumList = ["1", "10", "100"]
#stackThetaList = ["80","89"]
stackThetaList = ["10", "30", "50", "70", "89"]

def pname(particle, theta, momentum):
    return f"{particle}_{theta}deg_{momentum}GeV_{Nevts}evts"

processList = {pname(particle, theta, momentum):{} for particle in ParticleList for theta in ThetaList for momentum in MomentumList}

outputDir = f"/eos/user/g/gasadows/Output/TrackingPerformance/{DetectorModel[0]}/analysis/plots"

inputDir = f"/eos/user/g/gasadows/Output/TrackingPerformance/{DetectorModel[0]}/analysis/"

# Create outputDir if it does not exist
if not os.path.exists(outputDir):
    os.makedirs(outputDir)

residualList = ["d0", "z0", "phi0", "omega", "tanLambda", "phi", "theta"]
specialList = ["pt", "p"]

varList = [f"delta_{v}" for v in residualList] + [f"sdelta_{v}" for v in specialList]

title = {
    "delta_d0": "#sigma(#Deltad_{0}) [#mum]",
    "delta_z0": "#sigma(#Deltaz_{0}) [#mum]",
    "delta_phi0": "#Delta#phi_{0}",
    "delta_omega": "#Delta#Omega",
    "delta_tanLambda": "tan #Lambda",
    "delta_phi": "#sigma(#Delta#phi) [mrad]",
    "delta_theta": "#sigma(#Delta#theta) [mrad]",
    "sdelta_pt": "#sigma(#Deltap_{T}/p_{T,true}^{2}) [GeV^{-1}]",
    "sdelta_p": "#sigma(#Deltap/p_{true}^{2}) [GeV^{-1}]",
}

unit_scale = {
    "delta_d0": 1e3,
    "delta_z0": 1e3,
    "delta_phi0": 1.0,
    "delta_omega": 1.0,
    "delta_tanLambda": 1.0,
    "delta_phi": 1e3,
    "delta_theta": 1e3,
    "sdelta_pt": 1.0,
    "sdelta_p": 1.0,
}

def filter_data_std(data, threshold, n_selections):
    filtered_data = data
    for _ in range(n_selections):
        mean = np.mean(filtered_data)
        std = np.std(filtered_data)
        filtered_data = [d for d in filtered_data if abs(d - mean) < threshold * std]
    return filtered_data

df = {}
var_col_rp = {}
# get column for each variable by running event loop once
for p in processList:
    df[p] = ROOT.RDataFrame("events", f"{inputDir}/{p}.root")
    for v in specialList:
        df[p] = df[p].Define(f"sdelta_{v}", f"delta_{v} / (true_{v} * true_{v})")
    var_col_rp[p] = {}
    for v in varList:
        var_col_rp[p][v] = df[p].Take["double"](v)

var_col = {}
var_low = {}
var_high = {}
h = {}  
# get bin borders and run again to make histograms
for p in processList:
    var_col[p] = {}
    var_low[p] = {}
    var_high[p] = {}
    h[p] = {}
    for v in varList:
        var_col[p][v] = sorted(var_col_rp[p][v].GetValue())
        # Adjust the filtering parameters here
        threshold = 2.5  # Adjust the threshold value 
        n_selections = 3  # Adjust the number of selections 
        var_col[p][v] = filter_data_std(var_col[p][v], threshold, n_selections)
        
        # Recalculate var_low and var_high after filtering
        var_low[p][v] = min(var_col[p][v])
        var_high[p][v] = max(var_col[p][v])
        
        h[p][v] = (df[p]
                   .Filter(f"{v} > {var_low[p][v]} && {v} < {var_high[p][v]}")
                   .Histo1D((v, f"{p};{title[v]}", 200, var_low[p][v], var_high[p][v]), v)
                    )

# After both runs do fits and make plots
mean = {}
mean_err = {}
sigma = {}
sigma_err = {}
for p in processList:
    fname = f"{outputDir}/{p}.pdf"
    root_fname = ROOT.TFile(f"{outputDir}/{p}.root", "RECREATE")
    mean[p] = {}
    mean_err[p] = {}
    sigma[p] = {}
    sigma_err[p] = {}
    c = ROOT.TCanvas()
    root_fname.cd() # Open root file for writing
    c.Print(f"{fname}[")
    for v in varList:
        f = ROOT.TF1(f"f_{p}_{v}", "gaus", var_low[p][v], var_high[p][v])
        h[p][v].Fit(f, "RQ")
        mean[p][v] = f.GetParameter(1)
        mean_err[p][v] = f.GetParError(1)
        sigma[p][v] = f.GetParameter(2)
        sigma_err[p][v] = f.GetParError(2)
        h[p][v].Write(f"hist_{p}_{v}")  # Save histogram to ROOT file
        h[p][v].Draw()  # Save histogram to PDF
        c.Print(fname)  #
    c.Print(f"{fname}]")
    root_fname.Close()  # Close the root file

# combined plots
#--------------------------------
# Create a TLatex object for the text at the top right corner
latex_right = ROOT.TLatex()
latex_right.SetTextFont(42)  # Set the font style
latex_right.SetTextSize(0.03)  # Set the text size
# Set the position of the text at the top right corner
text_right_x = 0.69  # X position of the text (right)
text_right_y = 0.86  # Y position of the text (top)
# Create a TLatex object for the text at the top left corner
latex_left = ROOT.TLatex()
latex_left.SetTextFont(42)
latex_left.SetTextSize(0.03)
# Set the position of the text at the top left corner
text_left_x = 0.15  # X position of the text (left)
text_left_y = 0.86  # Y position of the text (top)

### momentum
outfile = ROOT.TFile(f"{outputDir}/p_dist.root", "recreate")
c = ROOT.TCanvas("canvas", "Plot", canvas_width, canvas_height)
c.cd()
# Set the plot position within the canvas
c.SetLeftMargin(plot_margin_left)
c.SetBottomMargin(plot_margin_bottom)
# Set the plot size within the canvas
c.SetWindowSize(int(canvas_width * plot_width), int(canvas_height * plot_height))

p_dist = {}
p_dist_t = {}
fname = f"{outputDir}/p_dist.pdf"
c.Print(f"{fname}[")
legend = {}
for v in varList:
    legend[v] = ROOT.TLegend(0.6, 0.7, 0.8, 0.9)
    legend[v].SetBorderSize(0)  # Set border size to zero
    legend[v].SetFillStyle(0)  # Set fill style to transparent
    legend[v].SetTextFont(62)
    legend[v].SetX1(0.62)  # Legend X position (left)
    legend[v].SetY1(0.62)  # Legend Y position (bottom)
    legend[v].SetX2(0.82)  # Legend X position (right)
    legend[v].SetY2(0.82)  # Legend Y position (top)
    p_dist[v] = ROOT.TMultiGraph()
    p_dist_t[v] = {}
    marker_style_index = 0  # Index for marker_styles list
    color_index = 0  # Index for colors list

    for t in stackThetaList:
        y = ROOT.std.vector["double"]((sigma[pname("mu", t, p)][v]) for p in MomentumList)
        x = ROOT.std.vector["double"](float(p) for p in MomentumList)
        err_y = ROOT.std.vector["double"]((sigma_err[pname("mu", t, p)][v]) for p in MomentumList)
        err_x = ROOT.std.vector["double"]([0]*len(MomentumList))
        p_dist_t[v][t] = ROOT.TGraphErrors(len(MomentumList), x.data(), y.data(), err_x.data(), err_y.data())
        p_dist_t[v][t].SetMarkerStyle(marker_styles[marker_style_index])
        p_dist_t[v][t].SetMarkerColor(colors[color_index])
        p_dist_t[v][t].Scale(unit_scale[v])
        p_dist[v].Add(p_dist_t[v][t])
        legend[v].AddEntry(p_dist_t[v][t], f"#theta = {t} deg", "p")

        marker_style_index = (marker_style_index + 1) #% len(marker_styles)
        color_index = (color_index + 1) #% len(colors)

    p_dist[v].SetTitle(f";p [GeV];{title[v]}")
   # Set logarithmic scale for x and y axes
    c.SetLogx()
    c.SetLogy()
   # Adjust the pad margins to make space for the right and top axes
    c.SetRightMargin(0.15)
    c.SetTopMargin(0.15)
   # Get the current pad
    pad = c.GetPad(0)
   # Set the position of the right and top axes
    pad.SetTickx(1)  # Draw the x-axis ticks on the top
    pad.SetTicky(1)  # Draw the y-axis ticks on the right
   # Draw the axes and data points
    p_dist[v].Draw("APE") 
   # Increase the size of the axis title text
    p_dist[v].GetXaxis().SetTitleSize(0.06)
    p_dist[v].GetYaxis().SetTitleSize(0.06)
   # Add the text at the top left corner
    latex_left.DrawLatexNDC(text_left_x, text_left_y, "FCC-ee CLD")
   # Draw the legend
    legend[v].Draw()
   # Print canvas to the PDF file
    c.Print(fname)
   # Write the TMultiGraph to the root file
    c.Write(f"Canvas_{v}")

c.Print(f"{fname}]")
outfile.Close()

### theta
outfile = ROOT.TFile(f"{outputDir}/t_dist.root", "recreate")
c = ROOT.TCanvas("canvas", "Plot", canvas_width, canvas_height)
c.cd()
# Set the plot position within the canvas
c.SetLeftMargin(plot_margin_left)
c.SetBottomMargin(plot_margin_bottom)
# Set the plot size within the canvas
c.SetWindowSize(int(canvas_width * plot_width), int(canvas_height * plot_height))

t_dist = {}
t_dist_p = {}
fname = f"{outputDir}/t_dist.pdf"
c.Print(f"{fname}[")
legend = {}
for v in varList:
    legend[v] = ROOT.TLegend(0.6, 0.7, 0.8, 0.9)
    legend[v].SetBorderSize(0)  # Set border size to zero
    legend[v].SetFillStyle(0)  # Set fill style to transparent
    legend[v].SetTextFont(62)
    legend[v].SetX1(0.62)  # Legend X position (left)
    legend[v].SetY1(0.62)  # Legend Y position (bottom)
    legend[v].SetX2(0.82)  # Legend X position (right)
    legend[v].SetY2(0.82)  # Legend Y position (top)
    t_dist[v] = ROOT.TMultiGraph()
    t_dist_p[v] = {}
    marker_style_index = 0  # Index for marker_styles list
    color_index = 0  # Index for colors list
    for p in stackMomentumList:
        y = ROOT.std.vector["double"]((sigma[pname("mu", t, p)][v]) for t in ThetaList)
        x = ROOT.std.vector["double"](float(t) for t in ThetaList)
        err_y = ROOT.std.vector["double"]((sigma_err[pname("mu", t, p)][v]) for t in ThetaList)
        err_x = ROOT.std.vector["double"]([0]*len(ThetaList))
        t_dist_p[v][p] = ROOT.TGraphErrors(len(ThetaList), x.data(), y.data(), err_x.data(), err_y.data())
        t_dist_p[v][p].SetMarkerStyle(marker_styles[marker_style_index])
        t_dist_p[v][p].SetMarkerColor(colors[color_index])
        t_dist_p[v][p].Scale(unit_scale[v])
        t_dist[v].Add(t_dist_p[v][p])
        legend[v].AddEntry(t_dist_p[v][p], f"p = {p}GeV", "p")

        marker_style_index = (marker_style_index + 1) % len(marker_styles)
        color_index = (color_index + 1) % len(colors)

    t_dist[v].SetTitle(f";#theta [deg];{title[v]}")
    # Set logarithmic scale for y axis
    c.SetLogy()
   # Adjust the pad margins to make space for the right and top axes
    c.SetRightMargin(0.15)
    c.SetTopMargin(0.15)
   # Get the current pad
    pad = c.GetPad(0)
   # Set the position of the right and top axes
    pad.SetTickx(1)  # Draw the x-axis ticks on the top
    pad.SetTicky(1)  # Draw the y-axis ticks on the right
   # Draw the axes and data points
    t_dist[v].Draw("AP") 
   # Increase the size of the axis title text
    t_dist[v].GetXaxis().SetTitleSize(0.06)
    t_dist[v].GetYaxis().SetTitleSize(0.06)
   # Add the text at the top left corner
    latex_left.DrawLatexNDC(text_left_x, text_left_y, "FCC-ee CLD")
   # Draw the legend
    legend[v].Draw()
   # Print canvas to the PDF file
    c.Print(fname)
   # Write the TMultiGraph to the root file
    c.Write(f"Canvas_{v}")

c.Print(f"{fname}]")
outfile.Close()
#------------------------------------
