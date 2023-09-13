import ROOT

def set_styles_and_colors_momentum(input_file_idx):
    marker_styles_full = [ROOT.kFullTriangleUp, ROOT.kFullSquare, ROOT.kFullDiamond, ROOT.kFullCross, ROOT.kFullCircle]
    marker_styles_open = [ROOT.kOpenTriangleUp, ROOT.kOpenSquare, ROOT.kOpenDiamond, ROOT.kOpenCross, ROOT.kOpenCircle]
    colors1 = [ROOT.kBlue, ROOT.kRed, ROOT.kMagenta, ROOT.kGreen, ROOT.kBlack]
    colors2 = [ROOT.kCyan, ROOT.kOrange+1, ROOT.kMagenta+3, ROOT.kGreen+3, ROOT.kGray]
    colors3 = [ROOT.kAzure+1, ROOT.kOrange+8, ROOT.kMagenta+2, ROOT.kGreen+2, ROOT.kGray+1]
    colors4 = [ROOT.kAzure+2, ROOT.kRed+2, ROOT.kMagenta-8, ROOT.kGreen-6, ROOT.kGray+2]

    style_map = {
        0: (marker_styles_full, colors2),
        1: (marker_styles_full, colors3),
        2: (marker_styles_open, colors1),
        3: (marker_styles_full, colors1),
        4: (marker_styles_full, colors4)
    }
    
    return style_map.get(input_file_idx, (marker_styles_full, colors1))

def set_styles_and_colors_theta(input_file_idx):
    marker_styles_full = [ROOT.kFullCircle, ROOT.kFullSquare, ROOT.kFullTriangleUp]
    marker_styles_open = [ROOT.kOpenCircle, ROOT.kOpenSquare, ROOT.kOpenTriangleUp]
    colors1 = [ROOT.kBlack, ROOT.kRed,ROOT.kBlue]
    colors2 = [ROOT.kGray+2, ROOT.kMagenta+2,ROOT.kCyan]
    colors3 = [ROOT.kGray+1, ROOT.kMagenta,ROOT.kCyan+2]
    colors4 = [ROOT.kGray, ROOT.kRed+2, ROOT.kBlue+2]

    style_map = {
        0: (marker_styles_full, colors2),
        1: (marker_styles_full, colors3),
        2: (marker_styles_open, colors1),
        3: (marker_styles_full, colors1),
        4: (marker_styles_full, colors4)
        #0: (marker_styles_open, colors1),
        #1: (marker_styles_full, colors1),
        #2: (marker_styles_full, colors2),
    }
    
    return style_map.get(input_file_idx, (marker_styles_full, colors1))

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

def combine_canvases(input_files, output_file, marker_styles_func, log_x=False, log_y=False):
    ROOT.gROOT.SetBatch(True)
    custom_texts = [", VXD res 1 #mum", ", VXD res 2 #mum", ", VXD res 3 #mum", ", VXD res 4 #mum", ", VXD res 5 #mum"]
    #custom_texts = [", VDX res 3 #mum", ", VDX res 5 #mum", ", VDX res 7 #mum"]

    #output_root_file = ROOT.TFile(output_file, "recreate")
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
        output_legend = ROOT.TLegend(0.90, 0.45, 1.20, 0.90)
        output_legend.SetTextFont(62)
        output_legend.SetFillStyle(0)
        output_legend.SetBorderSize(0)
        output_legend.SetHeader("Single #mu^{-}")

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
                            legend_label = f"{new_entry.GetLabel()}{custom_texts[input_file_idx]}\n"
                            output_legend.AddEntry(new_entry, legend_label, "P")

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
        
        # Draw the superposed TMultiGraph to the output canvas
        superposed_multigraph.Draw("APE" if output_canvas.GetListOfPrimitives().GetSize() == 0 else "APEsame")
        
        # Set the X-axis title
        if marker_styles_func == momentum_styles:
            superposed_multigraph.GetXaxis().SetTitle("momentum [GeV]")
        elif marker_styles_func == theta_styles:
            superposed_multigraph.GetXaxis().SetTitle("#theta [deg]")
        superposed_multigraph.GetXaxis().SetTitleSize(0.05)
        
        # Set the Y-axis title based on the input canvas name
        y_axis_title = set_y_axis_title(canvas_name)
        superposed_multigraph.GetYaxis().SetTitle(y_axis_title)
        superposed_multigraph.GetYaxis().SetTitleSize(0.05)
        
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
        text_left_x = 0.10
        text_left_y = 0.91
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
        latex_left.DrawLatexNDC(text_left_x, text_left_y, "FCC-ee CLD")
        output_canvas.Print(output_pdf_file, "pdf")

    output_pdf_canvas.Print(output_pdf_file + "]")
    output_root_file.Close()

if __name__ == "__main__":
    momentum_styles = set_styles_and_colors_momentum
    theta_styles = set_styles_and_colors_theta

    input_files = [
        #"/afs/cern.ch/user/g/gasadows/Output/FCCee_o2_v02/final_1mic/p_dist.root",
        #"/afs/cern.ch/user/g/gasadows/Output/FCCee_o2_v02/final_2mic/p_dist.root",
        #"/afs/cern.ch/user/g/gasadows/Output/FCCee_o2_v02/final_3mic/p_dist.root",
        #"/afs/cern.ch/user/g/gasadows/Output/FCCee_o2_v02/final_4mic/p_dist.root",
        #"/afs/cern.ch/user/g/gasadows/Output/FCCee_o2_v02/final_5mic/p_dist.root"
        '/afs/cern.ch/user/g/gasadows/Output/FCCee_o1_v04/final_3mic/p_dist.root',
        '/afs/cern.ch/user/g/gasadows/Output/FCCee_o1_v04/final_5mic/p_dist.root',
        '/afs/cern.ch/user/g/gasadows/Output/FCCee_o1_v04/final_7mic/p_dist.root'
    ]
    output_file = "combined_canvas_momentum"
    combine_canvases(input_files, output_file, momentum_styles, log_x=True, log_y=True)

    input_files = [
        "/afs/cern.ch/user/g/gasadows/Output/FCCee_o2_v02/final_1mic/t_dist.root",
        "/afs/cern.ch/user/g/gasadows/Output/FCCee_o2_v02/final_2mic/t_dist.root",
        "/afs/cern.ch/user/g/gasadows/Output/FCCee_o2_v02/final_3mic/t_dist.root",
        "/afs/cern.ch/user/g/gasadows/Output/FCCee_o2_v02/final_4mic/t_dist.root",
        "/afs/cern.ch/user/g/gasadows/Output/FCCee_o2_v02/final_5mic/t_dist.root"
        #'/afs/cern.ch/user/g/gasadows/Output/FCCee_o1_v04/final_3mic/t_dist.root',
        #'/afs/cern.ch/user/g/gasadows/Output/FCCee_o1_v04/final_5mic/t_dist.root',
        #'/afs/cern.ch/user/g/gasadows/Output/FCCee_o1_v04/final_7mic/t_dist.root'
    ]
    output_file = "combined_canvas_theta"
    combine_canvases(input_files, output_file, theta_styles, log_x=False, log_y=True)
