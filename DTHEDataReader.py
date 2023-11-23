# -*- coding: utf-8 -*-
#  Copyright 2023 United Kingdom Research and Innovation
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
# Authors:
# CIL Developers, listed at: https://github.com/TomographicImaging/CIL/blob/master/NOTICE.txt
# Franck P. Vidal (Science and Technology Facilities Council)


from cil.framework import AcquisitionGeometry #, AcquisitionData, ImageData, ImageGeometry, DataOrder
from cil.io.TIFF import TIFFStackReader

import numpy as np
import os
from pathlib import Path
from xml.etree import ElementTree
from tifffile import imread

class DTHEDataReader(object):

    '''
    Create a reader for DTHE files
    
    Parameters
    ----------
    file_name: str
        file name to read

    normalise: bool, default=True
        normalises loaded projections by detector white level (I_0)

    mode: str: {'bin', 'slice'}, default='bin'
        In bin mode, 'step' number of pixels is binned together,
        values of resulting binned pixels are calculated as average. 
        In 'slice' mode 'step' defines standard numpy slicing.
        Note: in general output array size in bin mode != output array size in slice mode

    fliplr: bool, default = False,
        flip projections in the left-right direction (about vertical axis)

    Notes
    -----
    `roi` behaviour:
        Files are stacked along axis_0. axis_1 and axis_2 correspond
        to row and column dimensions, respectively.
        
        Files are stacked in alphabetic order. 
        
        To skip projections or to change number of projections to load, 
        adjust 'angle'. For instance, 'angle': (100, 300)
        will skip first 100 projections and will load 200 projections.
        
        ``'angle': -1`` is a shortcut to load all elements along axis.
            
        ``start`` and ``end`` can be specified as ``None`` which is equivalent
        to ``start = 0`` and ``end = load everything to the end``, respectively.
        Start and end also can be negative.
    '''
    
    def __init__(self,
                 file_name: str=None,
                 normalise: bool=True,
                 mode: str="bin",
                 fliplr: bool=False):

        # Initialise class attributes to None
        self.file_name = None
        self.normalise = normalise
        self.mode = mode
        self.fliplr = fliplr
        self._ag = None # The acquisition geometry object
        self.tiff_directory_path = None

        # The file name is set
        if file_name is not None:

            # Initialise the instance
            self.set_up(file_name=file_name,
                normalise=normalise,
                fliplr=fliplr)


    def set_up(self,
               file_name: str=None,
               normalise: bool=True,
               mode: str="bin",
               fliplr: bool=False):

        '''Set up the reader
        
        Parameters
        ----------
        file_name: str
            file name to read

        normalise: bool, default=True
            normalises loaded projections by detector white level (I_0)

        mode: str: {'bin', 'slice'}, default='bin'
            In bin mode, 'step' number of pixels is binned together,
            values of resulting binned pixels are calculated as average. 
            In 'slice' mode 'step' defines standard numpy slicing.
            Note: in general output array size in bin mode != output array size in slice mode

        fliplr: bool, default = False,
            flip projections in the left-right direction (about vertical axis)
        '''

        # Save the attributes
        self.file_name = file_name
        # self.roi = roi
        self.normalise = normalise
        self.mode = mode
        self.fliplr = fliplr

        # Check a file name was provided
        if file_name is None:
            raise ValueError('Path to unireconstruction.xml file is required.')

        # Check if the file exists
        file_name = os.path.abspath(file_name)
        if not(os.path.isfile(file_name)):
            raise FileNotFoundError('{}'.format(file_name))

        # Check the file name without the path
        file_type = os.path.basename(file_name).lower()
        if file_type != "unireconstruction.xml":
            raise TypeError('This reader can only process \"unireconstruction.xml\" files. Got {}'.format(file_type))

        # Get the directory path
        directory_path = Path(os.path.dirname(file_name))

        # Look for projections
        self.tiff_directory_path = directory_path / "Proj"
        if not os.path.isdir(self.tiff_directory_path):
            raise ValueError(f"The projection directory '{self.tiff_directory_path}' does not exist")

        # Open the XML file
        tree = ElementTree.parse(file_name)

        # Find the conebeam profile
        profile = tree.find("conebeam/profile")
        assert profile is not None

        # Get the number of projections
        number_of_projections = int(profile.attrib["images"])

        # Look for the name of projection images
        image_file_names = [image for image in self.tiff_directory_path.rglob("*.tif")]
        assert (len(image_file_names) == number_of_projections)

        # Find the acquisition information
        acquisition_info = tree.find("conebeam/acquisitioninfo")
        assert acquisition_info is not None

        # Find the acquisition geometry
        conf_geo = acquisition_info.find("geometry")
        assert conf_geo is not None

        # Get the SDD and SOD
        source_to_detector = float(conf_geo.attrib["sdd"])
        source_to_object = float(conf_geo.attrib["sod"])
        object_to_detector = source_to_detector - source_to_object

        # Known values from the manufacturer
        pixel_size_in_um = 150
        pixel_size_in_mm = pixel_size_in_um * 0.001

        # Create the acquisition geometry
        self._ag = AcquisitionGeometry.create_Cone3D(
            source_position=[0, -source_to_object, 0], 
            detector_direction_x=[1, 0,  0],
            detector_direction_y=[0, 0, 1],
            detector_position=[0, object_to_detector, 0], 
            rotation_axis_position=[0, 0, 0])

        # Set the angles of rotation
        self._ag.set_angles(-np.linspace(0, 360, number_of_projections))

        # Read the first projection to extract its size in nmber of pixels
        first_projection_data = imread(image_file_names[0])
        projections_shape = (number_of_projections, *first_projection_data.shape)
        
        # self._ag.set_panel(detector_number_of_pixels, pixel_spacing_mm)
        self._ag.set_labels(['angle','vertical','horizontal'])

        # Panel is width x height
        self._ag.set_panel(first_projection_data.shape[::-1], pixel_size_in_mm)


    def read(self):
        
        '''
        Reads projections and returns AcquisitionData with corresponding geometry,
        arranged as ['angle', horizontal'] if a single slice is loaded
        and ['vertical, 'angle', horizontal'] if more than 1 slice is loaded.
        '''

        # Check a file name was provided
        if self.tiff_directory_path is None:
            raise ValueError('The reader was not set properly.')

        # Create the TIFF reader
        reader = TIFFStackReader()

        reader.set_up(file_name=self.tiff_directory_path,
                    #   roi=roi,
                      mode=self.mode)

        ad = reader.read_as_AcquisitionData(self._ag)
              
        if (self.normalise):
            white_level = np.max(ad.array)
            ad.array[ad.array < 1] = 1

            # cast the data read to float32
            ad = ad / np.float32(white_level)
            
        
        if self.fliplr:
            dim = ad.get_dimension_axis('horizontal')
            ad.array = np.flip(ad.array, dim)
        
        return ad

    def load_projections(self):
        '''alias of read for backward compatibility'''
        return self.read()


    def get_geometry(self):
        
        '''
        Return AcquisitionGeometry object
        '''
        
        return self._ag

    def get_geometry(self):
        '''
        Return the acquisition geometry object
        '''
        return self._ag
