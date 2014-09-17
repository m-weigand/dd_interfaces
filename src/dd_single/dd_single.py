#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Debye decomposition interface for spectral induced polarisation data. One or
more spectra can be fitted using a Debye decomposition approach.

Copyright 2014 Maximilian Weigand

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
import json
import sys
import os
from optparse import OptionParser
import numpy as np
from multiprocessing import Pool
import tempfile
import shutil

import NDimInv
import NDimInv.version as VV
import NDimInv.regs as RegFuncs
import NDimInv.reg_pars as LamFuncs
from NDimInv.plot_helper import *
import NDimInv.lib_dd_interface as lDDi
import gc
import lib_dd.plot as lDDp


def add_base_options(parser):
    """Add options common to all dd_* programs to the parser
    """
    parser.add_option("-f", "--frequency_file", dest="frequency_file",
                      type='string', metavar="FILE", default='frequencies.dat',
                      help="Frequency file (default: frequency.dat)")
    parser.add_option("--ignore", help="Frequency id's to ignore, example:\
                      '12,13,14'. Starts with index 0.", type='string',
                      default=None, dest="ignore_frequencies")

    parser.add_option("-d", "--data_file", dest="data_file", type='string',
                      help="Extract file (default: data.dat)", metavar="FILE",
                      default='data.dat')
    parser.add_option('--data_format', dest='data_format', type='string',
                      help='Input data format, possible values are: ' +
                      'rmag_rpha, lnrmag_rpha, log10rmag_rpha, rmag_rpha, ' +
                      ' rre_rim rre_rmim, cmag_cpha, cre_cim, cre_cmim ' +
                      '(default: rmag_rpha). "r" stands for resistance/' +
                      'resistivity, and "c" stands for conductance/' +
                      'conductivity', default='rmag_rpha')
    parser.add_option("-n", "--nr_terms", dest="nr_terms_decade", type='int',
                      help="Number of Debye terms per frequency decade " +
                      "(default: 10)", metavar="INT", default=10)
    parser.add_option("-o", "--output", type='string', metavar='DIR',
                      help="Output directory", default=".", dest="output_dir")
    parser.add_option('-p', "--plot", action="store_true", dest="plot_spectra",
                      help="Plot final iterations (default: False)",
                      default=False)
    parser.add_option('-i', "--plot_its", action="store_true",
                      dest="plot_it_spectra", default=False,
                      help="Plot spectra of each iteration (default: False)")
    parser.add_option("--silent", action="store_true", dest="silent",
                      help="Do not plot any logs to STDOUT (default: False)",
                      default=False)
    parser.add_option("--tmp", action="store_true", dest="use_tmp",
                      help="Create the output in a temporary directory and " +
                      "later move it later to its destination (default: " +
                      "False)", default=False)

    parser.add_option("--tausel", type='string', metavar='STRATEGY',
                      help="Tau selection strategy:\ndata: Use " +
                      "data frequency limits for tau selection\ndata_ext " +
                      "(default): Extend tau ranges by one frequency decade " +
                      "compared to the 'data' strategy", default="data_ext",
                      dest="tausel")
    parser.add_option("--norm_mag", type='float', metavar='FLOAT',
                      help="Normalize magnitudes to the linear " +
                      "resistivity/resistance value (default: None)",
                      default=None, dest="norm_mag")
    parser.add_option("--plot_lcurve", type='int', metavar='ITERATION',
                      help="Plot the l-curve for a selected iteration. " +
                      "WARNING: This only plots the lcurve and does not " +
                      "use it in the inversion process. Use -1 for last " +
                      "iteration. default=None ",
                      default=None, dest="plot_lambda")
    parser.add_option("--max_it", type='int', metavar='INT',
                      help="Maximum nr of iterations (default: 20)",
                      default=20, dest="max_iterations")
    parser.add_option('-v', "--version", action="store_true",
                      dest="version", default=False,
                      help="Print version information")

    return parser


def handle_cmd_options():
    """
    Handle command line options
    """
    parser = OptionParser()
    parser = add_base_options(parser)
    # add options specific to dd_single
    parser.add_option("-c", "--nr_cores", dest="nr_cores", type='int',
                      help="Number of CPU cores to use (default: 2)",
                      metavar="INT", default=2)
    parser.add_option("--lambda", type='float', metavar='FLOAT',
                      help="Use a fixed lambda (integer), default=None",
                      default=None, dest="fixed_lambda")
    (options, args) = parser.parse_args()

    # print version information if requested
    if(options.version):
        print(VV.version)
        exit()
    return options


