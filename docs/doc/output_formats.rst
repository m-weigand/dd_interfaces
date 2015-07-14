Output Files
^^^^^^^^^^^^

ascii_audit format
""""""""""""""""""

A typical result directory in this format contains the following files ::

    results/
    ├── covf.dat
    ├── covm.dat
    ├── data.dat
    ├── errors.dat
    ├── f.dat
    ├── frequencies.dat
    ├── integrated_paramaters.dat
    ├── inversion_options.json
    ├── lams_and_nr_its.dat
    ├── m_i.dat
    ├── normalization_factors.dat
    ├── rms_definition.json
    ├── tau.dat
    └── version.dat

    0 directories, 14 files

ascii format
""""""""""""

A typical result directory in this format contains the following files ::

    results/
    ├── command.dat
    ├── data.dat
    ├── data_format.dat
    ├── errors.dat
    ├── f.dat
    ├── f_format.dat
    ├── frequencies.dat
    ├── inversion_options.json
    ├── lambdas.dat
    ├── normalization_factors.dat
    ├── nr_iterations.dat
    ├── omega.dat
    ├── rms_definition.json
    ├── s.dat
    ├── stats_and_rms
    │   ├── covf_results.dat
    │   ├── covm_results.dat
    │   ├── decade_bins_results.dat
    │   ├── decade_loadings_results.dat
    │   ├── f_50_results.dat
    │   ├── f_arithmetic_results.dat
    │   ├── f_geometric_results.dat
    │   ├── f_max_results.dat
    │   ├── f_mean_results.dat
    │   ├── f_peak1_results.dat
    │   ├── f_peak2_results.dat
    │   ├── f_peaks_all_results.dat
    │   ├── m_data_results.dat
    │   ├── m_i_results.dat
    │   ├── m_tot_n_results.dat
    │   ├── m_tot_results.dat
    │   ├── rho0_results.dat
    │   ├── rms_all_error.dat
    │   ├── rms_all_noerr.dat
    │   ├── rms_imag_parts_error.dat
    │   ├── rms_imag_parts_noerr.dat
    │   ├── rms_real_parts_error.dat
    │   ├── rms_real_parts_noerr.dat
    │   ├── tau_50_results.dat
    │   ├── tau_arithmetic_results.dat
    │   ├── tau_geometric_results.dat
    │   ├── tau_max_results.dat
    │   ├── tau_mean_results.dat
    │   ├── tau_peak1_results.dat
    │   ├── tau_peak2_results.dat
    │   ├── tau_peaks_all_results.dat
    │   └── U_tau_results.dat
    ├── tau.dat
    └── version.dat

    1 directory, 48 files

The following output files will be created in the selected output directory.
These files are described below, sorted by category.

Input data
++++++++++

* *data.dat* contains the input data saved as :math:`\rho';\rho''~[\Omega m]`.
* *data_format.dat* contains the data format in the format usable with the
  ``--data_format`` command line option (usually **cre_cim**).
* Frequencies and corresponding angular frequencies (
   :math:`\omega = 2 \cdot \pi \cdot f`) are stored in the files
   *frequencies.dat* and *omega.dat*.
* The file *command.dat* holds the complexe call to the fit routine
* A JSON formatted file *inversion_options.json* stores internal inversion
  options. This file is mainly for debugging purposes, and needed to recreated
  inversion objects from fit results.

Filter results
++++++++++++++

* *filter_mask.dat* contains the remaining indices after a filter operation
  with `ddps.py`

Primary fit results
+++++++++++++++++++

* :math:`\tau` and :math:`s = log_{10}(\tau)` values are stored in the files
  *tau.dat* and *s.dat*, respectively.

* The regularization parameters of the last iterations are stored in the file
  *lambdas.dat*, one per line:

  ::

    1.000000000000000021e-03
    1.000000000000000056e-01

* The chargeability values of the last iteration can be found in
  *stats_and_rms/m_i_results.dat*

* The forward response of the final iteration is stored in *f.dat*

* RMS values are stored in the subdirectory *stats_and_rms*, using the
  following files (final RMS of each spectrum per line). *real/imag* here
  correspond to real part and imaginary part of resistivity, respectively. The
  *_error* suffix denotes RMS values computed with data weighting.

  ==========================  ==========================================================
  filename                    description
  ==========================  ==========================================================
  *rms_all_error.dat*         RMS of real and imaginary parts, including error weighting
  *rms_all_noerr.dat*         RMS of real and imaginary parts, without error weighting
  *rms_imag_parts_error.dat*  Error weighted RMS of imaginary parts
  *rms_imag_parts_noerr.dat*  Non-error weighted RMS of imaginary parts
  *rms_real_parts_error.dat*  Error weighted RMS of real parts
  *rms_real_parts_noerr.dat*  Non-error weighted RMS of real parts
  ==========================  ==========================================================

    .. math::

        RMS_{\text{no error}} = \sqrt{\frac{1}{N} \sum_i^N d_i - f_i(m)}\\
        RMS_{\text{with error}} = \sqrt{\frac{1}{N} \sum_i^N \frac{d_i - f_i(m)}{\epsilon_i}}

* The number of iterations for each spectrum are stored in *nr_iterations.dat*

* Data weighting errors are stored in *errors.dat*

* Normalization factors are stored in *normalization_factors.dat*

Integral parameters
+++++++++++++++++++

Statistical parameters are stored in the subdirectory *stats_and_rms*, and all
output files have the same file format. Each line contains the value of one
spectrum. This applies to the following files:

