import ROOT
import os
ROOT.gROOT.SetBatch(True)  # Run ROOT in batch mode to avoid displaying the plot

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
        "Canvas_delta_phi0": (0.15*(10**-4), 1),
        "Canvas_delta_omega": (0.15*(10**-7), 10**-2),
        "Canvas_delta_tanLambda": (0.15*(10**-4), 10),
        "Canvas_delta_phi": (0.15*(10**-1), 10**3),
        "Canvas_delta_theta": (0.15*(10**-1), 10**3),
        "Canvas_sdelta_pt": (0.15*(10**-4), 5),
        "Canvas_sdelta_p": (0.15*(10**-4), 5),
    }
    return y_axis_range.get(canvas_name, (1, 100))  # Default range if canvas_name not found

def set_y_axis_range_momentum(canvas_name):
    y_axis_range = {
        "Canvas_delta_d0": (0.5, 10**3),
        "Canvas_delta_z0": (0.5, 10**4),
        "Canvas_delta_phi0": (0.15*(10**-4), 10**-1),
        "Canvas_delta_omega": (0.15*(10**-7), 10**-3),
        "Canvas_delta_tanLambda": (0.15*(10**-4), 10),
        "Canvas_delta_phi": (0.15*(10**-1), 10**2),
        "Canvas_delta_theta": (0.15*(10**-1), 10),
        "Canvas_sdelta_pt": (0.15*(10**-4), 10),
        "Canvas_sdelta_p": (0.15*(10**-4), 1),
    }
    return y_axis_range.get(canvas_name, (1, 100))  # Default range if canvas_name not found

def marker_styles_func(file_identifier, graph_type, canvas_style):
    # Define marker styles and colors based on file content and graph type ('a' or 'b')
    if canvas_style == 'theta':
        styles = {
            '1': {'a': [ROOT.kOpenCircle], 'b': [ROOT.kFullCircle], 'color': ROOT.kBlack},
            '10': {'a': [ROOT.kOpenSquare], 'b': [ROOT.kFullSquare], 'color': ROOT.kRed},
            '100': {'a': [ROOT.kOpenTriangleUp], 'b': [ROOT.kFullTriangleUp], 'color': ROOT.kBlue},
        }
    elif canvas_style == 'momentum':
        styles = {
            '10': {'a': [ROOT.kOpenTriangleUp], 'b': [ROOT.kFullTriangleUp], 'color': ROOT.kBlue},
            '30': {'a': [ROOT.kOpenSquare], 'b': [ROOT.kFullSquare], 'color': ROOT.kRed},
            '50': {'a': [ROOT.kOpenDiamond], 'b': [ROOT.kFullDiamond], 'color': ROOT.kMagenta},
            '70': {'a': [ROOT.kOpenCross], 'b': [ROOT.kFullCross], 'color': ROOT.kGreen},
            '89': {'a': [ROOT.kOpenCircle], 'b': [ROOT.kFullCircle], 'color': ROOT.kBlack},
        }
    else:
        raise ValueError(f"Invalid canvas style: {canvas_style}")

    if file_identifier not in styles:
        raise ValueError(f"Unknown file identifier: {file_identifier}")

    selected_style = styles[file_identifier][graph_type]
    selected_color = styles[file_identifier]['color']

    return selected_style, [selected_color]  # Return color in a list for consistency

def process_canvas(input_file, canvas_name, graph_type, file_identifier, canvas_style):
    input_root_file = ROOT.TFile.Open(input_file)
    input_canvas = input_root_file.Get(canvas_name)
    new_graphs = []

    if input_canvas and input_canvas.InheritsFrom("TCanvas"):
        primitives = input_canvas.GetListOfPrimitives()
        for obj in primitives:
            if obj.InheritsFrom("TMultiGraph"):
                multigraph = obj
                for i, graph in enumerate(multigraph.GetListOfGraphs()):
                    selected_style, selected_color = marker_styles_func(file_identifier, graph_type, canvas_style)
                    new_marker_style = selected_style[i % len(selected_style)]
                    new_marker_color = selected_color[0]
                    new_graph = ROOT.TGraphErrors(graph.GetN(), graph.GetX(), graph.GetY(), graph.GetEX(), graph.GetEY())
                    new_graph.SetMarkerStyle(new_marker_style)
                    new_graph.SetMarkerColor(new_marker_color)
                    new_graphs.append(new_graph)
    input_root_file.Close()
    return new_graphs