def split_options_base(options):
    """
    Prepare dicts containing preparation and inversion settings common to all
    dd_* programs
    """
    prep_opts = {}
    prep_opts['plot_it_spectra'] = options.plot_it_spectra
    prep_opts['plot'] = options.plot_spectra
    prep_opts['output_dir'] = options.output_dir
    prep_opts['data_format'] = options.data_format
    prep_opts['plot_lambda'] = options.plot_lambda

    inv_opts = {}
    inv_opts['tausel'] = options.tausel
    inv_opts['Nd'] = options.nr_terms_decade
    inv_opts['max_iterations'] = options.max_iterations

    return prep_opts, inv_opts


def split_options_single(options):
    """
    Extract options for two groups:
    1) prep_opts : these options are used to prepare the actual inversion, i.e.
                   which regularization objects to use
    2) inv_opts : these options are directly passed through to the NDimInv
                  object
    """
    prep_opts, inv_opts = split_options_base(options)

    # now add options specific to dd_single
    prep_opts['lambda'] = options.fixed_lambda
    prep_opts['nr_cores'] = options.nr_cores

    return prep_opts, inv_opts


def _prepare_ND_object(fit_data):
    ND = NDimInv.Inversion('dd_log10rho0log10m', fit_data['inv_opts'])
    ND.finalize_dimensions()

    # Read in data
    ND.Data.add_data(fit_data['data'], fit_data['prep_opts']['data_format'],
                     extra=[])

    # now that we know the frequencies we can call the post_frequency handler
    # for the model side
    ND.update_model()

    ND.set_custom_plot_func(lDDp.plot_iteration())

    # here you can change the rms value we optimize for
    # rms_part2_no_err yields good results
    # optimize_for = 'rms_both_no_err'
    # optimize_for = 'rms_part1_no_err'
    # optimize_for = 'rms_part1_err'
    optimize_for = 'rms_part2_no_err'
    # optimize_for = 'rms_part2_err'

    # add a frequency regularization for the DD model
    if(fit_data['prep_opts']['lambda'] is None):
        lam_obj = LamFuncs.SearchLambda(LamFuncs.Lam0_Easylam())
        lam_obj.rms_key = optimize_for
    else:
        lam_obj = LamFuncs.FixedLambda(fit_data['prep_opts']['lambda'])

    ND.Model.add_regularization(0,
                                RegFuncs.SmoothingFirstOrder(
                                    decouple=[0, ]),
                                lam_obj
                                )

    # if we use an extended tau range, we want to minimize the m-values in
    # those extra ranges
    # if(fit_data['inv_opts']['tausel'] == 'data_ext'):
    #    print('Extra taus')
    #   # we only want to regularize the extra values, i.e. Nd values on the
    #   # left and to the right
    #   Nd = fit_data['inv_opts']['Nd']
    #   nr_taus = len(ND.Data.obj.tau)
    #   # note: +1 for rho0
    #   # lower tau range
    #   decouple = range(Nd + 1, nr_taus - Nd + 2)
    #   decouple = range(Nd + 1, nr_taus + 1)

    #   ND.Model.add_regularization(0,
    #                               RegFuncs.Damping(
    #                                   decouple=decouple),
    #                          #LamFuncs.SearchLambda(LamFuncs.Lam0_Easylam())
    #                               LamFuncs.FixedLambda(1e5)
    #                               )

    # choose from a fixed set of step lengths
    ND.Model.steplength_selector = NDimInv.main.SearchSteplengthParFit(
        optimize_for)
    return ND


# @profile
def fit_one_spectrum(fit_data):
    """
    Fit one spectrum
    """
    print('Fitting spectrum {0} of {1}'.format(fit_data['nr'],
                                               fit_data['nr_of_spectra']))
    ND = _prepare_ND_object(fit_data)

    # run the inversion
    ND.run_inversion()

    final_iteration = ND.iterations[-1]

    # renormalize data (we deal only with one spectrum here)
    if(fit_data['inv_opts']['norm_factors'] is not None):
        norm_fac = fit_data['inv_opts']['norm_factors']
        # add normalization factor to the parameters
        final_iteration.m[0] -= np.log10(norm_fac)
        final_iteration.f = final_iteration.Model.f(final_iteration.m)
        # data
        # note: the normalization factor can be applied either to the
        # magnitude, or to both real and imaginary parts!
        final_iteration.Data.D /= norm_fac

    if(fit_data['prep_opts']['plot']):
        print('Plotting final iteration')
        ND.iterations[-1].plot()
        ND.iterations[-1].plot_reg_strengths()

    if(fit_data['prep_opts']['plot_it_spectra']):
        for it in ND.iterations:
            it.plot()

    if(fit_data['prep_opts']['plot_lambda'] is not None):
        ND.iterations[fit_data['prep_opts']['plot_lambda']].plot_lcurve()

    # invoce the garbage collection just to be sure
    gc.collect()
    return ND


