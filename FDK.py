#!/usr/bin/env python3

# import sys
import argparse

from cil.processors import TransmissionAbsorptionConverter
from cil.utilities.display import show_geometry
from cil.io import TIFFWriter
from cil.recon import FDK

from DTHEDataReader import *


parser = argparse.ArgumentParser(description="Just an example",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("src",  type=str, help="Source location")
parser.add_argument("dest", type=str, help="Destination location")
parser.add_argument("-dg", "--display_geometry", action="store_true", help="Display the geometry using a Matplotlib figure")
parser.add_argument("-pg", "--print_geometry", action="store_true", help="Print the geometry in the terminal")
args = parser.parse_args()

# Create the reader
reader = DTHEDataReader(args.src)

# Load the data
data = reader.read()

# Display the geometry using a Matplotlib figure
if args.display_geometry:
    show_geometry(data.geometry)

# Print the geometry in the terminal
if args.print_geometry:
    print(data.geometry)

# Apply the minus log 
data = TransmissionAbsorptionConverter()(data)

# Prepare the data for Tigre
data.reorder(order='tigre')

# Reconstruct using FDK
ig = data.geometry.get_ImageGeometry()
reconstruction_algorithm =  FDK(data, ig)
recon = reconstruction_algorithm.run()

# Save the CT volume as a stack of TIFF files
if not os.path.isdir(args.dest):
    os.makedirs(args.dest)

print("A stack of TIFF files will be saved in the directory as follows:", args.dest)
TIFFWriter(data=recon, file_name=os.path.join(args.dest, "slice")).write()
