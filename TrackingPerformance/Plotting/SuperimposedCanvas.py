import ROOT

def set_y_axis_title(canvas_name):
    y_axis_titles = {
        "Canvas_delta_d0": "#sigma(#Deltad_{0}) [#mum]",
        "Canvas_delta_z0": "#sigma(#Deltaz_{0}) [#mum]",
        "Canvas_delta_phi0": "#Delta#phi_{0}",
        "Canvas_delta_omega": "#Delta#Omega",
        "Canvas_delta_tanLambda": "tan #Lambda",
        "Canvas_delta_phi": "#sigma(#Delta#phi) [mrad]",
        "Canvas_delta_theta": "#sigma(#Delta#theta) [mrad]",
        "Canvas_sdelta_pt": "#sigma(#Deltap_{T}/p_{T,true}^{2}) [GeV^{-1}]",
        "Canvas_sdelta_p": "#sigma(#Deltap/p_{true}^{2}) [GeV^{-1}]"
    }
    return y_axis_titles.get(canvas_name, "Some Default Y-axis Title")

def set_y_axis_range_theta(canvas_name):
    y_axis_range = {
        "Canvas_delta_d0": (0.5, 10**4),
        "Canvas_delta_z0": (0.5, 10**4),
        "Canvas_delta_phi0": (10**-5, 1),
        "Canvas_delta_omega": (10**-8, 10**-2),
        "Canvas_delta_tanLambda": (10**-5, 10),
        "Canvas_delta_phi": (10**-2, 10**3),
        "Canvas_delta_theta": (10**-2, 10**3),
        "Canvas_sdelta_pt": (10**-5, 10**2),
        "Canvas_sdelta_p": (10**-5, 10**2),
    }
    return y_axis_range.get(canvas_name, "Some Default Y-axis range")

def set_y_axis_range_momentum(canvas_name):
    y_axis_range = {
        "Canvas_delta_d0": (0.5, 10**3),
        "Canvas_delta_z0": (0.5, 10**4),
        "Canvas_delta_phi0": (10**-5, 10**-1),
        "Canvas_delta_omega": (10**-8, 10**-3),
        "Canvas_delta_tanLambda": (10**-5, 10),
        "Canvas_delta_phi": (10**-2, 10**2),
        "Canvas_delta_theta": (10**-2, 10),
        "Canvas_sdelta_pt": (10**-5, 10),
        "Canvas_sdelta_p": (10**-5, 1),
    }
    return y_axis_range.get(canvas_name, "Some Default Y-axis range")

