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
import argparse

# Get the current working directory
cwd = os.getcwd()

# Set Detector Model and numder of events
#Nevts = "1000"
#DetectorModel = "FCCee_o1_v04"

# Define the command-line argument parser
parser = argparse.ArgumentParser(description="Script for plotting Detector Performances")
parser.add_argument("-DetectorModel", help="Detector model: FCCee_o1_v04 or FCCee_o2_v02", required=True)
parser.add_argument("-Nevts", help="Number of events", required=True)
args = parser.parse_args()

# Define the directory where the plots will be saved
output_dir = f'plots_{args.DetectorModel}'
sub_dirs = ['DeltaPt_Pt2_Distributions', 'Hist_pT_Distributions', 'd0_Distributions', 'z0_Distributions']

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
    filelist = glob.glob(f'/eos/user/g/gasadows/Output/TrackingPerformance/{args.DetectorModel}/Analysis/'+f'{ftype}'+'*.root')

    sigma_DeltaPt_Pt2_list = []
    theta_list = []
    momentum_list = []
    transverse_momentum_list = []
    efficiency_list = []
    d0_std_list = []
    z0_std_list = []
    std_values_DeltaPt_Pt2 = []
    std_values_Delta_d0 = []
    std_values_Delta_z0 = []
   # List for calculated point and error from the divided histogram
    eff_list = []
    errors_list = []

    for file_name in filelist:
        # Open ROOT file and get events tree
        file = ROOT.TFile.Open(file_name)
        tree = file.Get("events")

        # Create list sigma_DeltaPt_Pt2 containing the sigma value of the distribution DeltaPt_Pt2
        sigma_DeltaPt_Pt2 = []
        DeltaPt_Pt2 = []
        MC_theta_list = []  # Create empty list for MC_theta values
        MC_p_list = []  # Create empty list for MC_p values
        MC_pt_list = []  # Create empty list for MC_pt mathed to reco values
        MC_pt_all_list = []  # Create empty list for all MC_pt values
        trk_pt_list = []  # Create empty list for Trk_pt values
        d0_list = []  # Create empty list for d0 values
        z0_list = []  # Create empty list for z0 values
        for i in range(tree.GetEntries()):
            tree.GetEntry(i)
            MC_tlv = tree.MC_tlv   # MC particles
            trk_pT = tree.Track_pt # Reconstructed track matched to the MC particle
            trk_d0 = tree.d0
            trk_z0 = tree.z0
            reco_PDG = tree.MC_Reco_pdg
            for j in range(len(MC_tlv)):
                MC_pt_all = MC_tlv[j].Pt()
                MC_pt_all_list.append(MC_pt_all)  # Append each MC_pt value to the list
                if (trk_pT != 0) or (trk_pT != -9) :  # Matched particles only
                    trk_pt = trk_pT[j]
                    trk_pt_list.append(trk_pt)  # Append each trk_pt value to the list
                    d0 = trk_d0[j]
                    d0_list.append(d0)  # Append each d0 value to the list
                    z0 = trk_z0[j]
                    z0_list.append(z0)  # Append each z0 value to the list
                    MC_theta = MC_tlv[j].Theta()
                    MC_theta_list.append(MC_theta)  # Append each MC_theta value to the list
                    MC_p = MC_tlv[j].P()
                    MC_p_list.append(MC_p)  # Append each MC_p value to the list
                    MC_pt = MC_tlv[j].Pt()
                    MC_pt_list.append(MC_pt)  # Append each MC_pt value to the list                 
            DeltaPt_Pt2.append( (trk_pt - MC_pt) / (MC_pt * MC_pt) )       

        #### Remove badly reconstructed tracks
        def filter_data(data, threshold, n_selections):
                filtered_data = data
                for _ in range(n_selections):
                    mean = np.mean(filtered_data)
                    std = np.std(filtered_data)
                    filtered_data = [d for d in filtered_data if abs(d - mean) < threshold * std]
                return filtered_data
        #####

        ############################### Plot the distributions of DeltaPt_Pt2 and DeltaPt_Pt2_sel for each file
        def plot_distribution_DeltaPt_Pt2(data, bins, xlabel, title, output_path, ftype, file_name):
            fig, ax = plt.subplots()
           # Plot the histogram distribution
            n, bins, patches = plt.hist(data, bins=bins, histtype='step', label='Data')
            if ftype != 'e':
               # Fit a normal distribution to the data
                mu, std = norm.fit(data)
                fit_line = scipy.stats.norm.pdf(bins[:-1], mu, std) * sum(n * np.diff(bins))
               # Calculate chi-square for normal distribution fit
                chi2, p_value = scipy.stats.chisquare(n / np.sum(n), f_exp=fit_line / np.sum(fit_line))
               # Plot the fitted line
                plt.plot(bins[:-1], fit_line, 'r', linewidth=1.5, label=(r"$\sigma=%0.3e$, $\chi^2=%0.3f$" % (std, chi2)))
                data_std = std
            else:
               # Fit a Crystal Ball distribution for electrons
                params = scipy.stats.crystalball.fit(data)
                fit_line = scipy.stats.crystalball.pdf(bins[:-1], *params) * sum(n * np.diff(bins))
                sigma = params[-1]
               # Calculate chi-square for normal distribution fit
                fit_line2 = scipy.stats.crystalball.pdf(bins[:-1], *params) * sum(n * np.diff(bins)) / np.sum(fit_line)
                chi2, p_value = scipy.stats.chisquare(n / np.sum(n), f_exp=fit_line / np.sum(fit_line))
               # Plot the fitted line
                plt.plot(bins[:-1], fit_line, 'r', linewidth=1.5, label=(r"$\sigma=%0.3e$, $\chi^2=%0.3f$" % (sigma, chi2)))
                data_std = sigma

            plt.xlabel(xlabel, fontsize=12)
            plt.title(title)
            plt.legend()
            plt.savefig(os.path.join(output_path, f'{file_name}.png'))
            plt.close(fig)

            return data_std

        ############################### Plot the distribution of Delta d0/z0 for each file
        def plot_distribution_Delta_d0_z0(data, bins, xlabel, title, output_path, file_name):
            fig, ax = plt.subplots()
           # Plot the histogram distribution
            n, bins, patches = plt.hist(data, bins=bins, histtype='step', label='Data')
           # Fit a normal distribution to the data
            mu, std = norm.fit(data)
            fit_line = scipy.stats.norm.pdf(bins[:-1], mu, std) * sum(n * np.diff(bins))
           # Calculate chi-square for normal distribution fit
            chi2, p_value = scipy.stats.chisquare(n / np.sum(n), f_exp=fit_line / np.sum(fit_line))
           # Plot the fitted line
            plt.plot(bins[:-1], fit_line, 'r', linewidth=1.5, label=(r"$\sigma=%0.3e$, $\chi^2=%0.3f$" % (std, chi2)))
            data_std = std

            plt.xlabel(xlabel, fontsize=12)
            plt.title(title)
            plt.legend()
            plt.savefig(os.path.join(output_path, f'{file_name}.png'))
            plt.close(fig)

            return data_std

      ######################### Calculate Efficiency
        def calculate_efficiency(data_list, mc_list, delta_list, output_path, file_name):
           # Create histograms
            min_pt = min(min(data_list), min(mc_list))
            max_pt = max(max(data_list), max(mc_list))
            Nbins = 10
            data_hist = ROOT.TH1F("data_hist", "Data Distribution", Nbins, min_pt, max_pt)
            mc_matched_hist = ROOT.TH1F("mc_matched_hist", "MC Matched Distribution", Nbins, min_pt, max_pt)
           # Fill the histograms
            for data_pt, delta_pt in zip(data_list, delta_list):
                if delta_pt in delta_list:
                    mc_matched_hist.Fill(data_pt)
            for pt in mc_list:
                data_hist.Fill(pt)
           # Divide the histograms
            divided_hist = ROOT.TH1F("divided_hist", "Divided Histogram", Nbins, min_pt, max_pt)
            divided_hist.Divide(mc_matched_hist, data_hist, 1, 1, "b")
            for bin in range(1, divided_hist.GetNbinsX() + 1):
                bin_content = divided_hist.GetBinContent(bin)
                bin_error = divided_hist.GetBinError(bin)
                if bin_content != 0:
                    eff_list.append(bin_content)
                    errors_list.append(bin_error)
           # Plot the histograms
            ROOT.gROOT.SetBatch(True)
            file_name = os.path.basename(str(file_name))
            canvas = ROOT.TCanvas("canvas", "Histograms", 800, 600)
            canvas.Divide(2, 1)

            canvas.cd(1)
            data_hist.SetTitle("Data Distribution")
            data_hist.GetXaxis().SetTitle("pT (GeV)")
            data_hist.Draw()
            data_hist.SetLineColor(ROOT.kBlue)
            data_hist.SetLineWidth(2)

            mc_matched_hist.Draw("same")
            mc_matched_hist.SetLineColor(ROOT.kRed)
            mc_matched_hist.SetLineWidth(2)
            mc_matched_hist.SetLineStyle(9)

            legend = ROOT.TLegend(0.7, 0.7, 0.9, 0.9)
            legend.SetTextSize(0.03)
            legend.AddEntry(mc_matched_hist, "MC Matched Distribution", "l")
            legend.AddEntry(data_hist, "Data Distribution", "l")
            legend.Draw()

            canvas.cd(2)
            divided_hist.GetXaxis().SetTitle("pT (GeV)")
            divided_hist.Draw()
            divided_hist.SetLineColor(ROOT.kGreen)
            divided_hist.SetLineWidth(2)
            divided_hist.SetTitle("Divided Histogram")

            canvas.SaveAs(os.path.join(output_path, f'{file_name}.png'))
            ROOT.gROOT.SetBatch(False)
            canvas.Close()

            return eff_list, errors_list
      ######################### 

       # Calculate mean values of theta and momentum
        theta = int(np.mean(np.round(np.rad2deg(MC_theta_list))))  # Calculate mean of MC_theta_list
        momentum = int(np.mean(np.round(MC_p_list)))  # Calculate mean of MC_p_list
        transverse_momentum = int(np.mean(np.round(MC_pt_list)))  # Calculate mean of MC_pt_list