def add_entries_from_canvas(input_canvas, styles, colors, output_legend, additional_text):
    legend = None
    for prim in input_canvas.GetListOfPrimitives():
        if prim.InheritsFrom("TLegend"):
            legend = prim
            break
            
    if legend:
        for idx, entry in enumerate(legend.GetListOfPrimitives()):
            # Skip the first element if necessary
            if idx == 0:
                continue
            new_entry = entry.Clone()
            # Apply the style and color based on the index
            new_entry.SetMarkerStyle(styles[idx % len(styles)])
            new_entry.SetMarkerColor(colors[idx % len(colors)])
            new_entry.SetMarkerSize(1.5)
            legend_label = f"{new_entry.GetLabel()}{additional_text}"
            output_legend.AddEntry(new_entry, legend_label, "P")

# Example of extracting file identifier from file name
def extract_file_identifier(file_name, canvas_style):
    if canvas_style == 'theta':
        # Processing for 'theta' style
        if '1.root' in file_name:
            return '1'
        elif '10.root' in file_name:
            return '10'
        elif '100.root' in file_name:
            return '100'
        else:
            raise ValueError(f"Unable to extract file identifier from {file_name}")
    elif canvas_style == 'momentum':
        # Processing 'momentum' style with specific endings
        if '10.root' in file_name:
            return '10'
        elif '30.root' in file_name:
            return '30'
        elif '50.root' in file_name:
            return '50'
        elif '70.root' in file_name:
            return '70'
        elif '89.root' in file_name:
            return '89'
        else:
            raise ValueError(f"Unable to extract file identifier from {file_name}")
    else:
        raise ValueError(f"Invalid canvas style: {canvas_style}")