def combine_canvases(input_files, output_file, marker_styles_func, legend_text, log_x=False, log_y=False):
    ROOT.gROOT.SetBatch(True)

    output_root_file = ROOT.TFile(output_file + ".root", "recreate")
    output_pdf_file = output_file + ".pdf"
    output_pdf_canvas = ROOT.TCanvas("combined_canvas", "Combined Canvas", 800, 800)
    output_pdf_canvas.Print(output_pdf_file + "[")

    for canvas_name in [
        "Canvas_delta_d0", "Canvas_delta_z0", "Canvas_delta_phi0", "Canvas_delta_omega",
        "Canvas_delta_tanLambda", "Canvas_delta_phi", "Canvas_delta_theta",
        "Canvas_sdelta_pt", "Canvas_sdelta_p"
    ]:
        superposed_multigraph = ROOT.TMultiGraph()
       # Define different legend position for theta and momentum plots
        if marker_styles_func == momentum_styles:
            output_legend = ROOT.TLegend(0.55, 0.55, 1.30, 0.92)
            #output_legend = ROOT.TLegend(0.65, 0.55, 1.30, 0.92)    #x1,y1,x2,y2 normalised coordinates in the current pad 
        elif marker_styles_func == theta_styles:
            output_legend = ROOT.TLegend(0.5, 0.60, 1.15, 0.92)    #x1,y1,x2,y2 normalised coordinates in the current pad
        output_legend.SetTextFont(62)
        output_legend.SetTextSize(0.03)
        output_legend.SetFillStyle(0)
        output_legend.SetBorderSize(0)
        output_legend.SetMargin(0.1)    # distance between marker and text
        #output_legend.SetHeader("Single #mu^{-}")

        for input_file_idx, input_file in enumerate(input_files):
            input_root_file = ROOT.TFile(input_file)
            input_canvas = input_root_file.Get(canvas_name)
            
            if input_canvas and input_canvas.InheritsFrom("TCanvas"):
                primitives = input_canvas.GetListOfPrimitives()
                for i in range(primitives.GetSize()):
                    obj = primitives.At(i)
                    if obj.InheritsFrom("TMultiGraph"):
                        multigraph = obj.Clone()
                        graph_count = multigraph.GetListOfGraphs().GetSize()
                        new_graphs = []

                        marker_styles, marker_colors = marker_styles_func(input_file_idx)
                        for i, graph in enumerate(multigraph.GetListOfGraphs()):
                            new_graph = ROOT.TGraphErrors(graph.GetN(), graph.GetX(), graph.GetY(), graph.GetEX(), graph.GetEY())
                            new_marker_style = marker_styles[i % len(marker_styles)]
                            new_marker_color = marker_colors[i % len(marker_colors)]
                            new_graph.SetMarkerStyle(new_marker_style)
                            new_graph.SetMarkerColor(new_marker_color)
                            new_graphs.append(new_graph)

                        new_multigraph = ROOT.TMultiGraph()
                        for new_graph in new_graphs:
                            new_multigraph.Add(new_graph)

                        superposed_multigraph.Add(new_multigraph.Clone())
                        break

                legend = None
                for prim in input_canvas.GetListOfPrimitives():
                    if prim.InheritsFrom("TLegend"):
                        legend = prim
                        break

                if legend:
                    input_legend = None
                    for prim in input_canvas.GetListOfPrimitives():
                        if prim.InheritsFrom("TLegend"):
                            input_legend = prim
                            break
                    
                    if input_legend:
                        for marker_idx in range(len(marker_styles)):   
                            new_entry = input_legend.GetListOfPrimitives().At(marker_idx).Clone()
                            new_entry.SetTextFont(43)
                            new_entry.SetFillStyle(0)
                            new_entry.SetMarkerStyle(marker_styles[marker_idx])
                            new_entry.SetMarkerColor(marker_colors[marker_idx])
                            new_entry.SetMarkerSize(1.5) 
                            legend_label = f"{new_entry.GetLabel()}{legend_text[input_file_idx]}\n"
                            output_legend.AddEntry(new_entry, legend_label, "P")
                        #for marker_idx in range(1, len(marker_styles) + 1 ): # Skip legend Title
                        #    new_entry = input_legend.GetListOfPrimitives().At(marker_idx).Clone()
                        #    new_entry.SetTextFont(43)
                        #    new_entry.SetFillStyle(0)
                        #    adjusted_idx = marker_idx - 1
                        #    new_entry.SetMarkerStyle(marker_styles[adjusted_idx])
                        #    new_entry.SetMarkerColor(marker_colors[adjusted_idx])
                        #    new_entry.SetMarkerSize(1.5)
                        #    legend_label = f"{new_entry.GetLabel()}{legend_text[input_file_idx]}\n"
                        #    output_legend.AddEntry(new_entry, legend_label, "P")


        output_canvas = ROOT.TCanvas(canvas_name, "Superposed Canvas", 800, 800)
        
        # Set log scales for X and Y axes
        if log_x:
            output_canvas.SetLogx()
        if log_y:
            output_canvas.SetLogy()
        
        # Get the current pad
        pad = output_canvas.GetPad(0)
        # Set the position of the right and top axes
        pad.SetTickx(1)
        pad.SetTicky(1)
        # Set canvas margins
        output_canvas.SetRightMargin(0.02)
        output_canvas.SetLeftMargin(0.185)
        output_canvas.SetTopMargin(0.06)
        output_canvas.SetBottomMargin(0.15)
        
        # Draw the superposed TMultiGraph to the output canvas
        superposed_multigraph.Draw("APE" if output_canvas.GetListOfPrimitives().GetSize() == 0 else "APEsame")
        
        # Set the X-axis title
        if marker_styles_func == momentum_styles:
            superposed_multigraph.GetXaxis().SetTitle("momentum [GeV]")
        elif marker_styles_func == theta_styles:
            superposed_multigraph.GetXaxis().SetTitle("#theta [deg]")
        superposed_multigraph.GetXaxis().SetTitleSize(0.06)
        
        # Set the Y-axis title based on the input canvas name
        y_axis_title = set_y_axis_title(canvas_name)
        superposed_multigraph.GetYaxis().SetTitle(y_axis_title)
        superposed_multigraph.GetYaxis().SetTitleSize(0.06)

        # Set Y-axis range
        if marker_styles_func == theta_styles:
            y_axis_range = set_y_axis_range_theta(canvas_name)
            superposed_multigraph.GetYaxis().SetRangeUser(y_axis_range[0],y_axis_range[1])
        elif marker_styles_func == momentum_styles:
            y_axis_range = set_y_axis_range_momentum(canvas_name)
            superposed_multigraph.GetYaxis().SetRangeUser(y_axis_range[0],y_axis_range[1])
        
        # Set bigger axis scale numbers
        superposed_multigraph.GetXaxis().SetLabelSize(0.05)
        superposed_multigraph.GetYaxis().SetLabelSize(0.05)
        
        # Increase the marker size
        marker_size = 1.5
        for graph in superposed_multigraph.GetListOfGraphs():
            graph.SetMarkerSize(marker_size)
        
        # Draw the legend on the output canvas
        output_legend.Draw()
        
        # Add text on the top left above the graph
        text_left_x = 0.19
        text_left_y = 0.95
        latex_left = ROOT.TLatex()
        latex_left.SetNDC()
        latex_left.SetTextFont(42)
        latex_left.SetTextSize(0.04)
        latex_left.DrawLatexNDC(text_left_x, text_left_y, "FCC-ee CLD")
        
        # Save the output canvas to the root file
        output_root_file.cd()
        output_canvas.Write()

        # Save the output canvas as a PDF page
        output_pdf_canvas.Clear()
        superposed_multigraph.Draw("APE" if output_canvas.GetListOfPrimitives().GetSize() == 0 else "APEsame")
        output_legend.Draw()
        latex_left.DrawLatexNDC(text_left_x, text_left_y, "FCC-ee CLD (o2_v05)")
        output_canvas.Print(output_pdf_file, "pdf")

    output_pdf_canvas.Print(output_pdf_file + "]")
    output_root_file.Close()

