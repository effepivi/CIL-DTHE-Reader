#!/usr/bin/env python3

import sys
import argparse
# import matplotlib
import time

from cil.processors import TransmissionAbsorptionConverter
from cil.utilities.display import show_geometry
from cil.io import TIFFWriter
from cil.recon import FDK
from cil.plugins.astra import FBP as FBP_astra
from cil.plugins.tigre import FBP as FBP_tigre

from DTHEDataReader import *

def reconstruct(data_corr, FDK_filter, back_projector, set_filter_inplace=True, roi_size=None):
    
    # Check that `FDK_filter` is a valid option
    if FDK_filter.lower() != "cil" and FDK_filter.lower() != "tigre" and FDK_filter.lower() != "astra":
        raise ValueError(FDK_filter + " is not a valid filter implementation. Valid options are :\"cil\" (prefered), \"tigre\" and \"astra\".")

    # Check that `back_projector` is a valid option
    if back_projector.lower() != "tigre" and back_projector.lower() != "astra":
        raise ValueError(back_projector + " is not a valid projector implementation. Valid options are: \"tigre\" (prefered) and \"astra\".")
    
    # Chek the combination of options is a valid combination
    if FDK_filter.lower() == "astra" and back_projector.lower() != "astra":
        raise ValueError("With the astra filter implementation, you must use the astra projector.")
        
    if FDK_filter.lower() == "cil" and back_projector.lower() != "tigre":
        raise ValueError("With the cil filter implementation, you must use the tigre projector.")
        
    if FDK_filter.lower() == "tigre" and back_projector.lower() != "tigre":
        raise ValueError("With the tigre filter implementation, you must use the tigre projector.")
        
    # Reconstruction
    if FDK_filter.lower() == "cil" and back_projector.lower() == "tigre":
        print("Filter: CIL")
        print("Projector: Tigre")
        # Prepare the data for Tigre
        data_corr.reorder(order='tigre')

        # Reconstruct using FDK
        ig = data_corr.geometry.get_ImageGeometry()

        if roi_size is not None:
            ig.voxel_num_x = roi_size[0]
            ig.voxel_num_y = roi_size[1]
            ig.voxel_num_z = roi_size[2]

        reconstruction_algorithm =  FDK(data_corr, ig)
        reconstruction_algorithm.set_filter_inplace(set_filter_inplace)
        recon = reconstruction_algorithm.run()
        

    elif FDK_filter.lower() == "tigre" and back_projector.lower() == "tigre":
        print("Filter: Tigre")
        print("Projector: Tigre")
        # Prepare the data for Astra-toolbox
        data_corr.reorder(order='tigre')

        # Reconstruct using FDK
        ig = data_corr.geometry.get_ImageGeometry()
        
        if roi_size is not None:
            ig.voxel_num_x = roi_size[0]
            ig.voxel_num_y = roi_size[1]
            ig.voxel_num_z = roi_size[2]
            
        reconstruction_algorithm =  FBP_tigre(ig, data_corr.geometry)
        recon = reconstruction_algorithm(data_corr)

    elif FDK_filter.lower() == "astra" and back_projector.lower() == "astra":
        print("Filter: Astra-toolbox")
        print("Projector: Astra-toolbox")
        # Prepare the data for Astra-toolbox
        data_corr.reorder(order='astra')

        # Reconstruct using FDK
        ig = data_corr.geometry.get_ImageGeometry()

        if roi_size is not None:
            ig.voxel_num_x = roi_size[0]
            ig.voxel_num_y = roi_size[1]
            ig.voxel_num_z = roi_size[2]

        reconstruction_algorithm =  FBP_astra(ig, data_corr.geometry)
        recon = reconstruction_algorithm(data_corr)
    else:
        raise ValueError("You should never have reached that line of code, please contact the module maintainer.")

    return recon

def getRuntime(start, stop):
    duration_in_sec = stop - start
    
    if duration_in_sec < 60:
        if duration_in_sec <= 1:
            units_of_time = "second"
        else:
            units_of_time = "seconds"
        
        return duration_in_sec, units_of_time
    else:
        duration_in_min = duration_in_sec / 60

        if duration_in_min < 60:
            if duration_in_min <= 1:
                units_of_time = "minute"
            else:
                units_of_time = "minutes"

            return duration_in_min, units_of_time
        else:
            duration_in_h = duration_in_min / 60

            if duration_in_h < 60:
                if duration_in_h <= 1:
                    units_of_time = "hour"
                else:
                    units_of_time = "hours"

                return duration_in_h, units_of_time

def main():
    parser = argparse.ArgumentParser(description="Just an example",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("src",  type=str, help="Source location")
    parser.add_argument("dest", type=str, help="Destination location")
    parser.add_argument("-dg", "--display_geometry", action="store_true", help="Display the geometry using a Matplotlib figure")
    parser.add_argument("-pg", "--print_geometry", action="store_true", help="Print the geometry in the terminal")
    parser.add_argument("--save_geometry", type=str, help="Path of the file name where the plot of the geometry will be saved")
    parser.add_argument("-b", "--backend", type=str, default="CIL", help="The backend to use, either CIL, tigre or astra")
    args = parser.parse_args()
    print(args)

    # Create the reader
    start = time.time()
    reader = DTHEDataReader(args.src)

    # Load the data
    data = reader.read()
    stop = time.time()
    runtime, unit = getRuntime(start, stop)
    print("Data read execution time:", "{0:0.2f}".format(runtime), unit)

    # Display the geometry using a Matplotlib figure
    if args.display_geometry and args.save_geometry is None:
        show_geometry(data.geometry)

    # Display the geometry using a Matplotlib figure and save it into a file
    if args.save_geometry is not None and not args.display_geometry:
        # matplotlib.use('Agg')
        show_geometry(data.geometry).save(args.save_geometry)

    # Print the geometry in the terminal
    if args.print_geometry:
        print(data.geometry)

    # Apply the minus log 
    start = time.time()
    data = TransmissionAbsorptionConverter()(data)
    stop = time.time()
    runtime, unit = getRuntime(start, stop)
    print("minus log execution time:", "{0:0.2f}".format(runtime), unit)

    backend = args.backend.lower()
    start = time.time()
    if backend == "cil":
        recon = reconstruct(data, "cil", "tigre")
    elif backend == "tigre":
        recon = reconstruct(data, "tigre", "tigre")
    elif backend == "astra":
        recon = reconstruct(data, "astra", "astra")
    else:
        raise ValueError(backend + " is invalid. Expected values are \"cil\" \"tigre\" or \"astra\".")
    stop = time.time()
    runtime, unit = getRuntime(start, stop)
    print("Reconstuction execution time:", "{0:0.2f}".format(runtime), unit)

    # Save the CT volume as a stack of TIFF files
    if not os.path.isdir(args.dest):
        os.makedirs(args.dest)

    print("A stack of TIFF files will be saved in the directory as follows:", args.dest)
    TIFFWriter(data=recon, file_name=os.path.join(args.dest, "slice")).write()

if __name__ == '__main__':
    main()    