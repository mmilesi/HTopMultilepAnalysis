#!/usr/bin/env python

""" run_modifytree_MM.py: simple script to execute a ROOT macro by calling the CINT interpreter with TROOT::ProcessLine() """

__author__     = "Marco Milesi, Francesco Nuti"
__email__      = "marco.milesi@cern.ch, francesco.nuti@cern.ch"
__maintainer__ = "Marco Milesi"

import os, subprocess, sys, time, shlex, copy

sys.path.append(os.path.abspath(os.path.curdir))

from ROOT import gROOT

gROOT.SetBatch(True)

#oldpath  = '/data/mmilesi/ttH/MergedDatasets/Merged_v029/ICHEP_NOLEPISO/Merged_Melb15_ttH_029_NoLepIso_DxAOD_DATA/'
#newpath  = '/data/mmilesi/ttH/MergedDatasets/Merged_v029/ICHEP_NOLEPISO/Merged_Melb15_ttH_029_NoLepIso_DxAOD_DATA_MM_WEIGHTED/'

# -------------------------------------------------------------------------------------------------------------

#oldpath = "/afs/cern.ch/user/m/mmilesi/work/private/ttH/MiniNTup/25ns_v7/25ns_v7_Data_Original/"
#newpath = "/afs/cern.ch/user/m/mmilesi/work/private/ttH/MiniNTup/25ns_v7/25ns_v7_Data_MM_WEIGHTED/"
#rr_dir = "/afs/cern.ch/user/m/mmilesi/ttH/RUN2/HTopMultilepAnalysisCode/trunk/HTopMultilepAnalysis/PlotUtils/OutputPlots_MMRates_25ns_v7_FinalSelection_NominalBinning/Rates_YesSub_LHInput"

#oldpath = "/afs/cern.ch/user/m/mmilesi/work/private/ttH/MiniNTup/25ns_v7/25ns_v7_410000_Original/"
#newpath = "/afs/cern.ch/user/m/mmilesi/work/private/ttH/MiniNTup/25ns_v7/25ns_v7_410000_MM_WEIGHTED/"
#rr_dir = "/afs/cern.ch/user/m/mmilesi/ttH/RUN2/HTopMultilepAnalysisCode/trunk/HTopMultilepAnalysis/PlotUtils/OutputPlots_MMClosureRates_25ns_v7_FinalSelection_NominalBinning/Rates_YesSub_LHInput"

# -------------------------------------------------------------------------------------------------------------

oldpath = "/afs/cern.ch/user/m/mmilesi/work/private/ttH/MiniNTup/25ns_v7/25ns_v7_Data_Original/"
newpath = "/afs/cern.ch/user/m/mmilesi/work/private/ttH/MiniNTup/25ns_v7/25ns_v7_Data_MM_WEIGHTED_AVGMUFAKE/"
rr_dir = "/afs/cern.ch/user/m/mmilesi/ttH/RUN2/HTopMultilepAnalysisCode/trunk/HTopMultilepAnalysis/PlotUtils/OutputPlots_MMRates_25ns_v7_FinalSelection_NominalBinning/Rates_YesSub_AvgMuFake"

#oldpath = "/afs/cern.ch/user/m/mmilesi/work/private/ttH/MiniNTup/25ns_v7/25ns_v7_410000_Original/"
#newpath = "/afs/cern.ch/user/m/mmilesi/work/private/ttH/MiniNTup/25ns_v7/25ns_v7_410000_MM_WEIGHTED_AVGMUFAKE/"
#rr_dir = "/afs/cern.ch/user/m/mmilesi/ttH/RUN2/HTopMultilepAnalysisCode/trunk/HTopMultilepAnalysis/PlotUtils/OutputPlots_MMClosureRates_25ns_v7_FinalSelection_NominalBinning/Rates_YesSub_AvgMuFake"

# -------------------------------------------------------------------------------------------------------------

addMM    = 'YES' # Set to 'YES' if MM weight branch does not exist yet
nentries = 'ALL' #ALL

if not os.path.exists(newpath):
    os.makedirs(newpath)

gROOT.LoadMacro("modifyttree_MM.cxx+g")
group_list = os.listdir(oldpath)
group_list = group_list[:]

do_closure = None

for group in group_list:
    if not os.path.isdir(oldpath+group):
        continue
    if not os.path.exists(newpath+group):
        os.makedirs(newpath+group)
    sample_list = os.listdir(oldpath+group+'/')
    for sample in sample_list:
        print group+'/'+sample
        infile=oldpath+group+'/'+sample
        outfile=newpath+group+'/'+sample

        if "physics_Main" in sample: do_closure = "NO"
        else:                        do_closure = "YES"

        command_line = 'modifyttree_MM(\"'+infile+'\",\"'+outfile+'\",\"'+addMM+'\",\"'+rr_dir+'\",\"'+do_closure+'\",\"'+nentries+'\")'

        print command_line
        gROOT.ProcessLine(command_line);