def process_and_compare_graphs(output_file_path, canvas_names, folder_a, folder_b, file_names, canvas_style, legend_txt):
    # Open the output ROOT file
    output_root_file = ROOT.TFile(output_file_path, "RECREATE")
    output_pdf_canvas = ROOT.TCanvas("combined_canvas_ratio", "Combined Canvas Ratio", 600, 600)
    output_pdf_file = output_file_path[:-5] + ".pdf"
    output_pdf_canvas.Print(output_pdf_file + "[")
    
    graphs_from_a = {cn: [] for cn in canvas_names}
    graphs_from_b = {cn: [] for cn in canvas_names}
    ratio_graphs = {cn: [] for cn in canvas_names}
    
    for canvas_name in canvas_names:
        legends_from_graphs = []
        for file_name in file_names:

            file_path_a = os.path.join(folder_a, file_name)
            file_path_b = os.path.join(folder_b, file_name)
            # When calling process_canvas for each file
            file_identifier_a = extract_file_identifier(file_path_a, canvas_style)
            graphs_a = process_canvas(folder_a + file_name, canvas_name, 'a', file_identifier_a, canvas_style)  

            file_identifier_b = extract_file_identifier(file_path_b, canvas_style)
            graphs_b = process_canvas(folder_b + file_name, canvas_name, 'b', file_identifier_b, canvas_style)  

            # Create a new canvas for comparison and ratio plots
            output_root_file.cd()
            comparison_canvas = ROOT.TCanvas(f"{canvas_name}_{file_name[:-5]}", f"Comparison: {canvas_name}", 600, 600)
            comparison_canvas.Divide(1, 2)  # Divide the canvas for original and ratio plots
            
            # Top pad 
            pad1 = ROOT.TPad("pad1", "pad1", 0, 0.3, 1, 1.0)
            pad1.SetBottomMargin(0.0001)  
            pad1.SetLeftMargin(0.2)
            pad1.SetRightMargin(0.02)
            pad1.SetTopMargin(0.035)
            pad1.Draw()
            pad1.cd()
            # Set the position of the right and top axes
            pad1.SetTickx(1)
            pad1.SetTicky(1)

            # Drawing logic for graphs_a
            for i, graph in enumerate(graphs_a):
                file_identifier = extract_file_identifier(folder_a + file_name, canvas_style)
                marker_styles, marker_colors = marker_styles_func(file_identifier, 'a', canvas_style)
                graph.SetMarkerStyle(marker_styles[i % len(marker_styles)])
                graph.SetMarkerColor(marker_colors[0])
                graph.SetLineColor(marker_colors[0])
                y_axis_title = set_y_axis_title(canvas_name)
                graph.GetYaxis().SetTitle(y_axis_title)
                graph.GetXaxis().SetLabelSize(0)
                graph.GetYaxis().SetTitleSize(0.08) 
                graph.GetYaxis().SetLabelSize(0.07)
                graph.SetTitle("")
                pad1.cd()
                graph.Draw("AP" if graph == graphs_a[0] else "P SAME")  # Draw the first graph with axes, others on top
                graphs_from_a[canvas_name].append(graph)

            # Drawing logic for graphs_b
            for i, graph in enumerate(graphs_b):
                file_identifier = extract_file_identifier(folder_b + file_name, canvas_style)
                marker_styles, marker_colors = marker_styles_func(file_identifier, 'b', canvas_style)
                graph.SetMarkerStyle(marker_styles[i % len(marker_styles)])
                graph.SetMarkerColor(marker_colors[0])
                graph.SetLineColor(marker_colors[0])
                graph.GetXaxis().SetLabelSize(0)
                graph.SetTitle("")
                pad1.cd()
                graph.Draw("P SAME")  # Draw on top of existing graphs without axes
                graphs_from_b[canvas_name].append(graph)
            
            pad1.Update()

            # Adjust to log scale if needed
            pad1.SetLogy()
            if canvas_style == "momentum": pad1.SetLogx()

            pad1.Update()

            # Bottom pad 
            comparison_canvas.cd()  # Go back to the canvas to add the second pad

            pad2 = ROOT.TPad("pad2", "pad2", 0, 0.0, 1, 0.3)
            pad2.SetTopMargin(0.0)  # Set a top margin to visually separate pads
            pad2.SetBottomMargin(0.5)  # Increase bottom margin for axis labels
            pad2.SetLeftMargin(0.2)
            pad2.SetRightMargin(0.02)
            if canvas_style == "momentum": pad2.SetLogx()
            pad2.Draw()
            pad2.cd()
            
            # Example logic for calculating and drawing ratio
            # This is a placeholder and should be replaced with actual calculation
            if graphs_a and graphs_b:
                # Assume both graphs have the same number of points here for simplicity
                n_points = graphs_a[0].GetN()
                x = graphs_a[0].GetX()
                y_ratio = ROOT.TGraphErrors(n_points)  # Create an empty TGraphErrors for ratio
                for i in range(n_points):
                    xa = graphs_a[0].GetX()[i]
                    ya = graphs_a[0].GetY()[i]
                    yb = graphs_b[0].GetY()[i]
                    eya = graphs_a[0].GetEY()[i]
                    eyb = graphs_b[0].GetEY()[i]
                    ratio = ya / yb if yb != 0 else 0
                    error = ratio * ((eya/ya)**2 + (eyb/yb)**2)**0.5 if ya != 0 and yb != 0 else 0
                    
                    y_ratio.SetPoint(i, xa, ratio)
                    y_ratio.SetPointError(i, 0, error)
                    file_identifier = extract_file_identifier(folder_b + file_name, canvas_style)
                    marker_styles, marker_colors = marker_styles_func(file_identifier, 'b', canvas_style)
                    y_ratio.SetMarkerStyle(marker_styles[i % len(marker_styles)])
                    y_ratio.SetMarkerColor(marker_colors[0])
                    y_ratio.SetLineColor(marker_colors[0])
                    # Calculate uncertainties for ratio here, if applicable

                y_ratio.GetXaxis().SetTitleSize(0.18) 
                y_ratio.GetXaxis().SetLabelSize(0.15)
                y_ratio.GetXaxis().SetTickSize(0.11)
                y_ratio.GetYaxis().SetLabelSize(0.08)
                y_ratio.SetTitle(";#theta [deg];") if canvas_style == "theta" else y_ratio.SetTitle(";momentum [GeV];")
                y_ratio.Draw("AP")
                ratio_graphs[canvas_name].append(y_ratio)
                pad2.Update()

                # After you have drawn your ratio_graph and updated pad2
                # Determine the x-axis range of your ratio plot
                x_min = y_ratio.GetXaxis().GetXmin()
                x_max = y_ratio.GetXaxis().GetXmax()
                # Create a TLine at Y = 1 spanning the width of the x-axis range
                line = ROOT.TLine(x_min, 1, x_max, 1)
                line.SetLineColor(ROOT.kBlack)  # Set line color, e.g., red
                line.SetLineStyle(2)  # Set line style to dotted
                # Draw the line on the same pad as your ratio plot
                line.Draw("same")
                pad2.Update()

                # Create a new combined legend
                # Example of how you would call this in your loop
                file_identifier_a = extract_file_identifier(folder_a + file_name, canvas_style)
                file_identifier_b = extract_file_identifier(folder_b + file_name, canvas_style)

                input_canvas_a = ROOT.TFile.Open(folder_a + file_name).Get(canvas_name)
                input_canvas_b = ROOT.TFile.Open(folder_b + file_name).Get(canvas_name)

                # Create the legend
                output_legend = ROOT.TLegend(0.65, 0.5, 0.9, 0.93)
                output_legend.SetTextFont(62)
                output_legend.SetTextSize(0.04)
                output_legend.SetFillStyle(0)
                output_legend.SetBorderSize(0)
                output_legend.SetMargin(0.1)    # distance between marker and text
                output_legend.SetHeader("Single #mu^{-}")

                # Ensure legend_txt has at least 2 elements to avoid index errors
                if len(legend_txt) < 2:
                    raise ValueError("legend_txt must contain at least 2 elements.")

                # Get marker styles and colors based on file identifiers
                marker_styles_a, marker_colors_a = marker_styles_func(file_identifier_a, 'a', canvas_style)
                marker_styles_b, marker_colors_b = marker_styles_func(file_identifier_b, 'b', canvas_style)

                # Process the first canvas
                add_entries_from_canvas(input_canvas_a, marker_styles_a, marker_colors_a, output_legend, legend_txt[0])
                # Process the second canvas
                add_entries_from_canvas(input_canvas_b, marker_styles_b, marker_colors_b, output_legend, legend_txt[1])
                legends_from_graphs.append(output_legend)

                pad1.cd()  # Switch to the pad where you want the legend to appear
                output_legend.Draw()
                pad1.Update()

            # Write the canvas to the output file
            output_root_file.cd()
            comparison_canvas.Write()

            output_pdf_canvas.Clear()
            comparison_canvas.Draw("APE" if comparison_canvas.GetListOfPrimitives().GetSize() == 0 else "APEsame")
            output_legend.Draw()
            comparison_canvas.Print(output_pdf_file, "pdf")

        # Create a combined canvas for the current canvas_name
        combined_canvas_name = f"combined_{canvas_name}"
        combined_canvas = ROOT.TCanvas(combined_canvas_name, combined_canvas_name, 600, 600)
        combined_canvas.Divide(1, 2)  # Divide the canvas into two pads: top and bottom

        # Top pads
        top_pad = combined_canvas.cd(1)
        top_pad.SetPad(0.0, 0.3, 1.0, 1.0)  # Adjust these parameters as needed for layout
        top_pad.SetRightMargin(0.02)
        top_pad.SetTopMargin(0.035)
        top_pad.SetBottomMargin(0.0001)  
        top_pad.SetLeftMargin(0.2)

        # Set the position of the right and top axes
        top_pad.SetTickx(1)
        top_pad.SetTicky(1)
        top_pad.cd()
        first_graph = True
        for graph in graphs_from_a[canvas_name] + graphs_from_b[canvas_name]:
            y_axis_range = set_y_axis_range_theta(canvas_name) if canvas_style == "theta" else set_y_axis_range_momentum(canvas_name)
            graph.GetYaxis().SetRangeUser(y_axis_range[0],y_axis_range[1])
            draw_option = "APE" if first_graph else "PE same"
            graph.Draw(draw_option)
            first_graph = False
        top_pad.SetLogy()
        if canvas_style == "momentum": top_pad.SetLogx()

        combined_legend = ROOT.TLegend(0.65, 0.5, 0.9, 0.93)
        combined_legend.SetTextFont(62)
        combined_legend.SetTextSize(0.04)
        combined_legend.SetFillStyle(0)
        combined_legend.SetBorderSize(0)
        combined_legend.SetMargin(0.1)    # distance between marker and text
        combined_legend.SetHeader("Single #mu^{-}")

        # Example: Drawing the last legend from each list
        for legend in legends_from_graphs:
            for entry in legend.GetListOfPrimitives()[1:]:
                # Check if the entry is a TLegendEntry and not the title
                if isinstance(entry, ROOT.TLegendEntry):
                    # Add the entry to the new combined legend
                    combined_legend.AddEntry(entry.GetObject(), entry.GetLabel(), entry.GetOption())

        # Draw the accumulated legend after the loop
        top_pad.cd()
        combined_legend.Draw()
        top_pad.Update()

        bottom_pad = combined_canvas.cd(2)
        bottom_pad.SetPad(0, 0.0, 1, 0.3)
        bottom_pad.SetTopMargin(0.0)  # Set a top margin to visually separate pads
        bottom_pad.SetBottomMargin(0.5)  # Increase bottom margin for axis labels
        bottom_pad.SetLeftMargin(0.2)
        bottom_pad.SetRightMargin(0.02)
        if canvas_style == "momentum": bottom_pad.SetLogx()
        bottom_pad.Draw()
        bottom_pad.cd()
        first_graph = True
        for y_ratio in ratio_graphs[canvas_name]:
            draw_option = "APE" if first_graph else "PE same"
            y_ratio.Draw(draw_option)
            first_graph = False
        x_min = y_ratio.GetXaxis().GetXmin()
        x_max = y_ratio.GetXaxis().GetXmax()
        # Create a TLine at Y = 1 spanning the width of the x-axis range
        line = ROOT.TLine(x_min, 1, x_max, 1)
        line.SetLineColor(ROOT.kBlack)  # Set line color, e.g., red
        line.SetLineStyle(2)  # Set line style to dotted
        # Draw the line on the same pad as your ratio plot
        line.Draw("same")
        bottom_pad.Update()

        # Write the canvas to the output file
        output_root_file.cd()
        combined_canvas.Write()
        combined_canvas.Update()

        output_pdf_canvas.Clear()
        combined_canvas.Draw("APE" if combined_canvas.GetListOfPrimitives().GetSize() == 0 else "APEsame")
        combined_legend.Draw()
        output_pdf_canvas.Update()
        combined_canvas.Print(output_pdf_file, "pdf")

    output_pdf_canvas.Print(output_pdf_file + "]")
    output_root_file.Close()