def _filter_nan_values(frequencies, cr_spectrum):
    """
        Filter nan values along the frequency axis (we always ne part1 and
        part2).

        Return filtered frequencies, cr_spectrum
    """

    # check for NaN values
    nan_indices = np.isnan(cr_spectrum)
    nan_along_freq = np.any(nan_indices, axis=1)
    to_delete = np.where(nan_along_freq)
    frequencies_cropped = np.delete(frequencies, to_delete)
    cr_spectrum_cropped = np.delete(cr_spectrum, to_delete, axis=0)
    return frequencies_cropped, cr_spectrum_cropped


def _get_fit_datas(data, prep_opts, inv_opts):
    """
    Prepare data for fitting. Prepare a set of variables/objects for each
    spectrum. Also filter nan values

    Parameters
    ----------
    data : dict containing the keys 'frequencies', 'cr_data'
    prep_opts
    inv_opts
    """
    fit_datas = []

    # add frequencies to inv_opts
    # opts['max_iterations'] = 20
    # opts['frequencies'] = frequencies  # why do we need this

    nr_of_spectra = len(data['cr_data'])
    for i in range(0, nr_of_spectra):
        fit_data = {}
        # change file prefix for each spectrum
        # at the moment we need a copy for this
        frequencies_cropped, cr_data = _filter_nan_values(
            data['frequencies'], data['cr_data'][i])

        fit_data['prep_opts'] = prep_opts
        fit_data['data'] = cr_data
        fit_data['nr'] = i + 1
        fit_data['nr_of_spectra'] = nr_of_spectra
        fit_data['frequencies'] = frequencies_cropped

        inv_opts_i = inv_opts.copy()
        inv_opts_i['frequencies'] = frequencies_cropped
        inv_opts_i['global_prefix'] = 'spec_{0:03}_'.format(i)
        if('norm_factors' in data):
            inv_opts_i['norm_factors'] = data['norm_factors'][i]
        else:
            inv_opts_i['norm_factors'] = None

        fit_data['inv_opts'] = inv_opts_i

        fit_datas.append(fit_data)

    return fit_datas


def fit_data(data, prep_opts, inv_opts):
    """

    """
    fit_datas = _get_fit_datas(data, prep_opts, inv_opts)

    # before the inversion is started, save the dict
    # note: we should save inv_opts_i
    # delete frequencies and data
    # del(opts['frequencies'])
    with open('inversion_options.json', 'w') as fid:
        json.dump(inv_opts, fid)

    # fit
    if(prep_opts['nr_cores'] == 1):
        print('single processing')
        # single processing
        results = map(fit_one_spectrum, fit_datas)
    else:
        # multi processing
        print('multi processing')
        p = Pool(prep_opts['nr_cores'])
        results = p.map(fit_one_spectrum, fit_datas)

    final_iterations = [(x.iterations[-1], nr) for nr, x in enumerate(results)]
    save_fit_results(final_iterations, data)

    # plot some stats
    if(prep_opts['plot']):
        for it, nr in final_iterations:
            it.Model.obj.plot_stats('{0}'.format(nr))


