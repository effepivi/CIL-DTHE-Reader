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
print("Data read execution time:", "{0:0.2f}".format((stop - start) / 60.0), "minutes")

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
print("minus log execution time:", "{0:0.2f}".format((stop - start) / 60.0), "minutes")

backend = args.backend.lower()
start = time.time()
if backend == "cil":
    print("Filter: CIL")
    print("Projector: Tigre")
    # Prepare the data for Tigre
    data.reorder(order='tigre')

    # Reconstruct using FDK
    ig = data.geometry.get_ImageGeometry()
    reconstruction_algorithm =  FDK(data, ig)
    reconstruction_algorithm.set_filter_inplace(True)
    recon = reconstruction_algorithm.run()
elif backend == "tigre":
    print("Filter: Tigre")
    print("Projector: Tigre")
    # Prepare the data for Astra-toolbox
    data.reorder(order='tigre')

    # Reconstruct using FDK
    ig = data.geometry.get_ImageGeometry()
    reconstruction_algorithm =  FBP_tigre(ig, data.geometry)
    recon = reconstruction_algorithm(data)
elif backend == "astra":
    print("Filter: Astra-toolbox")
    print("Projector: Astra-toolbox")
    # Prepare the data for Astra-toolbox
    data.reorder(order='astra')

    # Reconstruct using FDK
    ig = data.geometry.get_ImageGeometry()
    reconstruction_algorithm =  FBP_astra(ig, data.geometry)
    recon = reconstruction_algorithm(data)
else:
    raise ValueError(backend + " is invalid. Expected values are \"cil\" \"tigre\" or \"astra\".")
stop = time.time()
print("Reconstuction execution time:", "{0:0.2f}".format((stop - start) / 60.0), "minutes")

# Save the CT volume as a stack of TIFF files
if not os.path.isdir(args.dest):
    os.makedirs(args.dest)

print("A stack of TIFF files will be saved in the directory as follows:", args.dest)
TIFFWriter(data=recon, file_name=os.path.join(args.dest, "slice")).write()
