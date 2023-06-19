import ROOT
import os
import glob
import numpy as np
import scipy as scipy
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from statistics import mean # importing mean()
from scipy.stats import norm, crystalball, chisquare
from scipy.stats import linregress

# Get the current working directory
cwd = os.getcwd()

# Set Detector Model and numder of events
DetectorModel = 'FCCee_o2_v02'
Nevts = '1000'

# Define the directory where the plots will be saved
output_dir = f'plots_{DetectorModel}'
sub_dirs = ['DeltaPt_Pt2_Distributions', 'Hist_pT_Distributions', 'd0_Distribution']

# Create the directory if it does not exist
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Create a TGraphErrors object to hold the data points from divided histograms
graph = ROOT.TGraphErrors()

# loop over the three file types mu*.root, e*.root, pi*.root
for ftype in ['mu', 'e', 'pi']:
    for sub_dir in sub_dirs:
        sub_dir_path = os.path.join(output_dir, f"{sub_dir}_{ftype}")
        if not os.path.exists(sub_dir_path):
            os.mkdir(sub_dir_path)

    # List of ROOT files
    filelist = glob.glob(f'/eos/user/g/gasadows/Output/TrackingPerformance/{DetectorModel}/Analysis/'+f'{ftype}'+'*.root')

    sigma_DeltaPt_Pt2_list = []
    theta_list = []
    momentum_list = []
    transverse_momentum_list = []
    efficiency_list = []
    d0_std_list = []
    # Create empty lists to store the calculated points and errors
    eff_list = []
    errors_list = []

    for file_name in filelist:
        # Open ROOT file and get events tree
        file = ROOT.TFile.Open(file_name)
        tree = file.Get("events")

        # Create list sigma_DeltaPt_Pt2 containing the sigma value of the distribution DeltaPt_Pt2
        sigma_DeltaPt_Pt2 = []
        DeltaPt_Pt2 = []
        Delta_d0 = []
        MC_theta_list = []  # Create empty list for MC_theta values
        MC_p_list = []  # Create empty list for MC_p values
        MC_pt_list = []  # Create empty list for MC_pt mathed to reco values
        MC_pt_all_list = []  # Create empty list for all MC_pt values
        trk_pt_list = []  # Create empty list for Trk_pt values
        d0_list = []  # Create empty list for d0 values
        for i in range(tree.GetEntries()):
            tree.GetEntry(i)
            MC_tlv = tree.MC_tlv
            trk_pT = tree.Track_pt # Reconstructed track matched to the MC particle
            trk_d0 = tree.d0
            reco_PDG = tree.MC_Reco_pdg
            for j in range(len(MC_tlv)):
                MC_pt_all = MC_tlv[j].Pt()
                MC_pt_all_list.append(MC_pt_all)  # Append each MC_pt value to the list
                if (trk_pT != 0) or (trk_pT != -9) :  # Matched particles only
                    trk_pt = trk_pT[j]
                    trk_pt_list.append(trk_pt)  # Append each trk_pt value to the list
                    d0 = trk_d0[j]
                    d0_list.append(d0)  # Append each d0 value to the list
                    MC_theta = MC_tlv[j].Theta()
                    MC_theta_list.append(MC_theta)  # Append each MC_theta value to the list
                    MC_p = MC_tlv[j].P()
                    MC_p_list.append(MC_p)  # Append each MC_p value to the list
                    MC_pt = MC_tlv[j].Pt()
                    MC_pt_list.append(MC_pt)  # Append each MC_pt value to the list                 
            DeltaPt_Pt2.append( (trk_pt - MC_pt) / (MC_pt * MC_pt) )       

    #### Remove badly reconstructed tracks
       # Delta pT / pT^2
        threshold = 3         # Define threshold value for number of standard deviations from the mean
        DeltaPt_Pt2_sel = DeltaPt_Pt2  # Initialise with original data
        n_selections = 3        # Number of selection
        for i in range(n_selections):            
            mean_DeltaPt_Pt2_sel = np.mean(DeltaPt_Pt2_sel)
            std_DeltaPt_Pt2_sel = np.std(DeltaPt_Pt2_sel)
            DeltaPt_Pt2_sel_new = []
            for dpt in DeltaPt_Pt2_sel:
                if abs(dpt - mean_DeltaPt_Pt2_sel) < threshold * std_DeltaPt_Pt2_sel:
                    DeltaPt_Pt2_sel_new.append(dpt)
            DeltaPt_Pt2_sel = DeltaPt_Pt2_sel_new
       # Delta d0
        threshold = 2         # Define threshold value for number of standard deviations from the mean
        Delta_d0_sel = d0_list  # Initialise with original data
        n_selections = 4        # Number of selection
        for i in range(n_selections):
            mean_Delta_d0_sel = np.mean(Delta_d0_sel)
            std_Delta_d0_sel = np.std(Delta_d0_sel)
            Delta_d0__sel_new = []
            for dpt in Delta_d0_sel:
                if abs(dpt - mean_Delta_d0_sel) < threshold * std_Delta_d0_sel:
                    Delta_d0__sel_new.append(dpt)
            Delta_d0_sel = Delta_d0__sel_new
    #####

        ############################### Plot the distributions of DeltaPt_Pt2 and DeltaPt_Pt2_sel for each files
        fig, ax = plt.subplots()  # create a new figure and axis object
        file_name = os.path.basename(str(file_name))  # Extract the filename only from the full path
        #------
        # Plot the histogram distribution of DeltaPt_Pt2_sel
        n, bins, patches = plt.hist(DeltaPt_Pt2_sel, bins=(len(DeltaPt_Pt2_sel)//10), histtype='step', label='DeltaPt_Pt2_sel')
        if ftype != 'e':       
            # Fit a normal distribution to the data
            mu, std = norm.fit(DeltaPt_Pt2_sel)
            fit_line = scipy.stats.norm.pdf(bins[:-1], mu, std) * sum(n * np.diff(bins))
            # Calculate chi-square for normal distribution fit
            chi2, p_value = scipy.stats.chisquare(n / np.sum(n), f_exp=fit_line / np.sum(fit_line))
            # Plot the fitted line
            plt.plot(bins[:-1], fit_line,'r', linewidth=1.5, label=(r"$\sigma=%0.3e$, $\chi^2=%0.3f$" % (std, chi2)))
            sigma_DeltaPt_Pt2 = std
        else:
            # Fit a Crystal Ball distribution for electrons
            params = scipy.stats.crystalball.fit(DeltaPt_Pt2_sel)
            fit_line = scipy.stats.crystalball.pdf(bins[:-1], *params) * sum(n * np.diff(bins)) 
            sigma = params[-1]
            # Calculate chi-square for normal distribution fit
            fit_line2 = scipy.stats.crystalball.pdf(bins[:-1], *params) * sum(n * np.diff(bins)) / np.sum(fit_line)
            chi2, p_value = scipy.stats.chisquare(n / np.sum(n), f_exp=fit_line / np.sum(fit_line))
            # Plot the fitted line
            plt.plot(bins[:-1], fit_line, 'r', linewidth=1.5, label=(r"$\sigma=%0.3e$, $\chi^2=%0.3f$" % (sigma, chi2)))
            sigma_DeltaPt_Pt2 = sigma
        #------
        plt.xlabel(r'$\Delta p_T / p^2_{T,true}$', fontsize=12)
        plt.title(f'Distribution of $\Delta p_T / p^2_{{T,true}}$ for {file_name}')
        plt.legend() 
        sub_dir_path = os.path.join(output_dir, f"{sub_dirs[0]}_{ftype}")
        plt.savefig(os.path.join(sub_dir_path, f'{file_name}.png'))
        #figure_path = os.path.join(cwd, f'{file_name}.png')
        plt.close(fig)  # close the figure to free up memory
        ################################

        ############################### Plot the distribution of Delta d0 for each files
        fig, ax = plt.subplots()  # create a new figure and axis object
        file_name = os.path.basename(str(file_name))  # Extract the filename only from the full path
        #------
        # Plot the histogram distribution of Delta_d0_sel
        n, bins, patches = plt.hist(Delta_d0_sel, bins=(100), histtype='step', label='Delta_d0_sel')      
        # Fit a normal distribution to the data
        mu, std = norm.fit(Delta_d0_sel)
        fit_line = scipy.stats.norm.pdf(bins[:-1], mu, std) * sum(n * np.diff(bins))
        # Calculate chi-square for normal distribution fit
        chi2, p_value = scipy.stats.chisquare(n / np.sum(n), f_exp=fit_line / np.sum(fit_line))
        # Plot the fitted line
        plt.plot(bins[:-1], fit_line,'r', linewidth=1.5, label=(r"$\sigma=%0.3e$, $\chi^2=%0.3f$" % (std, chi2)))
        d0_std = std
        #------
        plt.xlabel(r'$\Delta d_0$', fontsize=12)
        plt.title(f'Distribution of $\Delta d_0$ for {file_name}')
        plt.legend() 
        sub_dir_path = os.path.join(output_dir, f"{sub_dirs[2]}_{ftype}")
        plt.savefig(os.path.join(sub_dir_path, f'{file_name}.png'))
        plt.close(fig)  # close the figure to free up memory
        ################################

    ##### Calculate Efficiency
       # Create the histograms
        min_pt = min(min(MC_pt_all_list), min(MC_pt_list))    # Calculate the common axis limits for both histograms
        max_pt = max(max(MC_pt_all_list), max(MC_pt_list))    # Calculate the common axis limits for both histograms
        Nbins = 10    # Calculate the  number of bins for both histograms
        MC_matched_pt_hist = ROOT.TH1F("MC_matched_pt_hist", "MC matched pT Distribution", Nbins, min_pt, max_pt) # Nbins, min, max)
        MC_pt_hist = ROOT.TH1F("MC_pt_hist", "MC pT Distribution", Nbins, min_pt, max_pt)   # Nbins, min, max)
       # Fill the histograms
        for MC_pt, dpt in zip( MC_pt_list, DeltaPt_Pt2):
            if dpt in DeltaPt_Pt2:
                MC_matched_pt_hist.Fill(MC_pt)
        for pt in MC_pt_all_list:
            MC_pt_hist.Fill(pt)
       # Divide the histograms
        divided_hist = ROOT.TH1F("divided_hist", "Divided Histogram", Nbins, min_pt, max_pt) # Nbins, min, max)
        divided_hist.Divide(MC_matched_pt_hist, MC_pt_hist, 1, 1, "b") # weight Hist1, weight Hist2, b = binomial error     
        #divided_hist.Print("all") # Print the bin contents and errors
       # Get the calculated point and error from the divided histogram
        for bin in range(1, divided_hist.GetNbinsX() + 1):
            bin_content = divided_hist.GetBinContent(bin)
            bin_error = divided_hist.GetBinError(bin)
            if bin_content != 0:
                eff_list.append(bin_content)
                errors_list.append(bin_error)
       # Plot the histograms
        ROOT.gROOT.SetBatch(True)   # Disable interactive mode
        file_name = os.path.basename(str(file_name))  # Extract the filename only from the full path
       # Create canvas
        canvas = ROOT.TCanvas("canvas", "Histograms", 800, 600)
        canvas.Divide(2, 1) # Divide the canvas into 2 pads
        canvas . cd (1) ##
       # Draw MC_matched_pt_hist
        MC_matched_pt_hist.SetTitle("pT Distribution")
        MC_matched_pt_hist.GetXaxis().SetTitle("pT (GeV)")
        MC_matched_pt_hist.Draw()
        MC_matched_pt_hist.SetLineColor(ROOT.kBlue)
        MC_matched_pt_hist.SetLineWidth(2)
       # Draw MC_pt_hist on the same canvas
        MC_pt_hist.Draw("same")
        MC_pt_hist.SetLineColor(ROOT.kRed)
        MC_pt_hist.SetLineWidth(2)
        MC_pt_hist.SetLineStyle(9)
       # Set legend
        legend = ROOT.TLegend(0.7, 0.7, 0.9, 0.9)  # Adjust the legend position as needed
        legend.SetTextSize(0.03)  # Adjust the text size
        legend.AddEntry(MC_matched_pt_hist, "MC matched pT Distribution", "l")
        legend.AddEntry(MC_pt_hist, "MC pT Distribution", "l")
        legend.Draw()
        canvas . cd (2) ##
       # Draw the divided_hist
        divided_hist.GetXaxis().SetTitle("pT (GeV)")
        divided_hist.Draw()
       # Set properties
        divided_hist.SetLineColor(ROOT.kGreen)
        divided_hist.SetLineWidth(2)
       # Set title and axis labels
        divided_hist.SetTitle("Divided Histogram")
       # Save canvas as image file
        sub_dir_path = os.path.join(output_dir, f"{sub_dirs[1]}_{ftype}")
        canvas.SaveAs(os.path.join(sub_dir_path, f'{file_name}_pT.png'))
        ROOT.gROOT.SetBatch(False)  # Enable ineractive mode again
       # Clean up resources
        canvas.Close()
    ##### 

        # Calculate mean values of theta and momentum
        theta = int(np.mean(np.round(np.rad2deg(MC_theta_list))))  # Calculate mean of MC_theta_list
        momentum = int(np.mean(np.round(MC_p_list)))  # Calculate mean of MC_p_list
        transverse_momentum = int(np.mean(np.round(MC_pt_list)))  # Calculate mean of MC_pt_list

        d0_std = np.std(Delta_d0_sel)
        # Append the values to the lists
        sigma_DeltaPt_Pt2_list.append(sigma_DeltaPt_Pt2)
        theta_list.append(theta)
        momentum_list.append(momentum)
        transverse_momentum_list.append(transverse_momentum)
        d0_std_list.append(d0_std)

        # Close the ROOT file
        file.Close()

   # Rename the lists
    theta = theta_list
    momentum = momentum_list
    transverse_momentum = transverse_momentum_list
    sigma_DeltaPt_Pt2 = sigma_DeltaPt_Pt2_list
    d0 = d0_std_list

   # Create a dict by theta
    data_dict = {}
    variable_names = ['momentum', 'transverse_momentum', 'sigma_DeltaPt_Pt2', 'd0', 'eff_list', 'errors_list']
    for i in range(len(theta)):
        if theta[i] not in data_dict:
            data_dict[theta[i]] = {}
        for var_name, var_value in zip(variable_names, [momentum, transverse_momentum, sigma_DeltaPt_Pt2, d0, eff_list, errors_list]):
            if var_name not in data_dict[theta[i]]:
                data_dict[theta[i]][var_name] = []
            data_dict[theta[i]][var_name].append(var_value[i])

   # Create a dict by momentum
    data_dict_p = {}
    variable_names = ['theta', 'transverse_momentum', 'sigma_DeltaPt_Pt2', 'd0', 'eff_list', 'errors_list']
    for i in range(len(momentum)):
        if momentum[i] not in data_dict_p:
            data_dict_p[momentum[i]] = {}
        for var_name, var_value in zip(variable_names, [theta, transverse_momentum, sigma_DeltaPt_Pt2, d0, eff_list, errors_list]):
            if var_name not in data_dict_p[momentum[i]]:
                data_dict_p[momentum[i]][var_name] = []
            data_dict_p[momentum[i]][var_name].append(var_value[i])

    ############################### Momentum resolution PLOT ###############################
    ## Delta_pT/pT^2 vs p
    #----------------------------------
    fig, ax = plt.subplots() 
    ax.set_xscale('log')
    ax.set_yscale('log')
    # Add graduations on top and right sides of the plot
    ax.xaxis.set_ticks_position('both')
    ax.yaxis.set_ticks_position('both')
    ax.tick_params(axis='x', which='both', direction='in')
    ax.tick_params(axis='y', which='both', direction='in')
    ax.set_xlabel(r'$p$ [GeV] ', fontsize=12)
    ax.set_ylabel(r'$\sigma(\Delta p_T / p^2_{T,true})$ $[GeV^{-1}] $', fontsize=12)
    markers = ['o', 's', 'd', 'X', '^']
    handles = []
    labels = []

    for idx, (t, data_list) in enumerate(sorted(data_dict.items())):
        if t in [10, 30, 50, 70, 89]:
            ## plot the points by theta
            momentum = data_dict[t]['momentum']
            sigma_DeltaPt_Pt2 = data_dict[t]['sigma_DeltaPt_Pt2']
            scatter = ax.scatter(momentum, sigma_DeltaPt_Pt2, s=30, linewidth=0, marker=markers[idx % len(markers)])
            handles.append(scatter)
            labels.append(r'$\theta$ = '+str(t)+' deg')

            ## fit by theta
            # Fit the data using linear regression
            a, b, r_value, p_value, std_err = linregress(np.log(momentum), np.log(sigma_DeltaPt_Pt2))
            # Plot the fitted line on top of the data
            xfit = np.linspace(min(momentum), max(momentum), 100)
            yfit = np.exp(b) * xfit**a
            plt.loglog(xfit, yfit,'--', linewidth=0.5)

    legend_line = mlines.Line2D([], [], color='black', linestyle='--', linewidth=0.5)
    handles.append(legend_line)
    labels.append(r'a + b / (p $\sin^{3/2}\theta)$')

    # Customise title depending on ftype 
    if ftype == 'mu' or ftype == 'pi':
        title = r'Single $\mu^-$' if ftype == 'mu' else r'Single $\pi^-$'
    else:
        title = r'Single $e^-$'
    leg = plt.legend(handles,labels, loc='upper right', labelspacing=-0.2, title=title, title_fontsize='larger')
    leg._legend_box.align = "left" # Make title align on the left

    # add text in the upper left corner
    text_str = "FCC−ee CLD"
    plt.text(-0.00005, 1.04, text_str, transform=ax.transAxes, fontsize=12, va='top', ha='left')
    # add text in the upper right corner
    text_str = f"~{Nevts} events/point"
    plt.text(1.0, 1.04, text_str, transform=ax.transAxes, fontsize=10, va='top', ha='right')

    ## Save the plot to a file
    plt.savefig(os.path.join(output_dir,'momentum_resolution_'+f'{ftype}'+'.png'))
    #----------------------------------

    ## Delta_pT/pT^2 vs theta
    #----------------------------------
    fig, ax = plt.subplots() 
    ax.set_yscale('log')
    # Add graduations on top and right sides of the plot
    ax.xaxis.set_ticks_position('both')
    ax.yaxis.set_ticks_position('both')
    ax.tick_params(axis='x', which='both', direction='in')
    ax.tick_params(axis='y', which='both', direction='in')
    ax.set_xlabel(r'$\theta$ [deg] ', fontsize=12)
    ax.set_ylabel(r'$\sigma(\Delta p_T / p^2_{T,true})$ $[GeV^{-1}] $', fontsize=12)
    markers = ['o', 's', 's', '^']
    handles = []
    labels = []

    for idx, (p, data_list_p) in enumerate(sorted(data_dict_p.items())):
        if p in [1, 10, 100]:
            ## plot the points by momentum
            theta = data_dict_p[p]['theta']
            sigma_DeltaPt_Pt2 = data_dict_p[p]['sigma_DeltaPt_Pt2']
            scatter = ax.scatter(theta, sigma_DeltaPt_Pt2, s=30, linewidth=0, marker=markers[idx % len(markers)])
            handles.append(scatter)
            labels.append(r'$p$ = '+str(p)+' GeV')

    # Customise title depending on ftype 
    if ftype == 'mu' or ftype == 'pi':
        title = r'Single $\mu^-$' if ftype == 'mu' else r'Single $\pi^-$'
    else:
        title = r'Single $e^-$'
    leg = plt.legend(handles,labels, loc='upper right', labelspacing=-0.2, title=title, title_fontsize='larger')
    leg._legend_box.align = "left" # Make title align on the left

    # add text in the upper left corner
    text_str = "FCC−ee CLD"
    plt.text(-0.00005, 1.04, text_str, transform=ax.transAxes, fontsize=12, va='top', ha='left')
    # add text in the upper right corner
    text_str = f"~{Nevts} events/point"
    plt.text(1.0, 1.04, text_str, transform=ax.transAxes, fontsize=10, va='top', ha='right')

    ## Save the plot to a file
    plt.savefig(os.path.join(output_dir,'momentum_resolution_theta_'+f'{ftype}'+'.png'))
    #----------------------------------

    ############################### Impact parameter resolution PLOT ###############################
    ## sgima(d0) vs p
    #----------------------------------
    fig, ax = plt.subplots() 
    ax.set_xscale('log')
    ax.set_yscale('log')
    # Add graduations on top and right sides of the plot
    ax.xaxis.set_ticks_position('both')
    ax.yaxis.set_ticks_position('both')
    ax.tick_params(axis='x', which='both', direction='in')
    ax.tick_params(axis='y', which='both', direction='in')
    ax.set_xlabel(r'$p$ [GeV] ', fontsize=12)
    ax.set_ylabel(r'$\sigma(\Delta d_0$) $[\mu m] $', fontsize=12)
    markers = ['o', 's', 'd', 'X', '^']
    handles = []
    labels = []

    for idx, (t, data_list) in enumerate(sorted(data_dict.items())):
        if t in [10, 30, 50, 70, 89]:
            ## plot the points by theta
            momentum = data_dict[t]['momentum']
            d0 = data_dict[t]['d0']
            d0_mu = [val * 1000 for val in d0]  # Convert d0 from mm to μm
            scatter = ax.scatter(momentum, d0_mu, s=30, linewidth=0, marker=markers[idx % len(markers)])
            handles.append(scatter)
            labels.append(r'$\theta$ = '+str(t)+' deg')

    # Customise title depending on ftype 
    if ftype == 'mu' or ftype == 'pi':
        title = r'Single $\mu^-$' if ftype == 'mu' else r'Single $\pi^-$'
    else:
        title = r'Single $e^-$'
    leg = plt.legend(handles,labels, loc='upper right', labelspacing=-0.2, title=title, title_fontsize='larger')
    leg._legend_box.align = "left" # Make title align on the left

    # add text in the upper left corner
    text_str = "FCC−ee CLD"
    plt.text(-0.00005, 1.04, text_str, transform=ax.transAxes, fontsize=12, va='top', ha='left')
    # add text in the upper right corner
    text_str = f"~{Nevts} events/point"
    plt.text(1.0, 1.04, text_str, transform=ax.transAxes, fontsize=10, va='top', ha='right')

    ## Save the plot to a file
    plt.savefig(os.path.join(output_dir,'Impact_parameter_resolution_'+f'{ftype}'+'.png'))
    #----------------------------------
    ## sgima(d0) vs theta
    #----------------------------------
    fig, ax = plt.subplots()
    ax.set_yscale('log')
    # Add graduations on top and right sides of the plot
    ax.xaxis.set_ticks_position('both')
    ax.yaxis.set_ticks_position('both')
    ax.tick_params(axis='x', which='both', direction='in')
    ax.tick_params(axis='y', which='both', direction='in')
    ax.set_xlabel(r'$\theta$ [deg] ', fontsize=12)
    ax.set_ylabel(r'$\sigma(\Delta d_0$) $[\mu m] $', fontsize=12)
    markers = ['o', 's', 's', '^']
    handles = []
    labels = []

    for idx, (p, data_list_p) in enumerate(sorted(data_dict_p.items())):
        if p in [1, 10, 100]:
            ## plot the points by momentum
            theta = data_dict_p[p]['theta']
            d0 = data_dict_p[p]['d0']
            d0_mu = [val * 1000 for val in d0]  # Convert d0 from mm to μm
            scatter = ax.scatter(theta, d0_mu, s=30, linewidth=0, marker=markers[idx % len(markers)])
            handles.append(scatter)
            labels.append(r'$p$ = '+str(p)+' GeV')

    # Customise title depending on ftype 
    if ftype == 'mu' or ftype == 'pi':
        title = r'Single $\mu^-$' if ftype == 'mu' else r'Single $\pi^-$'
    else:
        title = r'Single $e^-$'
    leg = plt.legend(handles,labels, loc='upper right', labelspacing=-0.2, title=title, title_fontsize='larger')
    leg._legend_box.align = "left" # Make title align on the left

    # add text in the upper left corner
    text_str = "FCC−ee CLD"
    plt.text(-0.00005, 1.04, text_str, transform=ax.transAxes, fontsize=12, va='top', ha='left')
    # add text in the upper right corner
    text_str = f"~{Nevts} events/point"
    plt.text(1.0, 1.04, text_str, transform=ax.transAxes, fontsize=10, va='top', ha='right')

    ## Save the plot to a file
    plt.savefig(os.path.join(output_dir,'Impact_parameter_resolution_theta_'+f'{ftype}'+'.png'))
    #----------------------------------

    ############################### Efficiency PLOT ###############################
    ## Single particle reconstruction efficiency vs pt
    #----------------------------------
    fig, ax = plt.subplots() 
    ax.set_xscale('log')
    # Add graduations on top and right sides of the plot
    ax.xaxis.set_ticks_position('both')
    ax.yaxis.set_ticks_position('both')
    ax.tick_params(axis='x', which='both', direction='in')
    ax.tick_params(axis='y', which='both', direction='in')
    #ax.set_title(r'single $\mu^-$', fontsize=14)
    ax.set_xlabel(r'$p_T$ [GeV] ', fontsize=12)
    ax.set_ylabel(r'Reconstruction efficiency', fontsize=12)
    markers = ['o', 's', 'd', 'X', '^']
    handles = []
    labels = []

    for idx, (t, data_list) in enumerate(sorted(data_dict.items())):
        ## plot the points by theta
        pt = data_dict[t]['transverse_momentum']
        eff_points = data_dict[t]['eff_list']
        errors = data_dict[t]['errors_list']
        scatter = plt.errorbar(pt, eff_points, yerr=errors, fmt=markers[idx % len(markers)], capsize=3)
        handles.append(scatter)
        labels.append(r'$\theta$ = '+str(t)+' deg')

    # Customise title depending on ftype 
    if ftype == 'mu' or ftype == 'pi':
        title = r'Single $\mu^-$' if ftype == 'mu' else r'Single $\pi^-$'
    else:
        title = r'Single $e^-$'
    leg = plt.legend(handles,labels, loc='lower right', labelspacing=-0.1, title=title, title_fontsize='larger')
    leg._legend_box.align = "left" # Make title align on the left

    # add text in the upper left corner
    text_str = "FCC−ee CLD"
    plt.text(-0.00005, 1.04, text_str, transform=ax.transAxes, fontsize=12, va='top', ha='left')
    # add text in the upper right corner
    text_str = f"~{Nevts} events/point"
    plt.text(1.0, 1.04, text_str, transform=ax.transAxes, fontsize=10, va='top', ha='right')

    ## Save the plot to a file
    plt.savefig(os.path.join(output_dir,'reco_efficiency_'+f'{ftype}'+'.png'))
    #----------------------------------

    ## show plots
    #plt.show() 