def save_base_results(final_iterations, data):
    """
    Save data files that are shared between
    dd_single.py/dd_time.py/dd_space_time.py
    """
    with open('version.dat', 'w') as fid:
        fid.write(VV.version + '\n')

    with open('data_format.dat', 'w') as fid:
        fid.write(final_iterations[0][0].Data.obj.data_format + '\n')

    # save call to debye_decomposition.py
    with open('command.dat', 'w') as fid:
        fid.write(' '.join(sys.argv) + '\n')

    # save tau/s
    np.savetxt('tau.dat', final_iterations[0][0].Data.obj.tau)
    np.savetxt('s.dat', final_iterations[0][0].Data.obj.s)

    # save frequencies/omega
    np.savetxt('frequencies.dat', final_iterations[0][0].Data.obj.frequencies)
    np.savetxt('omega.dat', final_iterations[0][0].Data.obj.omega)

    # save weighting factors
    Wd_diag = final_iterations[0][0].Data.Wd.diagonal()
    np.savetxt('errors.dat', Wd_diag)

    # save lambdas
    # TODO: We want all lambdas, not only from the last iteration
    try:
        lambdas = [x[0].lams for x in final_iterations]
        np.savetxt('lambdas.dat', lambdas)
    except Exception, e:
        print('There was an error saving the lambda values')
        print(e)
        pass

    # save number of iterations
    nr_of_iterations = [x[0].nr for x in final_iterations]
    np.savetxt('nr_iterations.dat', nr_of_iterations, fmt='%i')

    # save normalization factors
    if('norm_factors' in data):
        np.savetxt('rho_normalizations.dat', data['norm_factors'])


def save_fit_results(final_iterations, data):
    """
    Save results of all DD fits to files
    """
    save_base_results(final_iterations, data)
    if(not os.path.isdir('stats_and_rms')):
        os.makedirs('stats_and_rms')
    os.chdir('stats_and_rms')
    stats_for_all_its = lDDi.aggregate_dicts(final_iterations, 'stat_pars')
    if('norm_factors' in data):
        norm_factors = data['norm_factors']
    else:
        norm_factors = None
    lDDi.save_stat_pars(stats_for_all_its, norm_factors)

    rms_for_all_its = lDDi.aggregate_dicts(final_iterations, 'rms_values')
    lDDi.save_rms_values(rms_for_all_its)
    os.chdir('..')

    # save data
    with open('data.dat', 'w') as fid:
        for nr, itd in enumerate(final_iterations):
            data = itd[0].Data.Df.flatten()[np.newaxis, :]
            # if necessary, apply renormalization
            if(norm_factors is not None):
                data[0:data.size/2] /= norm_factors[nr]

            np.savetxt(fid, data)

    # save model response
    with open('f.dat', 'w') as fid:
        for itd in final_iterations:
            np.savetxt(fid,
                       itd[0].Model.f(itd[0].m)[np.newaxis, :])


def get_data_dd_single(options):
    """
    Load frequencies and data and return a data dict

    options is also returned in case we change some settings, e.g. the data
    format
    """
    data = lDDi.load_frequencies_and_data(options)

    # we need list of spectra
    size_y = data['raw_data'].shape[1] / 2
    cr_data = [x.reshape((size_y, 2), order='F') for x in data['raw_data']]

    data['cr_data'] = cr_data
    return data, options


def get_output_dir(options):
    if(options.use_tmp):
        # get temporary directory
        tmp_outdir = tempfile.mkdtemp(suffix='dd_')
        outdir = tmp_outdir
    else:
        if(not os.path.isdir(options.output_dir)):
            os.makedirs(options.output_dir)
        outdir = options.output_dir
    return outdir


# @profile
def main():
    print('Debye Decomposition')
    options = handle_cmd_options()
    outdir = get_output_dir(options)

    # DD_RES_INV.inversion.setup_logger('dd', outdir, options.silent)
    # logger = logging.getLogger('dd.debye decomposition')

    # logger.info('----------------------------------')
    # logger.info('       Debye Decomposition')
    # logger.info('----------------------------------')
    # logger.info('Frequency file: {0}'.format(options.frequency_file))
    # logger.info('Data file: {0}'.format(options.data_file))
    # frequencies, data_list = get_frequencies_and_data(options)
    data, options = get_data_dd_single(options)

    # we distinguish two sets of options:
    # prep_opts : all settings we need to prepare the inversion (i.e. set
    #             regularization objects)
    # inv_opts : options that are directly looped through to the NDimInv object
    prep_opts, inv_opts = split_options_single(options)

    # for the fitting process, change to the output_directory
    pwd = os.getcwd()
    os.chdir(outdir)

    fit_data(data, prep_opts, inv_opts)

    # logger.info('=======================================')
    # logger.info('     Debye Decomposition finished!     ')
    # logger.info('=======================================')

    # go back to initial working directory
    os.chdir(pwd)

    # move temp directory to output directory
    if(options.use_tmp):
        shutil.move(outdir, options.output_dir)


if __name__ == '__main__':
    main()