#______________________________________________________________________________
# Define paths to the directories containing the ROOT files
folder_a = '/eos/user/g/gasadows/Output/TrackingPerformance/CLD_o2_v05/analysis/mu/plots/'
folder_b = '/eos/user/g/gasadows/Output/TrackingPerformance/CLD_o3_v01/analysis/plots/'
legend_txt =  [", CLD_o2_v5" , ", CLD_o3_v1"  ]

canvas_names = [
    "Canvas_delta_d0", "Canvas_delta_z0", "Canvas_delta_phi0", "Canvas_delta_omega",
    "Canvas_delta_tanLambda", "Canvas_delta_phi", "Canvas_delta_theta",
    "Canvas_sdelta_pt", "Canvas_sdelta_p"
]

# Theta
output_file_path = './ratio_theta.root'

file_names = ['t_dist_1.root', 't_dist_10.root', 't_dist_100.root']

process_and_compare_graphs(output_file_path, canvas_names, folder_a, folder_b, file_names, 'theta', legend_txt)

# Momentum
output_file_path = './ratio_momentum.root'

file_names = ['p_dist_10.root', 'p_dist_30.root', 'p_dist_50.root', 'p_dist_70.root', 'p_dist_89.root']

process_and_compare_graphs(output_file_path, canvas_names, folder_a, folder_b, file_names, 'momentum', legend_txt)
