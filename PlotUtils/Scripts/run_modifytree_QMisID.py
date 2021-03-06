#!/usr/bin/env python

""" run_modifytree_QMisID.py: simple script to execute a ROOT macro by calling the CINT interpreter with TROOT::ProcessLine() """

__author__     = "Marco Milesi, Francesco Nuti"
__email__      = "marco.milesi@cern.ch, francesco.nuti@cern.ch"
__maintainer__ = "Marco Milesi"

import os, subprocess, sys, time, shlex, copy

sys.path.append(os.path.abspath(os.path.curdir))

from ROOT import gROOT

gROOT.SetBatch(True)

# -------------------------------------------------------------------------------------------------------------

#oldpath = "/afs/cern.ch/user/m/mmilesi/work/private/ttH/MiniNTup/25ns_v7/25ns_v7_Data_Original/"
#newpath = "/afs/cern.ch/user/m/mmilesi/work/private/ttH/MiniNTup/25ns_v7/25ns_v7_Zjets_QMisID_WEIGHTED_testing/"

# -------------------------------------------------------------------------------------------------------------

#oldpath = "/afs/cern.ch/user/m/mmilesi/work/private/ttH/MiniNTup/25ns_v14/25ns_v14_Direct_Data_Original/"
#newpath = "/afs/cern.ch/user/m/mmilesi/work/private/ttH/MiniNTup/25ns_v14/25ns_v14_Direct_Data_QMisID_WEIGHTED/"

# -------------------------------------------------------------------------------------------------------------

#oldpath = "/afs/cern.ch/user/m/mmilesi/work/private/ttH/MiniNTup/25ns_v14/25ns_v14_Direct_DLT_Data_Original/"
#newpath = "/afs/cern.ch/user/m/mmilesi/work/private/ttH/MiniNTup/25ns_v14/25ns_v14_Direct_DLT_Data_QMisID_WEIGHTED/"

# -------------------------------------------------------------------------------------------------------------

#oldpath = "/afs/cern.ch/user/m/mmilesi/work/private/ttH/MiniNTup/25ns_v15/25ns_v15_Direct_Data_Original/"
#newpath = "/afs/cern.ch/user/m/mmilesi/work/private/ttH/MiniNTup/25ns_v15/25ns_v15_Direct_Data_QMisID_WEIGHTED/"

# -------------------------------------------------------------------------------------------------------------

#oldpath = "/afs/cern.ch/user/m/mmilesi/work/private/ttH/MiniNTup/25ns_v17/25ns_v17_Direct_Data_Original/"
#newpath = "/afs/cern.ch/user/m/mmilesi/work/private/ttH/MiniNTup/25ns_v17/25ns_v17_Direct_Data_QMisID_WEIGHTED/"

#oldpath = "/coepp/cephfs/mel/mmilesi/ttH/MiniNTup/25ns_v17/25ns_v17_Direct_Data_Original/"
#newpath = "/coepp/cephfs/mel/mmilesi/ttH/MiniNTup/25ns_v17/25ns_v17_Direct_Data_QMisID_WEIGHTED/"

# -------------------------------------------------------------------------------------------------------------

#oldpath = "/afs/cern.ch/user/m/mmilesi/work/private/ttH/MiniNTup/25ns_v18/25ns_v18_Skim_Data_Original/"
#newpath = "/afs/cern.ch/user/m/mmilesi/work/private/ttH/MiniNTup/25ns_v18/25ns_v18_Skim_Data_QMisID_WEIGHTED/"

# -------------------------------------------------------------------------------------------------------------

oldpath = "/afs/cern.ch/user/m/mmilesi/work/private/ttH/MiniNTup/25ns_v19/25ns_v19_Skim_Data_Original/"
newpath = "/afs/cern.ch/user/m/mmilesi/work/private/ttH/MiniNTup/25ns_v19/25ns_v19_Skim_Data_QMisID_WEIGHTED/"

# -------------------------------------------------------------------------------------------------------------

# path and name of files w/ QMisID rates
#
glob_rate_path = "$ROOTCOREBIN/data/HTopMultilepAnalysis/External/"

#filename_T     = "QMisIDRates_Data_2016_T_25ns_v14.root"
#filename_AntiT = "QMisIDRates_Data_2016_antiT_25ns_v14.root"

#filename_T     = "QMisIDRates_Data_2016_T_25ns_v15.root"
#filename_AntiT = "QMisIDRates_Data_2016_antiT_25ns_v15.root"

#filename_T     = "QMisIDRates_Data_2016_T_25ns_v17.root"
#filename_AntiT = "QMisIDRates_Data_2016_antiT_25ns_v17.root"

#filename_T     = "QMisIDRates_Data_2016_T_25ns_v18.root"
#filename_AntiT = "QMisIDRates_Data_2016_TanitiT_25ns_v18.root"

filename_T     = "QMisIDRates_Data_2016_T_25ns_v19.root"
filename_AntiT = "QMisIDRates_Data_2016_TanitiT_25ns_v19.root"

# -------------------------------------------------------------------------------------------------------------

addQMisID     = 'YES' # Set to 'YES' if QMisID weight branch does not exist yet, else use 'NO' ( --> the script will update the existing QMisID weight)
nentries      = 'ALL' # Set the number of entries. Use 'ALL' to run on all events
useGroupNTup  = 'YES' # Are we using group ntuples?
useMixedRates = 'YES' # Set to 'YES' if the rates for !T electrons were measured in a mixed (T!T || !TT) region

if not os.path.exists(newpath):
    os.makedirs(newpath)

gROOT.LoadMacro("modifyttree_QMisID.cxx+g")
group_list = os.listdir(oldpath)
group_list = group_list[:]

for group in group_list:
    if not os.path.isdir(oldpath+group):
        continue
    if not os.path.exists(newpath+group):
        os.makedirs(newpath+group)
    sample_list = os.listdir(oldpath+group+'/')
    for sample in sample_list:
	if "hist-" in sample:
	   continue
        print group+'/'+sample
        infile=oldpath+group+'/'+sample
        outfile=newpath+group+'/'+sample

        command_line = 'modifyttree_QMisID(\"'+infile+'\",\"'+outfile+'\",\"'+glob_rate_path+'\",\"'+filename_AntiT+'\",\"'+filename_T+'\",\"'+addQMisID+'\",\"'+nentries+'\",\"'+useGroupNTup+'\",\"'+useMixedRates+'\")'

        print command_line
        gROOT.ProcessLine(command_line);