if __name__ == "__main__":  

    def set_styles_and_colors_momentum(input_file_idx):
        marker_styles_full = [ROOT.kFullTriangleUp, ROOT.kFullSquare, ROOT.kFullDiamond, ROOT.kFullCross, ROOT.kFullCircle]
        marker_styles_open = [ROOT.kOpenTriangleUp, ROOT.kOpenSquare, ROOT.kOpenDiamond, ROOT.kOpenCross, ROOT.kOpenCircle]
        colors1 = [ROOT.kBlue, ROOT.kRed, ROOT.kMagenta, ROOT.kGreen, ROOT.kBlack]
        colors2 = [ROOT.kCyan, ROOT.kOrange+1, ROOT.kMagenta+3, ROOT.kGreen+3, ROOT.kGray]
        colors3 = [ROOT.kAzure+1, ROOT.kOrange+8, ROOT.kMagenta+2, ROOT.kGreen+2, ROOT.kGray+1]
        colors4 = [ROOT.kAzure+2, ROOT.kRed+2, ROOT.kMagenta-8, ROOT.kGreen-6, ROOT.kGray+2]

        style_map = {
            #0: (marker_styles_full, colors2),
            #1: (marker_styles_open, colors1),
            #2: (marker_styles_full, colors3),
            #3: (marker_styles_full, colors1),
            #0: (marker_styles_open, colors1),
            #1: (marker_styles_full, colors1),
            #2: (marker_styles_full, colors2),
            0: (marker_styles_full, colors1),
            1: (marker_styles_open, colors1),
        }
        
        return style_map.get(input_file_idx, (marker_styles_full, colors1))
    momentum_styles = set_styles_and_colors_momentum

    def set_styles_and_colors_theta(input_file_idx):
        marker_styles_full = [ROOT.kFullCircle, ROOT.kFullSquare, ROOT.kFullTriangleUp]
        marker_styles_full2 = [ ROOT.kFullSquare, ROOT.kFullTriangleUp]
        marker_styles_open = [ROOT.kOpenCircle, ROOT.kOpenSquare, ROOT.kOpenTriangleUp]
        colors1 = [ROOT.kBlack, ROOT.kRed,ROOT.kBlue]
        colors2 = [ROOT.kGray+1, ROOT.kMagenta,ROOT.kCyan]
        colors3 = [ROOT.kGray+2, ROOT.kMagenta+2,ROOT.kCyan+2]
        colors4 = [ROOT.kGray, ROOT.kRed+2, ROOT.kBlue+2]

        style_map = {
            0: (marker_styles_open, colors1),
            1: (marker_styles_full, colors1),
            2: (marker_styles_full, colors2),
            #3: (marker_styles_full, colors3),
            #0: (marker_styles_full, colors3),
            #1: (marker_styles_open, colors1),
            #2: (marker_styles_full, colors1),
            #3: (marker_styles_full, colors2),
        }
        
        return style_map.get(input_file_idx, (marker_styles_full, colors1))
    theta_styles = set_styles_and_colors_theta
