#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=unused-wildcard-import,wildcard-import
"""
Cole-Cole decomposition interface for spectral induced polarization data. One
or more spectra can be fitted using a Debye decomposition approach.

Copyright 2014,2015,2016 Maximilian Weigand

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
# from memory_profiler import *
import logging
logging.basicConfig(level=logging.INFO)
import os
import shutil
from NDimInv.plot_helper import *
import lib_dd.io.io_general as iog
import lib_dd.config.cfg_single as cfg_single
import lib_dd.interface as lDDi
# import lib_dd.plot as lDDp
from lib_dd.decomposition.ccd_single import ccd_single


# @profile
def main():
    print('Cole-Cole decomposition, no time regularization')

    options = cfg_single.cfg_single()
    options.parse_cmd_arguments()
    options.check_input_files()

    outdir_real, options = lDDi.create_output_dir(options)

    ccds_object = ccd_single(options)
    # ccds_object.fit_data()

    # DD_RES_INV.inversion.setup_logger('dd', outdir, options.silent)
    # logger = logging.getLogger('dd.debye decomposition')

    # fit the data
    ccds_object.fit_data()

    # for the fitting process, change to the output_directory
    pwd = os.getcwd()
    os.chdir(options['output_dir'])

    iog.save_fit_results(
        ccds_object.data,
        ccds_object.results
    )

    # go back to initial working directory
    os.chdir(pwd)

    # move temp directory to output directory
    if options['use_tmp']:
        if os.path.isdir(outdir_real):
            print('WARNING: Output directory already exists')
            print('The new inversion can be found here:')
            print((options['output_dir'] + os.sep + os.path.basename(outdir)))
        shutil.move(options['output_dir'], outdir_real)

    # logger.info('=======================================')
    # logger.info('     Debye Decomposition finished!     ')
    # logger.info('=======================================')


if __name__ == '__main__':
    main()
