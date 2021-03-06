#!/usr/bin/env python

import glob, os, sys, subprocess, shutil, string, argparse

parser = argparse.ArgumentParser(description="Wrapper script for MakePlots_HTopMultilep.py. This gets called on the PBS worker node via the PBS script generated by submit-PBS-ARRAY-MakePlots_HTopMultilep.py. The variable to be plotted gets retrieved via the PBS_ARRAYID index.")

parser.add_argument("--optstr", dest="optstr", action="store", type=str)
parser.add_argument("--varlist", dest="varlist", action="store", type=str, nargs="+")
parser.add_argument("--outputpath", dest="outputpath", action="store", type=str)

args = parser.parse_args()

if __name__ == '__main__':

    # Read varlist from argparse.
    # It will automagically re-create a python list from the multiple arguments of the input --varlist option.

    varlist = args.varlist

    # Get the var from the PBS_ARRAYID

    pbs_array_idx = int(os.getenv('PBS_ARRAYID'))

    var = varlist[pbs_array_idx]

    print("Current job index PBS_ARRAYID={0}, var={1}".format(pbs_array_idx,var))

    # OK, execute plotting script for this var!

    # NB: it's crucial to make this call when running on the worker node, otherwise
    # python will not be able to find modules in Plotter/

    os.chdir(os.path.abspath(os.path.curdir)+"/HTopMultilepAnalysis/PlotUtils")

    plotscript = os.path.abspath(os.path.curdir) + "/Plotter/MakePlots_HTopMultilep.py"
    optlist = args.optstr.split(' ')

    cmdlist = ['python',plotscript] + optlist + ['--submitPBSVar',var]
    cmd = " ".join( "{0}".format(c) for c in cmdlist )

    print("Executng command:\n{0}".format(cmd))

    subprocess.call( cmd, shell = True )

    # Now move the output to the target directory

    outputpath  = args.outputpath
    if not outputpath[-1] == '/':
        outputpath += '/'

    # Get all subdirs in current location whose name starts with "OutputPlots_", rsync them to output directory, and remove the local copy

    job_outdirs = [ dir for dir in os.listdir(".") if "OutputPlots_" in dir and os.path.isdir(dir)  ]

    for dir in job_outdirs:
        thisdir = dir
        if thisdir[-1] == '/':
            thisdir = thisdir[:-1]
        subprocess.call( ['rsync','-azP',thisdir,outputpath] )
        shutil.rmtree(thisdir)
