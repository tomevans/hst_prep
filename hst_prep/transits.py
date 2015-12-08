import numpy as np
import matplotlib.pyplot as plt
import pdb, sys, os
from planetc import transit

HST_ORB_PERIOD_DAYS = 96.36/60./24.

def phase_constraints( jd_cycle_end, syspars, P_unc=0.0, T0_unc=0.0, phase_range=[], n_hstorb=5, nsigma=3 ):
    """
    Given a particular transit system and a set of orbital phase
    constraints, plot the resulting HST phase coverage over the
    specified number of orbits.
    """

    # Find the last transit of the HST cycle:
    Tmid = syspars['T0']
    while Tmid<jd_cycle_end:
        Tmid += syspars['P']
    while Tmid>=jd_cycle_end:
        Tmid -= syspars['P']

    # Get the number of planet orbits between the 
    # reference epoch and the HST cycle:
    norb = int( np.round( np.abs( Tmid - syspars['T0'] )/syspars['P'] ) )
    
    # Determine the uncertainty on the mid-time by
    # the last transit of the HST cycle:
    unc = T0_unc + norb*P_unc

    # Determine the JD corresponding to the earliest possible
    # observation start time, i.e. the lower phase constraint
    # and assuming the lower limit of the possible Tmid value:
    phase_low = phase_range[0] - nsigma*unc/syspars['P']
    phase_upp = phase_range[1] + nsigma*unc/syspars['P']
    jd_start = Tmid - syspars['P']*( 1-phase_low )

    # Determine the offset between the earliest possible start
    # time and the latest possible start time:
    delt = syspars['P']*( phase_range[1]-phase_range[0] ) + 2*nsigma*unc

    # Amount of time spent observing
    # per HST orbit:
    tvis = 50./60./24. # i.e. 50 minutes

    # Make sure the limb darkening is turned off:
    syspars['ld'] = None

    # Set an arbitrary number of points to be evaluated
    # per HST orbit, at sufficiently high time-sampling to
    # trace out the shape of the transit:
    npoints = 100
    jd = []
    for i in range( n_hstorb ):
        jd_i = np.r_[ jd_start:jd_start+tvis:1j*npoints ]
        jd += [ jd_i ]
        jd_start += HST_ORB_PERIOD_DAYS
    jd1 = np.concatenate( jd )
    t1 = 1+( jd1-Tmid )/syspars['P']
    psignal1 = transit.ma02_aRs( jd1, **syspars )
    jd2 = jd1+delt
    t2 = 1+( jd2-Tmid )/syspars['P']
    psignal2 = transit.ma02_aRs( jd2, **syspars )
    jdfull = np.r_[ jd1.min():jd2.max():1j*1000 ]
    tfull = 1+( jdfull-Tmid )/syspars['P']
    psignalfull = transit.ma02_aRs( jdfull, **syspars )

    # Make plot:
    plt.figure( figsize=[14,6] )
    c1 = 'c'
    c2 = 'r'
    plt.plot( tfull, psignalfull, '-k', lw=2, zorder=0 )
    ms = 8
    plt.plot( t1, psignal1, 'o', mfc=c1, mec='none', ms=ms, zorder=1 )
    plt.plot( t2, psignal2, 'o', mfc=c2, mec='none', ms=ms*0.5, zorder=2 )
    dy = psignal1.max()-psignal1.min()
    ymax = psignal1.max()+0.1*dy
    ymin = psignal1.min()-0.1*dy
    plt.ylim( [ ymin, ymax ] )
    xmin = min( [ t1.min(), t2.min() ] )
    xmax = max( [ t1.max(), t2.max() ] )
    dx = xmax-xmin
    plt.xlim( [ xmin-0.1*dx, xmax+0.1*dx ] )
    plt.ylabel( 'Relative flux' )
    plt.xlabel( 'Planet orbital phase' )
    text_fs = 14
    text_str = 'Assuming:\n  HST period = {0:.2f} minutes\n  Visibility = {1:.2f} minutes'\
               .format( HST_ORB_PERIOD_DAYS*24*60, tvis*24*60 )
    text_str = '{0}\n  P = {1:.8f} days\n  T0 = {2:.8f}'.format( text_str, syspars['P'], syspars['T0'] )
    text_str = '{0}\n\nSpecified phase range:\n  Lower = {1:.5f}\n  Upper = {2:.5f}'\
               .format( text_str, phase_range[0], phase_range[1] )
    text_str = '{0}\n\n{1}-sigma plausible range:\n  Phase lower = {2:.5f}\n  Phase upper = {3:.5f}'\
               .format( text_str, nsigma, phase_low, phase_upp )
    ax = plt.gca()
    ax.text( 0.05, 0.7, text_str, fontsize=text_fs, transform=ax.transAxes, \
             horizontalalignment='left', verticalalignment='top' )

    return None