#====================================================================
    #-------------------- Data selection
       # DeltaPt_Pt2
        DeltaPt_Pt2_sel = filter_data(DeltaPt_Pt2, 3, 3)    # data, threshold, n_selections
       # Delta_d0
        Delta_d0_sel = filter_data(d0_list, 2, 3)    # data, threshold, n_selections
       # Delta_z0
        Delta_z0_sel = filter_data(z0_list, 3, 3)    # data, threshold, n_selections
    #-------------------- Fit and plotting distribution for each files
        file_name = os.path.basename(str(file_name))  # Extract the filename only from the full path
       # Plot the distributions for DeltaPt_Pt2
        std_DeltaPt_Pt2 = plot_distribution_DeltaPt_Pt2(DeltaPt_Pt2_sel, len(DeltaPt_Pt2_sel) // 10, r'$\Delta p_T / p^2_{T,true}$', f'Distribution of $\Delta p_T / p^2_{{T,true}}$ for {file_name}', os.path.join(output_dir, f"{sub_dirs[0]}_{ftype}"), ftype, file_name)
        std_values_DeltaPt_Pt2.append(std_DeltaPt_Pt2)
       # Plot the distributions for Delta_d0
        std_Delta_d0 = plot_distribution_Delta_d0_z0(Delta_d0_sel, 100, r'$\Delta d_0$', f'Distribution of $\Delta d_0$ for {file_name}', os.path.join(output_dir, f"{sub_dirs[2]}_{ftype}"), file_name)
        std_values_Delta_d0.append(std_Delta_d0)
      # Plot the distributions for Delta_z0
        std_Delta_z0 = plot_distribution_Delta_d0_z0(Delta_z0_sel, 100, r'$\Delta z_0$', f'Distribution of $\Delta z_0$ for {file_name}', os.path.join(output_dir, f"{sub_dirs[3]}_{ftype}"), file_name)
        std_values_Delta_z0.append(std_Delta_z0)
    #-------------------- Efficiency histograms
        efficiency_list, errors_list = calculate_efficiency(MC_pt_all_list, MC_pt_list, DeltaPt_Pt2,  os.path.join(output_dir, f"{sub_dirs[1]}_{ftype}"), file_name)
#====================================================================

       # Calculate std for d0 and z0
        d0_std = np.std(Delta_d0_sel)
        z0_std = np.std(Delta_z0_sel)

       # Append the values to the lists
        sigma_DeltaPt_Pt2_list.append(sigma_DeltaPt_Pt2)
        theta_list.append(theta)
        momentum_list.append(momentum)
        transverse_momentum_list.append(transverse_momentum)
        d0_std_list.append(d0_std)
        z0_std_list.append(z0_std)

       # Close the ROOT file
        file.Close()

   # Rename the lists
    theta = theta_list
    momentum = momentum_list
    transverse_momentum = transverse_momentum_list
    sigma_DeltaPt_Pt2 = std_values_DeltaPt_Pt2
    d0 = std_values_Delta_d0
    z0 = std_values_Delta_z0

   # Create a dict by theta
    data_dict = {}
    variable_names = ['momentum', 'transverse_momentum', 'sigma_DeltaPt_Pt2', 'd0', 'z0', 'eff_list', 'errors_list']
    for i in range(len(theta)):
        if theta[i] not in data_dict:
            data_dict[theta[i]] = {}
        for var_name, var_value in zip(variable_names, [momentum, transverse_momentum, sigma_DeltaPt_Pt2, d0, z0, eff_list, errors_list]):
            if var_name not in data_dict[theta[i]]:
                data_dict[theta[i]][var_name] = []
            data_dict[theta[i]][var_name].append(var_value[i])

   # Create a dict by momentum
    data_dict_p = {}
    variable_names = ['theta', 'transverse_momentum', 'sigma_DeltaPt_Pt2', 'd0', 'z0', 'eff_list', 'errors_list']
    for i in range(len(momentum)):
        if momentum[i] not in data_dict_p:
            data_dict_p[momentum[i]] = {}
        for var_name, var_value in zip(variable_names, [theta, transverse_momentum, sigma_DeltaPt_Pt2, d0, z0, eff_list, errors_list]):
            if var_name not in data_dict_p[momentum[i]]:
                data_dict_p[momentum[i]][var_name] = []
            data_dict_p[momentum[i]][var_name].append(var_value[i])

    ############################### Momentum resolution PLOT ###############################
    def momentum_resolution_plots(data_dict, data_dict_p, ftype, Nevts, output_dir):
       ## Delta_pT/pT^2 vs p
       #----------------------------------
        def momentum_resolution_plot():
            fig, ax = plt.subplots()
            ax.set_xscale('log')
            ax.set_yscale('log')
            ax.xaxis.set_ticks_position('both')
            ax.yaxis.set_ticks_position('both')
            ax.tick_params(axis='x', which='both', direction='in') # Add graduations on top and right sides of the plot
            ax.tick_params(axis='y', which='both', direction='in') # Add graduations on top and right sides of the plot
            ax.set_xlabel(r'$p$ [GeV]', fontsize=12)
            ax.set_ylabel(r'$\sigma(\Delta p_T / p^2_{T,true})$ $[GeV^{-1}] $', fontsize=12)
            markers = ['o', 's', 'd', 'X', '^']
            handles = []
            labels = []

            for idx, (t, data_list) in enumerate(sorted(data_dict.items())):
                if t in [10, 30, 50, 70, 89]:
                   # plot the points by theta
                    momentum = data_dict[t]['momentum']
                    sigma_DeltaPt_Pt2 = data_dict[t]['sigma_DeltaPt_Pt2']
                    scatter = ax.scatter(momentum, sigma_DeltaPt_Pt2, s=30, linewidth=0, marker=markers[idx % len(markers)])
                    handles.append(scatter)
                    labels.append(r'$\theta$ = '+str(t)+' deg')

                    a, b, r_value, p_value, std_err = linregress(np.log(momentum), np.log(sigma_DeltaPt_Pt2))
                    xfit = np.linspace(min(momentum), max(momentum), 100)
                    yfit = np.exp(b) * xfit**a
                    plt.loglog(xfit, yfit,'--', linewidth=0.5)

            legend_line = mlines.Line2D([], [], color='black', linestyle='--', linewidth=0.5)
            handles.append(legend_line)
            labels.append(r'a + b / (p $\sin^{3/2}\theta)$')

           # Title depending on ftype
            if ftype == 'mu' or ftype == 'pi':
                title = r'Single $\mu^-$' if ftype == 'mu' else r'Single $\pi^-$'
            else:
                title = r'Single $e^-$'
            leg = plt.legend(handles, labels, loc='upper right', labelspacing=-0.2, title=title, title_fontsize='larger')
            leg._legend_box.align = "left"  # Make title align on the left

           # add text in the upper left corner
            text_str = "FCC−ee CLD"
            plt.text(-0.00005, 1.04, text_str, transform=ax.transAxes, fontsize=12, va='top', ha='left')
           # add text in the upper right corner
            text_str = f"~{args.Nevts} events/point"
            plt.text(1.0, 1.04, text_str, transform=ax.transAxes, fontsize=10, va='top', ha='right')

           # Save the plot to a file
            plt.savefig(os.path.join(output_dir, 'momentum_resolution_' + f'{ftype}' + '.png'))
            plt.close(fig)  # close the figure to free up memory

       ## Delta_pT/pT^2 vs theta
       #----------------------------------
        def momentum_resolution_theta_plot():
            fig, ax = plt.subplots()
            ax.set_yscale('log')
            ax.xaxis.set_ticks_position('both') # Add graduations on top and right sides of the plot
            ax.yaxis.set_ticks_position('both') # Add graduations on top and right sides of the plot
            ax.tick_params(axis='x', which='both', direction='in')
            ax.tick_params(axis='y', which='both', direction='in')
            ax.set_xlabel(r'$\theta$ [deg]', fontsize=12)
            ax.set_ylabel(r'$\sigma(\Delta p_T / p^2_{T,true})$ $[GeV^{-1}] $', fontsize=12)
            markers = ['o', 's', 's', '^']
            handles = []
            labels = []

            for idx, (p, data_list_p) in enumerate(sorted(data_dict_p.items())):
                if p in [1, 10, 100]:
                   # plot the points by momentum
                    theta = data_dict_p[p]['theta']
                    sigma_DeltaPt_Pt2 = data_dict_p[p]['sigma_DeltaPt_Pt2']
                    scatter = ax.scatter(theta, sigma_DeltaPt_Pt2, s=30, linewidth=0, marker=markers[idx % len(markers)])
                    handles.append(scatter)
                    labels.append(r'$p$ = '+str(p)+' GeV')

            if ftype == 'mu' or ftype == 'pi':
                title = r'Single $\mu^-$' if ftype == 'mu' else r'Single $\pi^-$'
            else:
                title = r'Single $e^-$'
            leg = plt.legend(handles, labels, loc='upper right', labelspacing=-0.2, title=title, title_fontsize='larger')
            leg._legend_box.align = "left"  # Make title align on the left

           # add text in the upper left corner
            text_str = "FCC−ee CLD"
            plt.text(-0.00005, 1.04, text_str, transform=ax.transAxes, fontsize=12, va='top', ha='left')
           # add text in the upper right corner
            text_str = f"~{args.Nevts} events/point"
            plt.text(1.0, 1.04, text_str, transform=ax.transAxes, fontsize=10, va='top', ha='right')

           # Save the plot to a file
            plt.savefig(os.path.join(output_dir, 'momentum_resolution_theta_' + f'{ftype}' + '.png'))
            plt.close(fig)  # close the figure to free up memory

        momentum_resolution_plot()
        momentum_resolution_theta_plot()
    #----------------------------------

    ############################### Impact parameter resolution PLOT ###############################
    def Impact_parameter_esolution_plots(data_dict, data_dict_p, ftype, Nevts, output_dir, variable):
       ## sgima(Delta d0) vs p
       #----------------------------------
        def Impact_parameter_resolution_plot():
            fig, ax = plt.subplots()
            #ax.set_xscale('log')
            ax.set_yscale('log')
            ax.xaxis.set_ticks_position('both') # Add graduations on top and right sides of the plot
            ax.yaxis.set_ticks_position('both') # Add graduations on top and right sides of the plot
            ax.tick_params(axis='x', which='both', direction='in')
            ax.tick_params(axis='y', which='both', direction='in')
            ax.set_xlabel(r'$p$ [GeV]', fontsize=12)
            if variable == 'd0':
                ax.set_ylabel(r'$\sigma(\Delta d_0)$ [$\mu$m]', fontsize=12)
            elif variable == 'z0':
                ax.set_ylabel(r'$\sigma(\Delta z_0)$ [$\mu$m]', fontsize=12)
            markers = ['o', 's', 'd', 'X', '^']
            handles = []
            labels = []

            for idx, (t, data_list) in enumerate(sorted(data_dict.items())):
                if t in [10, 30, 50, 70, 89]:
                    # plot the points by theta
                    momentum = data_dict[t]['momentum']
                    data = data_dict[t][variable]
                    data_mu = [val * 1000 for val in data]  # Convert d0/z0 from mm to μm
                    scatter = ax.scatter(momentum, data_mu, s=30, linewidth=0, marker=markers[idx % len(markers)])
                    handles.append(scatter)
                    labels.append(r'$\theta$ = '+str(t)+' deg')

           # Title depending on ftype
            if ftype == 'mu' or ftype == 'pi':
                title = r'Single $\mu^-$' if ftype == 'mu' else r'Single $\pi^-$'
            else:
                title = r'Single $e^-$'
            leg = plt.legend(handles, labels, loc='upper right', labelspacing=-0.2, title=title, title_fontsize='larger')
            leg._legend_box.align = "left"  # Make title align on the left

            # add text in the upper left corner
            text_str = "FCC−ee CLD"
            plt.text(-0.00005, 1.04, text_str, transform=ax.transAxes, fontsize=12, va='top', ha='left')
           # add text in the upper right corner
            text_str = f"~{args.Nevts} events/point"
            plt.text(1.0, 1.04, text_str, transform=ax.transAxes, fontsize=10, va='top', ha='right')

           # Save the plot to a file
            plt.savefig(os.path.join(output_dir, 'Impact_parameter_' + variable + '_resolution_' + f'{ftype}' + '.png'))
            plt.close(fig)  # close the figure to free up memory

       ## sigma(Delta d0) vs theta
       #----------------------------------
        def Impact_parameter_resolution_theta_plot():
            fig, ax = plt.subplots()
            ax.set_yscale('log')
            ax.xaxis.set_ticks_position('both') # Add graduations on top and right sides of the plot
            ax.yaxis.set_ticks_position('both') # Add graduations on top and right sides of the plot
            ax.tick_params(axis='x', which='both', direction='in')
            ax.tick_params(axis='y', which='both', direction='in')
            ax.set_xlabel(r'$\theta$ [deg]', fontsize=12)
            if variable == 'd0':
                ax.set_ylabel(r'$\sigma(\Delta d_0)$ [$\mu$m]', fontsize=12)
            elif variable == 'z0':
                ax.set_ylabel(r'$\sigma(\Delta z_0)$ [$\mu$m]', fontsize=12)
            markers = ['o', 's', 's', '^']
            handles = []
            labels = []

            for idx, (p, data_list_p) in enumerate(sorted(data_dict_p.items())):
                if p in [1, 10, 100]:
                   # plot the points by momentum
                    theta = data_dict_p[p]['theta']
                    data = data_dict_p[p][variable]
                    data_mu = [val * 1000 for val in data]  # Convert d0/z0 from mm to μm
                    scatter = ax.scatter(theta, data_mu, s=30, linewidth=0, marker=markers[idx % len(markers)])
                    handles.append(scatter)
                    labels.append(r'$p$ = '+str(p)+' GeV')

           # Title depending on ftype 
            if ftype == 'mu' or ftype == 'pi':
                title = r'Single $\mu^-$' if ftype == 'mu' else r'Single $\pi^-$'
            else:
                title = r'Single $e^-$'
            leg = plt.legend(handles, labels, loc='upper right', labelspacing=-0.2, title=title, title_fontsize='larger')
            leg._legend_box.align = "left" # Make title align on the left

           # add text in the upper left corner
            text_str = "FCC−ee CLD"
            plt.text(-0.00005, 1.04, text_str, transform=ax.transAxes, fontsize=12, va='top', ha='left')
           # add text in the upper right corner
            text_str = f"~{args.Nevts} events/point"
            plt.text(1.0, 1.04, text_str, transform=ax.transAxes, fontsize=10, va='top', ha='right')

           # Save the plot to a file
            plt.savefig(os.path.join(output_dir, 'Impact_parameter_' + variable + '_resolution_theta_' + f'{ftype}' + '.png'))
            plt.close(fig)  # close the figure to free up memory

        Impact_parameter_resolution_plot()
        Impact_parameter_resolution_theta_plot()
    #----------------------------------

############################### Efficiency PLOT ###############################
  #----------------------------------
  ## Single particle reconstruction efficiency vs pt
    def efficiency_plot(data_dict, ftype, Nevts, output_dir):
        fig, ax = plt.subplots()
        ax.set_xscale('log')
        ax.xaxis.set_ticks_position('both') # Add graduations on top and right sides of the plot
        ax.yaxis.set_ticks_position('both')
        ax.tick_params(axis='x', which='both', direction='in')
        ax.tick_params(axis='y', which='both', direction='in')
        ax.set_xlabel(r'$p_T$ [GeV]', fontsize=12)
        ax.set_ylabel('Reconstruction efficiency', fontsize=12)
        markers = ['o', 's', 'd', 'X', '^']
        handles = []
        labels = []

        for idx, (t, data_list) in enumerate(sorted(data_dict.items())):
           # plot the points by theta
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
        text_str = f"~{args.Nevts} events/point"
        plt.text(1.0, 1.04, text_str, transform=ax.transAxes, fontsize=10, va='top', ha='right')

       # Save the plot to a file
        plt.savefig(os.path.join(output_dir,'reco_efficiency_'+f'{ftype}'+'.png'))
        plt.close(fig)  # close the figure to free up memory
  #----------------------------------

#====================================================================
    #-------------------- Plots
    momentum_resolution_plots(data_dict, data_dict_p, ftype, {args.Nevts}, output_dir)
    Impact_parameter_esolution_plots(data_dict, data_dict_p, ftype, {args.Nevts}, output_dir, 'd0')
    Impact_parameter_esolution_plots(data_dict, data_dict_p, ftype, {args.Nevts}, output_dir, 'z0')
    efficiency_plot(data_dict, ftype, {args.Nevts}, output_dir)
#====================================================================