#_________________________________________________________________
# Traking performances as a function of Tranverse Momentum

    input_files = [
        #"/eos/user/g/gasadows/Output/TrackingPerformance/LCIO/analysis/Output/CLD_o2_v05/final_VXD_3mic_IT_5_7mic/p_dist.root",
        #'/eos/user/g/gasadows/Output/TrackingPerformance/LCIO/analysis/Output/CLD_o2_v05/final_3mic/p_dist.root',
        #"/eos/user/g/gasadows/Output/TrackingPerformance/LCIO/analysis/Output/CLD_o2_v05/final_VXD_3mic_IT_9_11mic/p_dist.root",
        '/eos/user/g/gasadows/Output/TrackingPerformance/CLD_o2_v05/analysis/VXD_1mic/plots/p_dist.root',
        '/eos/user/g/gasadows/Output/TrackingPerformance/CLD_o2_v05/analysis/final/VXD_3mic/p_dist.root',
        #'/eos/user/g/gasadows/Output/TrackingPerformance/LCIO/analysis/Output/CLD_o2_v05/final_5mic/p_dist.root',
        #'/eos/user/g/gasadows/Output/TrackingPerformance/LCIO/analysis/Output/CLD_o2_v05/final_7mic/p_dist.root',
        #"/eos/user/g/gasadows/Output/TrackingPerformance/LCIO/analysis/Output/FCCee_o1_v04/final_3mic/p_dist.root",
        #"/eos/user/g/gasadows/Output/TrackingPerformance/LCIO/analysis/Output/FCCee_o1_v04/final_7mic/p_dist.root",
        #'/eos/user/g/gasadows/Output/TrackingPerformance/LCIO/analysis/Output/FCCee_o1_v04/final_5mic/p_dist.root',
        #"/eos/user/g/gasadows/Output/TrackingPerformance/CLD_o2_v05/analysis/final/VXD_3mic/p_dist.root",
        #"/eos/user/g/gasadows/Output/TrackingPerformance/CLD_o2_v05/analysis2/plots/p_dist.root",
        #"/eos/user/g/gasadows/Output/TrackingPerformance/CLD_o3_v01/analysis/plots/p_dist.root",
    ]
    output_file = "combined_canvas_momentum"
    legend_text = [", VDX res 1 #mum", ", VDX res 3 #mum"]
    #combine_canvases(input_files, output_file, momentum_styles, legend_text, log_x=True, log_y=True)

#_________________________________________________________________
# Traking performances as a function of Theta

    input_files = [
        #"/eos/user/g/gasadows/Output/TrackingPerformance/CLD_o2_v05/analysis/VXD_1mic/plots/t_dist.root",
        #"/eos/user/g/gasadows/Output/TrackingPerformance/CLD_o2_v05/analysis/final/VXD_3mic/t_dist.root",
        "/eos/user/g/gasadows/Output/TrackingPerformance/CLD_o2_v05/analysis/test_CT005/final_VXD_3mic/t_dist.root",
        #"/eos/user/g/gasadows/Output/TrackingPerformance/CLD_o2_v05/analysis2/plots/t_dist.root",
        #"/eos/user/g/gasadows/Output/TrackingPerformance/CLD_o2_v05/analysis/VXD_5mic/plots/t_dist.root",
        #"/eos/user/g/gasadows/Output/TrackingPerformance/CLD_o2_v05/analysis/VXD_7mic/plots/t_dist.root",
        #"/eos/user/g/gasadows/Output/TrackingPerformance/CLD_o3_v01/analysis/plots/t_dist.root",
        #"/eos/user/g/gasadows/Output/TrackingPerformance/CLD_o2_v05_old_beamPipe/analysis/VXD_3mic/plots/t_dist.root",
        #"/eos/user/g/gasadows/Output/TrackingPerformance/CLD_o2_v05/analysis_OT_thirdLayer_1mic/plots/t_dist.root",
        #"/eos/user/g/gasadows/Output/TrackingPerformance/CLD_o2_v05/Analysis/OT_midLayer_200mic/plots/t_dist.root",
        #"/eos/user/g/gasadows/Output/TrackingPerformance/CLD_o2_v05/analysis/mu/plots/t_dist.root",
        #"/eos/user/g/gasadows/Output/TrackingPerformance/CLD_o2_v05/analysis/e/plots/t_dist.root",
        #"/eos/user/g/gasadows/Output/TrackingPerformance/CLD_o2_v05/analysis/pi/plots/t_dist.root",
        "/eos/user/g/gasadows/Output/TrackingPerformance/CLD_o2_v05/analysis/old_BP2/plots/t_dist.root",
    ]
    output_file = "combined_canvas_theta"
    #legend_text = [", VDX res 3 #mum", ", VDX res 5 #mum", ", VDX res 7 #mum"]
    #legend_text = [", o2_v05", ", OT 3rd resU = 1 #mum", ", OT 2nd resU = 200 #mum"]
    legend_text = [", BP = 1.7 mm AlBeMet + paraffin ", ", BP = 1.2 mm Be"]
    #legend_text = [", o2_v05", ", o3_v01"]
    #legend_text = [", Single #mu^{-}", ", Single e^{-}", ", Single #pi^{-}"]
    combine_canvases(input_files, output_file, theta_styles, legend_text, log_x=False, log_y=True)
