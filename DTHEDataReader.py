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


from cil.framework import AcquisitionData, AcquisitionGeometry, ImageData, ImageGeometry, DataOrder
# import numpy as np
import os
from pathlib import Path
from xml.etree import ElementTree
from tifffile import imread

# import olefile
# import logging
# dxchange_logger = logging.getLogger('dxchange')
# dxchange_logger.setLevel(logging.ERROR)

# import dxchange
# import warnings

# logger = logging.getLogger(__name__)

class DTHEDataReader(object):

    '''
    Create a reader for DTHE files
    
    Parameters
    ----------
    file_name: str
        file name to read
    '''
    
    def __init__(self, file_name: str=None):

        # Initialise class attributes to None
        self.file_name = None
        self._geometry = None

        # # Set logging level for dxchange reader.py
        # logger_dxchange = logging.getLogger(name='dxchange.reader')
        # if logger_dxchange is not None:
        #     logger_dxchange.setLevel(logging.ERROR)

        if file_name is not None:
            self.set_up(file_name)


    def set_up(self, file_name: str):
        '''Set up the reader
        
        Parameters
        ----------
        file_name: str
            file name to read
        '''

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
        projection_path = directory_path / "Proj"
        if not os.path.isdir(projection_path):
            raise ValueError(f"The projection directory '{projection_path}' does not exist")

        # Save the file name
        self.file_name = file_name

        # Open the file
        tree = ElementTree.parse(file_name)

        # Find the conebeam profile
        profile = tree.find("conebeam/profile")
        assert profile is not None

        # Get the number of projections
        number_of_projections = int(profile.attrib["images"])

        # Look for the name of projection images
        image_file_names = [image for image in projection_path.rglob("*.tif")]
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

        # Known values from the manufacturer
        pixel_size_in_um = 150
        pixel_size_in_mm = pixel_size_in_um * 0.001




        # Create the acquisition geometry
        self._geometry = AcquisitionGeometry.create_Cone3D(
            source_position=[-source_to_object,0 , 0], 
            detector_direction_x=[0, -1,  0],
            detector_direction_y=[0,  0, -1],
            detector_position=[object_to_detector, 0, 0], 
            rotation_axis_position=[0, 0, 0])

        # Set the angles of rotation
        self._geometry.set_angles(np.linspace(0, 360, number_of_projections))

        self._geometry.set_panel(detector_number_of_pixels, pixel_spacing_mm)
        self._geometry.set_labels(['angle','vertical','horizontal'])

        # Panel is height x width
        self._geometry.set_panel(projections_shape[1:][::-1], pixel_size_in_mm)


    def get_geometry(self):
        '''
        Return the acquisition geometry object
        '''
        return self._geometry
    