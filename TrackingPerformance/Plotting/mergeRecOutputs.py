import os
import subprocess
import itertools
from concurrent.futures import ThreadPoolExecutor

def merge_files(theta, momentum, part, dect, eos_dir, Nevts_, Nevt_per_job):
    file_pattern = f"REC_{dect}_{part}_{theta}_deg_{momentum}_GeV_{Nevt_per_job}_evts_*_edm4hep.root"
    files_dir = os.path.join(eos_dir, part)
    files_to_merge = [os.path.join(files_dir, f) for f in os.listdir(files_dir) if f.endswith('_edm4hep.root') and f.startswith(file_pattern[:-18])]

    if not files_to_merge:
        print(f"No files found for pattern {file_pattern}. Skipping.")
        return

    output_dir = os.path.join(eos_dir, f"{part}/merged")
    os.makedirs(output_dir, exist_ok=True)
    merged_file = os.path.join(output_dir, f"Merged_REC_{dect}_{part}_{theta}_deg_{momentum}_GeV_{Nevts_}_evts_edm4hep.root")

    hadd_command = ["hadd", "-f", merged_file] + files_to_merge

    try:
        subprocess.run(hadd_command, check=True)
        print(f"Successfully merged files into {merged_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error during merging for {file_pattern}: {e}")

def main():

    print(f"Number of processors available: {os.cpu_count()}")
    
    # Parameters as per your script
    thetaList_ = ["89"]
    momentumList_ = ["1", "10", "100"]
    particleList_ = ["mu"]
    DetectorModelList_ = ["CLD_o2_v05"]

    Nevts_ = "10"  
    Nevt_per_job = "5"

    eos_dir = f"/eos/user/g/gasadows/Output/TrackingPerformance/{DetectorModelList_[0]}/REC/"

    list_of_combined_variables = itertools.product(thetaList_, momentumList_, particleList_, DetectorModelList_)

    with ThreadPoolExecutor() as executor:
        for variables in list_of_combined_variables:
            executor.submit(merge_files, *variables, eos_dir, Nevts_, Nevt_per_job)

if __name__ == "__main__":
    main()