=============================  ===============================
filename                       stored values per line
=============================  ===============================
*m_i_results.dat*              :math:`m(\tau_i)`
*m_tot_n_results.dat*          :math:`log_{10}(m_{tot}^n)`
*m_tot_results.dat*            :math:`log_{10}(m_{tot}^n)`
*rho0_results.dat*             :math:`log_{10}(\rho_0)`
*tau_50_results.dat*           :math:`log_{10}(\tau_{50})`
*tau_mean_results.dat*         :math:`log_{10}(\tau_{mean})`
*tau_arithmetic_results.dat*   :math:`log_{10}(\tau_{arithmetic})`
*tau_geometric_results.dat*    :math:`log_{10}(\tau_{geometric})`
*tau_peak1_results.dat*        :math:`log_{10}(\tau_{peak}^1)`
*tau_peak2_results.dat*        :math:`log_{10}(\tau_{peak}^2)`
*tau_peaks_all_results.dat*    :math:`log_{10}(\tau_{peak}^i)`
*tau_x_\*.dat*                 :math:`log_{10}(\tau_x)`; see description below
*tau_max.dat*                  :math:`\tau` corresponding to max. chargeability. First occurence.
*U_tau_results.dat*            Uniformity parameter :math:`U_{\tau} = \frac{\tau_{60}}{\tau_{10}}`
*f_50_results.dat*
*f_mean_results.dat*
*f_peak1_results.dat*
*f_peak2_results.dat*
*f_peaks_all_results.dat*
*covf_results.dat*
*covm_results.dat*
=============================  ===============================

:math:`\tau_x`: Arbitrary cumulative relaxation times can be computed by setting
the environment variable **DD_TAU_X**. The string separates the requested
percentages as fractions with ';' characters.

For example, the following call to **dd_single** computes the 20%, 35%, and 60%
percentiles of the RTD:

::

    DD_TAU_X="0.2;0.35;0.6" dd_single.py

*Integral parameters* extracted from the RTD fall into two categories:
chargeability related values and relaxation time related values.  The first
category extracts information regarding the total or partial polarization
strength of the system, while the second extracts information regarding
relaxation times, i.e. the time scales on which the polarization processes take
place:

**Chargeability parameters:**

* The total chargeability :math:`m_{tot} = \sum_i^N m_i` is the analogon of the
  DD to the chargeability as defined by Seigel, 1959:
  :math:`m_{seigel} = \frac{\epsilon_{\infty} - \epsilon_0}{\epsilon_{\infty}}
  = \frac{\rho_0 - \rho_{\infty}}{\rho_0}` (this is also the definition used
  for :math:`m_{cc}`).  This is, howoever, only true insofar as the majority of
  the polarisation response of the system must be located within the measured
  frequency range for the DD to pick it up, while the original definition of
  the chargeability extends over the whole frequency domain. Thus, not fully
  resolved polarization peaks indicate an underestimation of the total
  polarization of the system by :math:`m_{tot}` in the DD.
* Nordsiek and Weller, 2008 computed chargeability sums for each
  relaxation time decades, normed by :math:`m_{tot}`. These so called *decade
  loadings* provide frequency (or relaxation time) dependent chargeabilities.
* The total, normalized chargeability :math:`m_{tot}^n =
  \frac{m_{tot}}{\rho_0}` is obtained by normalizing the total chargeability
  with the DC resistivity (Scott2003phd, Weller2010g_a). It gives an indication
  of the total polarization of the measured system without any influence of any
  occuring resistivity contrasts.

**Relaxation time parameters:**

Various parameters to determine characteristic relaxation times from the whole
RTD were proposed:

* Cumulative relaxation times :math:`\tau_x` denote relaxation times at which a
  certain percentage :math:`x` of chargeability is reached
  (Norsieg and Weller, 2008; Zisser et al. 2010). For example,
  :math:`\tau_{50}` is the median relaxation time of a given RTD.
* Nordsiek and Weller, 2008 introduced the non-uniformity parameter
  :math:`U_\tau = \frac{\tau_{10}}{\tau_{60}}` which characterizes the width of
  the RTD. However, no information regarding the number of siginificant peaks
  in the RTD can be derived using :math:`U_{\tau}`.
* Tong et al, 2004 use the arithmetic and geometric means of the relaxation
  times for further analysis:

  .. math::

      \tau_g = \left(\prod_{i=1}^N \tau_i^{m_i} \right)^{\frac{1}{\sum_{i=1}^N
      m_i}}\\
      \tau_a = \frac{\sum_{i=1}^N m_i \cdot \tau_i}{\sum_{i=1}^N m_i}

* Nordsiek et al., 2008 introduced the logarithmic average relaxation time
  :math:`\tau_{mean}`

  .. math::

      \tau_{mean} = \frac{exp(\sum_i m_i \cdot log(\tau_i))}{\sum m_i}`

The listed relaxation time parameters do not take into account the specific
shape of the RTD, and thus it is also useful to determine local maxima of the
distribution, e.g. to extract characteristic relaxation times specific to
certain polarisation peaks. This approach has conceptual similarities to the
use of (multi-)Cole-Cole models as the produced relaxation times can be
directly related to polarization peaks. The relaxation time with the larges
corresponding chargeability is called :math:`\tau_{max}`
(Attwa2013hess), and the in the generalized form the
relaxation time :math:`\tau_{peak}^i`, refers to the *i*-th local maximum of
the RTD, starting with the low frequencies (i.e. high :math:`\tau` values).
This approach can recover multiple peaks without any knowlegdge of the exact
number of peaks in the data.  However, this process can yield multiple small
maxima if the smoothing between adjacent chargeabilitiy values is not strong
enough. In these cases the corresponding smoothing parameters of the DD should
be increased.