#!/usr/bin/python
 #
 # *********************************************************************************
 # A python plotting script for the main HTopMultilep RunII analysis
 #
 #
 # Authors:
 #  Marco Milesi ( marco.milesi@cern.ch ), Francesco Nuti ( francesco.nuti@cern.ch )
 #
 # *********************************************************************************

import os
import sys
import math

sys.path.append(os.path.abspath(os.path.curdir))

# -------------------------------
# Parser for command line options
# -------------------------------
import argparse

parser = argparse.ArgumentParser(description='Plotting python macro for ttH to multileptons analysis.')

#***********************************
# positional arguments (compulsory!)
#***********************************
parser.add_argument('inputDir', metavar='inputDir',type=str,
                   help='path to the directory containing input files')
parser.add_argument('samplesCSV', metavar='samplesCSV',type=str,
                   help='path to the csv file containing the processes of interest with their cross sections and other metadata')
#*******************
# optional arguments
#*******************
parser.add_argument('--selection', dest='selection', action='store', default='', type=str,
                    help='the selection chosen (e.g. noTypeOriginMatch, noTruthMatch... )')
parser.add_argument('--channel', dest='channel', action='store', default='TwoLepSR', type=str,
		    help='the channel chosen (e.g. TwoLepSR, ThreeLepSR... )')
parser.add_argument('--ratesFromMC', dest='ratesFromMC', action='store_true', default=False,
                    help='Extract rates from pure simulation. Use w/ option --channel=MMRates')
parser.add_argument('--outdirname', dest='outdirname', action='store', default='', type=str,
		    help='specify a name to append to the output directory')
parser.add_argument('--fakeMethod', dest='fakeMethod', action='store', default='MC', type=str,
		    help='the fake estimation method chosen ( MC,MM,FF,ABCD )')
parser.add_argument('--lepFlavComp', dest='lepFlavComp', action='store', default='', type=str,
                    help='flavour composition of the SS pair ( ee, mm, em )')
parser.add_argument('--doLogScaleX', dest='doLogScaleX', action='store_true',
                    help='use log scale on the X axis')
parser.add_argument('--doLogScaleY', dest='doLogScaleY', action='store_true',
                    help='use log scale on the Y axis')
parser.add_argument('--doSyst', dest='doSyst', action='store_true',
                    help='run systematics')
parser.add_argument('--debug', dest='debug', action='store_true',
                    help='run in debug mode')
parser.add_argument('--noSignal', action='store_true', dest='noSignal',
                    help='exclude signal')
parser.add_argument('--noStandardPlots', action='store_true', dest='noStandardPlots',
                    help='exclude all standard plots')
parser.add_argument('--doEPS', action='store_true', dest='doEPS',
                    help='make a .eps output file (NB: heavy size!)')
parser.add_argument('--doChFlipRate', dest='doChFlipRate', action='store_true',
                    help='measure charge flip rate in MC (to be used with MMClosureRates channel')

args = parser.parse_args()

# -------------------------------
# Important to run without popups
# -------------------------------
from ROOT import gROOT

gROOT.SetBatch(True)

#gROOT.ProcessLineSync(".x /home/mmilesi/PhD/ttH_MultiLeptons/RUN2/PlotUtils/common_ntuple_melbourne/Scripts/containsAny.C+")
#gROOT.LoadMacro("/home/mmilesi/PhD/ttH_MultiLeptons/RUN2/PlotUtils/common_ntuple_melbourne/Scripts/containsAny.C+")
#from ROOT import containsAny

# -----------------
# Some ROOT imports
# -----------------
from ROOT import TH1I, TMath, TFile, TAttFill, TColor, kBlack, kWhite, kGray, kBlue, kRed, kYellow, kAzure, kTeal, kSpring, kOrange, kGreen, kCyan, kViolet, kMagenta, kPink, Double

# ---------------------------------------------------------------------
# Importing all the tools and the definitions used to produce the plots
# ---------------------------------------------------------------------
from Plotter.BackgroundTools_ttH import loadSamples, Category, Background, Process, VariableDB, Variable, Cut, Systematics, Category
# ---------------------------------------------------------------------------
# Importing the classes for the different processes.
# They contains many info on the normalization and treatment of the processes
# ---------------------------------------------------------------------------
from Plotter.ttH2015_Background import MyCategory, TTHBackgrounds2015

# -------------
# Check channel
# -------------
list_available_channel = ['TwoLepSR','ThreeLepSR','FourLepSR','MMRates',
			  'TwoLepLowNJetCR', 'ThreeLepLowNJetCR',
			  'WZonCR', 'WZoffCR', 'WZHFonCR', 'WZHFoffCR',
			  'ttWCR', 'ttZCR',
			  'ZSSpeakCR', 'DataMC', 'MMClosureTest', 'MMClosureRates']

try:
    args.channel in list_available_channel
except ValueError:
    sys.exit('the channel specified (', args.channel ,') is incorrect. Must be one of: ', list_available_channel)

doTwoLepSR      	= bool( args.channel == 'TwoLepSR' )
doThreeLepSR    	= bool( args.channel == 'ThreeLepSR' )
doFourLepSR     	= bool( args.channel == 'FourLepSR' )
doMMRates          	= bool( args.channel == 'MMRates' )
doTwoLepLowNJetCR       = bool( args.channel == 'TwoLepLowNJetCR' )
doThreeLepLowNJetCR     = bool( args.channel == 'ThreeLepLowNJetCR' )
doWZonCR                = bool( args.channel == 'WZonCR' )
doWZoffCR               = bool( args.channel == 'WZoffCR' )
doWZHFonCR              = bool( args.channel == 'WZHFonCR' )
doWZHFoffCR             = bool( args.channel == 'WZHFoffCR' )
dottWCR                 = bool( args.channel == 'ttWCR' )
dottZCR                 = bool( args.channel == 'ttZCR' )
doZSSpeakCR             = bool( args.channel == 'ZSSpeakCR' )
doDataMCCR              = bool( args.channel == 'DataMC' )
doMMClosureTest         = bool( args.channel == 'MMClosureTest' )
doMMClosureRates        = bool( args.channel == 'MMClosureRates' )

# -----------------------------------------
# a comprehensive flag for all possible SRs
# -----------------------------------------
doSR = (doTwoLepSR or doThreeLepSR or doFourLepSR)

# -----------------------------------------
# a comprehensive flag for the low-Njet CR
# -----------------------------------------
doLowNJetCR = (doTwoLepLowNJetCR or doThreeLepLowNJetCR)

# ------------------------------------------
# a comprehensive flag for all the other CRs
# ------------------------------------------
doOtherCR = (doWZonCR or doWZoffCR or doWZHFonCR or doWZHFoffCR or dottWCR or dottZCR or doZSSpeakCR or doMMRates or doDataMCCR or doMMClosureTest or doMMClosureRates)

# ------------------------------------------------
# make standard plots unless differently specified
# ------------------------------------------------
doStandardPlots = False if (args.noStandardPlots) else (doSR or doLowNJetCR or doOtherCR)

# ----------------------------
# Check fake estimation method
# ----------------------------
list_available_fakemethod = ['MC','MM','FF']

try:
    args.fakeMethod in list_available_fakemethod
except ValueError:
    sys.exit('the Fake Method specified (', args.fakeMethod ,') is incorrect. Must be one of ', list_available_fakemethod)

doMM   = bool( args.fakeMethod == 'MM' )
doFF   = bool( args.fakeMethod == 'FF' )
doABCD = bool( args.fakeMethod == 'ABCD' )

# -----------------------------------------------
# Check lepton flavour composition of the SS pair
# -----------------------------------------------
list_available_flavcomp = ['ee','mm','em', '']

try:
    args.lepFlavComp in list_available_flavcomp
except ValueError:
    sys.exit('ERROR: the lepton flavour composition of the SS pair is incorrect. Must be one of ', list_available_flavcomp)
else:
    if not ( args.lepFlavComp ):
        print 'WARNING: lepton flavour composition of the SS pair unspecified ( i.e., empty string '' )... will not use any restriction on the lepton flavour'


# ----------------------------------------------------
# When in debug mode, print out all the input commands
# ----------------------------------------------------
if ( args.debug ):
    print args

# --------------------------
# Retrieve the input samples
# --------------------------
inputs = loadSamples(
                        # path of the data to be processed
                        inputdir    = args.inputDir + args.selection,
                        samplescsv  = args.samplesCSV,
                        nomtree     = 'physics',
                        # name of the trees that contains values for shifted systematics
                        systrees =  [
                                        ##'METSys',
                                        #'ElEnResSys',
		                        #'ElES_LowPt',
					#'ElES_Zee',
					#'ElES_R12',
					#'ElES_PS',
                                        ##'EESSys',
					#'MuSys',
                                        ##'METResSys',
                                        ##'METScaleSys',
                                        #'JES_Total',
                                        #'JER',
                                    ],
                    )

# ------------------------------------------------------
# Here you include all names of variables to be plotted,
# with min, max, number of bins and ntuple name.
# ------------------------------------------------------
vardb = VariableDB()

doRelaxedBJetCut = False # be inclusive in bjet multiplicity

# -----------------------------------------------------
# The list of event-level cuts ( a-la TTree->Draw("") )
#
# WARNING:
# To avoid unexpected behaviour,
# ALWAYS enclose the cut string in '()'!!!
#
# -----------------------------------------------------
vardb.registerCut( Cut('DummyCut',    '( 1 )') )
vardb.registerCut( Cut('IsMC',        '( isMC == 1 )') )
#
# To ask for an event be passing an OR of triggers
#
#vardb.registerCut( Cut('TrigDec',     '( passHLT == 1 && ( Sum$( ( isMC == 1 && passedTriggers == \"HLT_e24_lhmedium_L1EM18VH\" ) + ( isMC == 0 && passedTriggers == \"HLT_e24_lhmedium_L1EM20VH\" ) + ( passedTriggers == \"HLT_e60_lhmedium\" ) + ( passedTriggers == \"HLT_e120_lhloose\" ) + ( passedTriggers == \"HLT_mu20_iloose_L1MU15\" ) + ( passedTriggers == \"HLT_mu50\" ) ) > 0 ) )') )
# the following does not work b/c TTreeFormula does not accept strings as arguments
#vardb.registerCut( Cut('TrigDec',    '( passHLT == 1 && ( containsAny(passedTriggers,\"HLT_e24_lhmedium_L1EM18VH,HLT_e24_lhmedium_L1EM20VH,HLT_e60_lhmedium,HLT_e120_lhloose,HLT_mu20_iloose_L1MU15,HLT_mu50\") ) )') )
#
# To ask for an event be passing any of the saved triggers
#
vardb.registerCut( Cut('TrigDec',     '( passHLT == 1 )') )
vardb.registerCut( Cut('TrigMatch',   '( ( lep_isTrigMatched[0] == 1 && ( ( lep_flavour[0] == 11 && lep_pt[0] > 25e3 ) || ( lep_flavour[0] == 13 && lep_pt[0] > 22e3 ) ) ) || ( lep_isTrigMatched[1] == 1 && ( ( lep_flavour[1] == 11 && lep_pt[1] > 25e3 ) || ( lep_flavour[1] == 13 && lep_pt[1] > 22e3 ) ) ) )') )
if doRelaxedBJetCut:
  vardb.registerCut( Cut('NBJet',      '( njets_mv2c20_Fix77 >= 0 )') )
else:
  vardb.registerCut( Cut('NBJet',       '( njets_mv2c20_Fix77 > 0 )') )
vardb.registerCut( Cut('LargeNBJet',  '( njets_mv2c20_Fix77 > 1 )') )
vardb.registerCut( Cut('BJetVeto',    '( njets_mv2c20_Fix77 == 0 )') )
vardb.registerCut( Cut('OneBJet',     '( njets_mv2c20_Fix77 == 1 )') )
vardb.registerCut( Cut('TauVeto',     '( ntau == 0 )') )
vardb.registerCut( Cut('OneTau',      '( ntau == 1 )') )
vardb.registerCut( Cut('NJet2L',      '( njets >= 4 )') )
vardb.registerCut( Cut('NJet3L',      '( njets >= 4 || ( njets_mv2c20_Fix77 > 1 && njets == 3 ) )') )
vardb.registerCut( Cut('NJet4L',      '( njets >= 2 )') )
if doRelaxedBJetCut:
  vardb.registerCut( Cut('LowJetCR',  '( njets > 0 && njets < 4 )') )
  #vardb.registerCut( Cut('LowJetCR', '( njets > 1 && njets < 4 )') )
else:
  vardb.registerCut( Cut('LowJetCR',    '( njets > 0 && njets < 4 )') )
vardb.registerCut( Cut('LowJetCR_ttW','( njets > 1 && njets < 4 )') )
#vardb.registerCut( Cut('2Lep',        '( nlep == 2 && ( lep_pt[0] > 20e3 && lep_pt[1] > 20e3 ) )') )
vardb.registerCut( Cut('2Lep',        '( nlep == 2 && ( lep_pt[0] > 25e3 && lep_pt[1] > 25e3 ) )') )
vardb.registerCut( Cut('2LepRelaxed', '( nlep == 2 && ( lep_pt[0] > 20e3 && lep_pt[1] > 10e3 ) )') )
vardb.registerCut( Cut('2LepTau',     '( nlep == 2 && ntau > 0 && ( lep_charge[0] * tau_charge[0] ) < 0 && ( lep_pt[0] > 15e3 && lep_pt[1] > 15e3 ) )') )
vardb.registerCut( Cut('SS',          '( isSS01 == 1 )') )
vardb.registerCut( Cut('3Lep',        '( nlep == 3 && isSS12 == 1 && lep_isTightSelected[0] == 1 && TMath::Abs( lep_charge[0] + lep_charge[1] + lep_charge[2] ) == 1 && lep_pt[1] > 20e3 && lep_pt[2] > 20e3 && mll01 > 12e3 && mll02 > 12e3 )') )
vardb.registerCut( Cut('4Lep',        '( nlep == 4 && lep_pt[0] > 25e3 && lep_pt[1] > 15e3 && lep_isTightSelected[0] == 1 && lep_isTightSelected[1] == 1 && lep_isTightSelected[2] == 1 && lep_isTightSelected[3] == 1 && TMath::Abs( lep_charge[0] + lep_charge[1] + lep_charge[2] + lep_charge[3] ) == 0 && ( ( mJPsiCand_ee > 10e3 || mJPsiCand_ee < 0.0 ) && ( mJPsiCand_mm > 10e3 || mJPsiCand_mm < 0.0 ) ) )') )
vardb.registerCut( Cut('SF_Event',    '( nmuon == 2 || nel == 2 )') )
vardb.registerCut( Cut('MuMu_Event',  '( nmuon == 2 )') )
vardb.registerCut( Cut('ElEl_Event',  '( nel == 2 )') )
vardb.registerCut( Cut('OF_Event',    '( nmuon == 1 && nel == 1 )') )
vardb.registerCut( Cut('MuEl_Event',  '( nmuon == 1 && nel == 1 && lep_flavour[0] == 13 )') )
vardb.registerCut( Cut('ElMu_Event',  '( nmuon == 1 && nel == 1 && lep_flavour[0] == 11 )') )
# temporary, to be used for 2 lep SF, OS CR (Z peak): keep events where leading jet |eta| in the barrel
#
vardb.registerCut( Cut('Jet0FwdCut',  '( TMath::Abs(jet_eta[0]) < 2.5 )') )
# apply to reduce charge flip contamination
#
vardb.registerCut( Cut('OF_ElEtaCut', '( TMath::Abs(el_eta[0]) < 1.37 )') )
vardb.registerCut( Cut('SF_ElEtaCut', '( ( TMath::Abs(el_eta[0]) < 1.37 && TMath::Abs(el_eta[1]) < 1.37 ) )') )
# require all leptons to be tight
#
vardb.registerCut( Cut('TightLeptons_2Lep',  '( lep_isTightSelected[0] == 1 && lep_isTightSelected[1] == 1 )') )
vardb.registerCut( Cut('TightLeptons_3Lep',  '( lep_isTightSelected[0] == 1 && lep_isTightSelected[1] == 1 && lep_isTightSelected[2] == 1 )') )

# -------------------------------------------------------------------------------
# the following cuts must be used only on MC :
#
#   -) plot only prompt-matched MC to avoid double counting of non prompt
#      (as they are estimated via MM or FF)
#   -) in case there are electrons in the regions, also brem electrons must be taken into account
#   -) what is left must be charge flip
#
# Use these cuts to plot specific MC contaminations in:
#
#   -) SR and low njet CR
#     (here you want the pure prompt MC contribution
#      to be plotted in SR/low-jet CR if
#      fakes and charge flips are already taken into account
#      by rescaling the data)
#
#   -) CR for FAKE rate measurement
#      (here you want to plot whatever is NON-non-prompt,
#       which then you will subtract to data for the fake rate estimate)
#
# Values of MC truth matching flags ( i.e., 'truthType', 'truthOrigin' ) are defined in MCTruthClassifier:
#
# https://svnweb.cern.ch/trac/atlasoff/browser/PhysicsAnalysis/MCTruthClassifier/trunk/MCTruthClassifier/MCTruthClassifierDefs.h
#
# -------------------------------------------------------------------------------

# 1.
# event passes this cut if ALL leptons are prompt (MCTruthClassifier --> Iso), and none is charge flip
#
vardb.registerCut( Cut('2Lep_PurePromptEvent', '( isMC==0 || ( isMC==1 && ( lep_truthType[0] == 6 || lep_truthType[0] == 2 ) && ( lep_truthType[1] == 6 || lep_truthType[1] == 2 ) && ( lep_isChFlip[0] == 0 && lep_isChFlip[1] == 0 ) ) )') )
# 2.
# event passes this cut if AT LEAST ONE lepton is !prompt (MCTruthClassifier --> !Iso), and none is charge flip
# (i.e., the !prompt lepton will be ( HF lepton || photon conv || lepton from Dalitz decay || mis-reco jet...)
# --> USED FOR CLOSURE TEST
#
vardb.registerCut( Cut('2Lep_NonPromptEvent', '( isMC==0 || ( isMC==1 && ( ( lep_truthType[0] != 6 && lep_truthType[0] != 2 ) || ( lep_truthType[1] != 6 && lep_truthType[1] != 2 ) ) && ( lep_isChFlip[0] == 0 && lep_isChFlip[1] == 0 ) ) )') )
#
# 3.
# event passes this cut if AT LEAST ONE lepton is charge flip (does not distinguish trident VS charge-misId)
#
vardb.registerCut( Cut('2Lep_ChFlipEvent',   '( isMC==0 || ( isMC==1 && ( lep_isChFlip[0] == 1 || lep_isChFlip[1] == 1 ) ) )') )
# 3a.
# event passes this cut if AT LEAST ONE lepton is (prompt and charge flip) (it will be a charge-misId charge flip)
#
vardb.registerCut( Cut('2Lep_ChFlipPromptEvent',  '( isMC==0 || ( isMC==1 && ( ( lep_isChFlip[0] == 1 && ( lep_truthType[0] == 6 || lep_truthType[0] == 2 ) ) || ( lep_isChFlip[1] == 1 && ( lep_truthType[1] == 6 || lep_truthType[1] == 2 ) ) ) ) )') )
# 3b.
# event passes this cut if AT LEAST ONE object is (!prompt and charge flip and from bremsstrahlung) (this will be a trident charge flip)
#
vardb.registerCut( Cut('2Lep_ChFlipBremEvent', '( isMC==0 || ( isMC==1 && ( ( lep_isChFlip[0] == 1 && lep_isBrem[0] == 1 && ( lep_truthType[0] != 6 && lep_truthType[0] != 2 ) ) || ( lep_isChFlip[1] == 1 && lep_isBrem[1] == 1 && ( lep_truthType[1] != 6 && lep_truthType[1] != 2 ) ) ) ) )') )
# 3c.
# event passes this cut if AT LEAST ONE lepton is (!prompt and charge flip)
#
vardb.registerCut( Cut('2Lep_ChFlipNonPromptEvent', '( isMC==0 || ( isMC==1 && ( ( lep_isChFlip[0] == 1 && ( lep_truthType[0] != 6 && lep_truthType[0] != 2 ) ) || ( lep_isChFlip[1] == 1 && ( lep_truthType[1] != 6 && lep_truthType[1] != 2 ) ) ) ) )') )
# 4.
# event passes this cut if NONE of the leptons is charge flip
vardb.registerCut( Cut('2Lep_ChFlipVeto',   '( isMC==0 || ( isMC==1 && ( lep_isChFlip[0] == 0 && lep_isChFlip[1] == 0 ) ) )') )

# -------------------------------------------------------------------------------

# compute invariant masses on-the-fly

lep0_px = '( lep_pt[0] * TMath::Cos( lep_phi[0] ) )'
lep0_py = '( lep_pt[0] * TMath::Sin( lep_phi[0] ) )'
lep0_pz = '( lep_pt[0] * TMath::SinH( lep_eta[0] ) )'
lep0_E  = '( lep_pt[0] * TMath::CosH( lep_eta[0] ) )'

lep1_px = '( lep_pt[1] * TMath::Cos( lep_phi[1] ) )'
lep1_py = '( lep_pt[1] * TMath::Sin( lep_phi[1] ) )'
lep1_pz = '( lep_pt[1] * TMath::SinH( lep_eta[1] ) )'
lep1_E  = '( lep_pt[1] * TMath::CosH( lep_eta[1] ) )'

# neglecting lepton masses
m_ll = '( TMath::Sqrt( 2*( ' + lep0_E + '*' + lep1_E + '-' + lep0_px + '*' + lep1_px + '-' + lep0_py + '*' + lep1_py + '-' + lep0_pz + '*' + lep1_pz + ' ) ) )'

if args.debug:
    print 'string for invariant mass of a generic lepton pair: ', m_ll

mZCand_sidescut = '( TMath::Abs( ' + m_ll + ' - 91.187e3 ) > 10e3 )'
mZCand_peakcut  = '( TMath::Abs( ' + m_ll + ' - 91.187e3 ) < 30e3 )'

# Powheg Z+jets has a cut at 60 GeV
mZCand_mincut  = '( ' + m_ll + '  > 40e3 )'

if args.debug:
    print 'string for selecting events w/ 2 leptons outside Z peak: ',   mZCand_sidescut
    print 'string for selecting events w/ 2 leptons around Z peak: ',    mZCand_peakcut

vardb.registerCut( Cut('Zsidescut', mZCand_sidescut ) )   # use this to require the 2 leptons to be outside Z peak
vardb.registerCut( Cut('Zpeakcut',  mZCand_peakcut )  )   # use this to require the 2 leptons to be around Z peak
vardb.registerCut( Cut('Zmincut',   mZCand_mincut )   )   # Powheg Z+jets has a cut at 60 GeV

# reconstructed pT of the Z
#
pT_Z = '( TMath::Sqrt( (lep_pt[0]*lep_pt[0]) + (lep_pt[1]*lep_pt[1]) + 2*lep_pt[0]*lep_pt[1]*(TMath::Cos( lep_phi[0] - lep_phi[1] )) ) )/1e3'

# -------------------------------------------------------------------
#  Used for the fake estimate in the 2lepSS and 3lep channel
#
# 'isXY' refers to the SS pair in a 2Lep or trilep event.
#    X is the lepton w/ highest pT of the pair, Y is the second.
#    X,Y = 'L' means that the lepton is ( loose && !tight )
#
#
#  NB: in SR, the TT cut is applied within the ttH2015_Background*.py classes
#      ( except for FakesMM, where the MM weight defines automatically the category )
#  NB: this cut will be used ONLY when looking at 2lep SS or 3lep events!!!
#
# -------------------------------------------------------------------
vardb.registerCut( Cut('TT',  '( isTT == 1 )') )
vardb.registerCut( Cut('TL',  '( isTL == 1 )') )
vardb.registerCut( Cut('LT',  '( isLT == 1 )') )
vardb.registerCut( Cut('LL',  '( isLL == 1 )') )

vardb.registerCut( Cut('TM',  '( isTM == 1 )') )
vardb.registerCut( Cut('MT',  '( isMT == 1 )') )
vardb.registerCut( Cut('MM',  '( isMM == 1 )') )

# ---------------------------
# A list of variables to plot
# ---------------------------

if doSR or doLowNJetCR:
  print ''
  vardb.registerVar( Variable(shortname = 'NJets',	     latexname = 'Jet multiplicity',				 ntuplename = 'njets',  			  bins = 10,  minval = 0,    maxval = 10) )
  vardb.registerVar( Variable(shortname = 'NBJets',	      latexname = 'BJet multiplicity',  			 ntuplename = 'njets_mv2c20_Fix77',		  bins = 4,  minval = 0,     maxval = 4) )
  vardb.registerVar( Variable(shortname = 'Mll01_inc',       latexname = 'm(l_{0}l_{1}) [GeV]',			 ntuplename = 'mll01/1e3',			  bins = 13,  minval = 0.0,  maxval = 260.0,) )
  vardb.registerVar( Variable(shortname = 'Lep0Pt',	      latexname = 'p_{T}^{lead lep} [GeV]',			 ntuplename = 'lep_pt[0]/1e3',  		  bins = 11, minval = 20.0,  maxval = 240.0,) )
  #vardb.registerVar( Variable(shortname = 'Lep0Eta',	      latexname = '|#eta^{lead lep}|',  			 ntuplename = 'TMath::Abs(lep_eta[0])', 	  bins = 8,  minval = 0.0,   maxval = 2.6) )

if doMMRates or doMMClosureRates:
  print ''
  vardb.registerVar( Variable(shortname = 'NJets',	     latexname = 'Jet multiplicity',				 ntuplename = 'njets',  			  bins = 10,  minval = 0,    maxval = 10) )
  vardb.registerVar( Variable(shortname = 'NBJets',	     latexname = 'BJet multiplicity',				 ntuplename = 'njets_mv2c20_Fix77',		  bins = 4,  minval = 0,     maxval = 4) )
if doMMClosureTest:
  print ''
  vardb.registerVar( Variable(shortname = 'NJets',	     latexname = 'Jet multiplicity',				 ntuplename = 'njets',  			  bins = 10,  minval = 0,    maxval = 10) )
  vardb.registerVar( Variable(shortname = 'NBJets',	     latexname = 'BJet multiplicity',				 ntuplename = 'njets_mv2c20_Fix77',		  bins = 4,  minval = 0,     maxval = 4) )
  vardb.registerVar( Variable(shortname = 'Mll01_inc',       latexname = 'm(l_{0}l_{1}) [GeV]',			         ntuplename = 'mll01/1e3',			  bins = 13,  minval = 0.0,  maxval = 260.0,) )

if doStandardPlots:
  print ''
  #vardb.registerVar( Variable(shortname = 'Jet0Pt',	      latexname = 'p_{T}^{lead jet} [GeV]',			ntuplename = 'jet_pt[0]/1e3',			 bins = 36, minval = 20.0,  maxval = 200.0,) )
  #vardb.registerVar( Variable(shortname = 'Jet0Eta',		      latexname = '#eta^{lead jet}',				ntuplename = 'jet_eta[0]',			 bins = 50,  minval = -5.0, maxval = 5.0) )
  #vardb.registerVar( Variable(shortname = 'NJets',	 latexname = 'Jet multiplicity',			   ntuplename = 'njets',			    bins = 10,  minval = 0,    maxval = 10) )
  #vardb.registerVar( Variable(shortname = 'NBJets',	 latexname = 'BJet multiplicity',			   ntuplename = 'njets_mv2c20_Fix77',		    bins = 4,  minval = 0,     maxval = 4) )
  vardb.registerVar( Variable(shortname = 'NJetsPlus10NBJets',   latexname = 'N_{Jets}+10*N_{BJets}',				   ntuplename = 'njets+10.0*njets_mv2c20_Fix77',    bins = 40,  minval = 0,    maxval = 40) )
  #
  # Inclusive m(ll) plot
  #
  #vardb.registerVar( Variable(shortname = 'Mll01_inc',  	 latexname = 'm(l_{0}l_{1}) [GeV]',				   ntuplename = 'mll01/1e3',			    bins = 40, minval = 40.0,  maxval = 240.0,) )
  #
  # Z peak plot
  #
  #vardb.registerVar( Variable(shortname = 'Mll01_peak', 	 latexname = 'm(l_{0}l_{1}) [GeV]',			   ntuplename = 'mll01/1e3',			    bins = 40, minval = 40.0,	maxval = 120.0,) )
  #
  #vardb.registerVar( Variable(shortname = 'pT_Z',	 latexname = 'p_{T} Z (reco) [GeV]',			   ntuplename = pT_Z,				    bins = 100, minval = 0.0,	maxval = 1000.0, logaxisX = True) )
  #
  #vardb.registerVar( Variable(shortname = 'Lep0Pt',		 latexname = 'p_{T}^{lead lep} [GeV]',  		   ntuplename = 'lep_pt[0]/1e3',		    bins = 11, minval = 20.0,  maxval = 240.0,) )
  #vardb.registerVar( Variable(shortname = 'Lep1Pt',		 latexname = 'p_{T}^{2nd lead lep} [GeV]',		   ntuplename = 'lep_pt[1]/1e3',		    bins = 7,  minval = 20.0,  maxval = 160.0,) )
  #vardb.registerVar( Variable(shortname = 'Lep0Eta',		 latexname = '#eta^{lead lep}', 			   ntuplename = 'TMath::Abs(lep_eta[0])',	    bins = 8,  minval = 0.0,   maxval = 2.6) )
  #vardb.registerVar( Variable(shortname = 'Lep1Eta',		 latexname = '#eta^{2nd lead lep}',			   ntuplename = 'TMath::Abs(lep_eta[1])',	    bins = 8,  minval = 0.0,   maxval = 2.6) )

  #vardb.registerVar( Variable(shortname = 'Mll12',		 latexname = 'm(l_{1}l_{2}) [GeV]',			   ntuplename = 'mll12/1e3',			    bins = 15, minval = 0.0,   maxval = 300.0,) )
  #vardb.registerVar( Variable(shortname = 'avgint',			 latexname = 'Average Interactions Per Bunch Crossing',    ntuplename = 'averageInteractionsPerCrossing',   bins = 50, minval = 0,     maxval = 50,  typeval = TH1I) )
  #vardb.registerVar( Variable(shortname = 'MET_FinalClus',	  latexname = 'E_{T}^{miss} (FinalClus) [GeV]', 	   ntuplename = 'metFinalClus/1e3',		    bins = 45, minval = 0.0,   maxval = 180.0,) )
  #vardb.registerVar( Variable(shortname = 'MET_FinalTrk',	 latexname = 'E_{T}^{miss} (FinalTrk) [GeV]',			   ntuplename = 'metFinalTrk/1e3',		    bins = 45, minval = 0.0,   maxval = 180.0,) )
  #vardb.registerVar( Variable(shortname = 'MET_SoftClus',	  latexname = 'E_{T}^{miss} (SoftClus) [GeV]',  		   ntuplename = 'metSoftClus/1e3',		    bins = 45, minval = 0.0,   maxval = 180.0,) )
  #vardb.registerVar( Variable(shortname = 'MET_SoftTrk',	  latexname = 'E_{T}^{miss} (SoftTrk) [GeV]',		   ntuplename = 'metSoftTrk/1e3',		    bins = 45, minval = 0.0,   maxval = 180.0,) )
  #vardb.registerVar( Variable(shortname = 'MET_Electrons',	 latexname = 'E_{T}^{miss} (Electrons) [GeV]',  	   ntuplename = 'metEle/1e3',			    bins = 45, minval = 0.0,   maxval = 180.0,) )
  #vardb.registerVar( Variable(shortname = 'MET_Muons', 	 latexname = 'E_{T}^{miss} (Muons) [GeV]',		   ntuplename = 'metMuons/1e3', 		    bins = 45, minval = 0.0,   maxval = 180.0,) )
  #vardb.registerVar( Variable(shortname = 'MET_Jets',  		 latexname = 'E_{T}^{miss} (Jets) [GeV]',		   ntuplename = 'metJet/1e3',			    bins = 45, minval = 0.0,   maxval = 180.0,) )

  #vardb.registerVar( Variable(shortname = 'MT_Lep0MET',	 latexname = 'm_{T}(l_{0},MET) [GeV]',  		   ntuplename = 'mT_lep0MET/1e3',		    bins = 40, minval = 0.0,   maxval = 160.0,) )
  #vardb.registerVar( Variable(shortname = 'MT_Lep1MET',	 latexname = 'm_{T}(l_{1},MET) [GeV]',  		   ntuplename = 'mT_lep1MET/1e3',		    bins = 40, minval = 0.0,   maxval = 160.0,) )
  #vardb.registerVar( Variable(shortname = 'Tau0Pt',		 latexname = 'p_{T}^{lead tau} [GeV]',  		   ntuplename = 'tau_pt[0]/1e3',		    bins = 30, minval = 25.0,  maxval = 100.0,) )

  #vardb.registerVar( Variable(shortname = 'El0Pt',   latexname = 'p_{T}^{lead e} [GeV]',			ntuplename = 'el_pt[0]/1e3',			 bins = 36, minval = 10.0,  maxval = 190.0,) )
  #vardb.registerVar( Variable(shortname = 'El1Pt',   latexname = 'p_{T}^{2nd lead e} [GeV]',			ntuplename = 'el_pt[1]/1e3',			 bins = 36, minval = 10.0,  maxval = 190.0,) )
  #vardb.registerVar( Variable(shortname = 'El0Eta',  latexname = '#eta^{lead e}',				ntuplename = 'TMath::Abs(el_eta[0])',		 bins = 8,  minval = 0.0,   maxval = 2.6, manualbins = [ 0.0, 0.5, 0.8, 1.1, 1.37, 1.52, 2.0, 2.25, 2.6]) )
  #vardb.registerVar( Variable(shortname = 'El1Eta',  latexname = '#eta^{2nd lead e}',  			ntuplename = 'TMath::Abs(el_eta[1])',		 bins = 8,  minval = 0.0,   maxval = 2.6, manualbins = [ 0.0, 0.5, 0.8, 1.1, 1.37, 1.52, 2.0, 2.25, 2.6]) )
  #vardb.registerVar( Variable(shortname = 'El0TopoEtCone20',     latexname = 'topoetcone20^{lead e} [GeV]',		     ntuplename = 'el_topoetcone20[0]/1e3',	      bins = 40, minval = 0.0,   maxval = 10.0, manualbins = [ 0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.5, 2.0, 2.5, 3.0] ) )
  #vardb.registerVar( Variable(shortname = 'El1TopoEtCone20',	  latexname = 'topoetcone20^{2nd lead e} [GeV]',	    ntuplename = 'el_topoetcone20[1]/1e3',	     bins = 40, minval = 0.0,	maxval = 10.0, manualbins = [ 0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.5, 2.0, 2.5, 3.0] ) )
  #vardb.registerVar( Variable(shortname = 'El0PtVarCone20',	  latexname = 'ptvarcone20^{lead e} [GeV]',		    ntuplename = 'el_ptvarcone20[0]/1e3',	     bins = 40, minval = 1.0,	maxval = 5.0) )
  #vardb.registerVar( Variable(shortname = 'El1PtVarCone20',	  latexname = 'ptvarcone20^{2nd lead e} [GeV]', 	    ntuplename = 'el_ptvarcone20[1]/1e3',	     bins = 40, minval = 1.0,	maxval = 5.0) )
  #vardb.registerVar( Variable(shortname = 'El0TopoEtCone20OverPt', latexname = 'topoetcone20/p_{T} lead e [GeV]',   ntuplename = 'el_topoetcone20[0]/el_pt[0]',  bins = 50, minval = -0.2,  maxval = 0.8) )
  #vardb.registerVar( Variable(shortname = 'El1TopoEtCone20OverPt', latexname = 'topoetcone20/p_{T} 2nd lead e [GeV]',    ntuplename = 'el_topoetcone20[1]/el_pt[1]',  bins = 50, minval = -0.2,  maxval = 0.8) )
  #vardb.registerVar( Variable(shortname = 'El0PtVarCone20OverPt',  latexname = 'ptvarcone20/p_{T} lead e [GeV]',    ntuplename = 'el_ptvarcone20[0]/el_pt[0]',   bins = 50, minval = 0.0,  maxval = 1.0) )
  #vardb.registerVar( Variable(shortname = 'El1PtVarCone20OverPt',  latexname = 'ptvarcone20/p_{T} 2nd lead e [GeV]',	 ntuplename = 'el_ptvarcone20[1]/el_pt[1]',  bins = 50, minval = 0.0,  maxval = 1.0) )
  #vardb.registerVar( Variable(shortname = 'El0d0sig',        latexname = '|d_{0}^{sig}| lead e',			ntuplename = 'el_trkd0sig[0]',  		 bins = 40, minval = 0.0,  maxval = 10.0,) )
  #vardb.registerVar( Variable(shortname = 'El1d0sig',        latexname = '|d_{0}^{sig}| 2nd lead e',			ntuplename = 'el_trkd0sig[1]',  		 bins = 40, minval = 0.0,  maxval = 10.0,) )
  #vardb.registerVar( Variable(shortname = 'El0z0sintheta',  latexname = 'z_{0}*sin(#theta) lead e [mm]',		ntuplename = 'el_trkz0sintheta[0]',		 bins = 20, minval = -1.0,  maxval = 1.0,) )
  #vardb.registerVar( Variable(shortname = 'El1z0sintheta',  latexname = 'z_{0}*sin(#theta) 2nd lead e [mm]',		ntuplename = 'el_trkz0sintheta[1]',		 bins = 20, minval = -1.0,  maxval = 1.0,) )
  #vardb.registerVar( Variable(shortname = 'El0LHTight',	 latexname = 'lead e IsLHTight',			   ntuplename = 'el_LHTight[0]',		    bins = 2, minval = -0.5,  maxval = 1.5,) )
  #vardb.registerVar( Variable(shortname = 'El1LHTight',	latexname = '2nd lead e IsLHTight',			  ntuplename = 'el_LHTight[1]', 		   bins = 2, minval = -0.5,  maxval = 1.5,) )
  #vardb.registerVar( Variable(shortname = 'El0isTag',  	latexname = 'lead e IsTag',	   ntuplename = 'el_isTag[0]',  	  bins = 2, minval = -0.5,  maxval = 1.5,) )
  #vardb.registerVar( Variable(shortname = 'El1isTag',  	latexname = '2nd lead e IsTag',    ntuplename = 'el_isTag[1]',  	  bins = 2, minval = -0.5,  maxval = 1.5,) )

  #vardb.registerVar( Variable(shortname = 'Mu0Pt',    latexname = 'p_{T}^{lead #mu} [GeV]',			 ntuplename = 'muon_pt[0]/1e3', 		  bins = 36, minval = 10.0,  maxval = 190.0,) )
  #vardb.registerVar( Variable(shortname = 'Mu1Pt',    latexname = 'p_{T}^{2nd lead #mu} [GeV]',		 ntuplename = 'muon_pt[1]/1e3', 		  bins = 36, minval = 10.0,  maxval = 190.0,) )
  #vardb.registerVar( Variable(shortname = 'Mu0Eta',	       latexname = '#eta^{lead #mu}',				 ntuplename = 'muon_eta[0]',			  bins = 16,  minval = -2.6, maxval = 2.6,) )
  #vardb.registerVar( Variable(shortname = 'Mu1Eta',	       latexname = '#eta^{2nd lead #mu}',			 ntuplename = 'muon_eta[1]',			  bins = 16,  minval = -2.6, maxval = 2.6,) )
  #vardb.registerVar( Variable(shortname = 'Mu0TopoEtCone20',    latexname = 'topoetcone20^{lead #mu} [GeV]',  	    ntuplename = 'muon_topoetcone20[0]/1e3',	     bins = 40, minval = 0.0,	maxval = 10.0, manualbins = [ 0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.5, 2.0, 2.5, 3.0]) )
  #vardb.registerVar( Variable(shortname = 'Mu1TopoEtCone20',	 latexname = 'topoetcone20^{2nd lead #mu} [GeV]',	   ntuplename = 'muon_topoetcone20[1]/1e3',	    bins = 40, minval = 0.0,   maxval = 10.0, manualbins = [ 0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.5, 2.0, 2.5, 3.0]) )
  #vardb.registerVar( Variable(shortname = 'Mu0PtVarCone30',	 latexname = 'ptvarcone20^{lead #mu} [GeV]',		   ntuplename = 'muon_ptvarcone30[0]/1e3',	    bins = 40, minval = 1.0,   maxval = 5.0) )
  #vardb.registerVar( Variable(shortname = 'Mu1PtVarCone30',	 latexname = 'ptvarcone20^{2nd lead #mu} [GeV]',	   ntuplename = 'muon_ptvarcone30[1]/1e3',	    bins = 40, minval = 1.0,   maxval = 5.0) )
  #vardb.registerVar( Variable(shortname = 'Mu0TopoEtCone20OverPt', latexname = 'topoetcone20/p_{T} lead #mu [GeV]',	   ntuplename = 'muon_topoetcone20[0]/muon_pt[0]',    bins = 50, minval = -0.2,  maxval = 0.8) )
  #vardb.registerVar( Variable(shortname = 'Mu1TopoEtCone20OverPt', latexname = 'topoetcone20/p_{T} 2nd lead #mu [GeV]',    ntuplename = 'muon_topoetcone20[1]/muon_pt[1]',    bins = 50, minval = -0.2,  maxval = 0.8) )
  #vardb.registerVar( Variable(shortname = 'Mu0PtVarCone30OverPt',  latexname = 'ptvarcone30/p_{T} lead #mu [GeV]',	   ntuplename = 'muon_ptvarcone30[0]/muon_pt[0]',     bins = 50, minval = 0.0,  maxval = 1.0) )
  #vardb.registerVar( Variable(shortname = 'Mu1PtVarCone30OverPt',  latexname = 'ptvarcone30/p_{T} 2nd lead #mu [GeV]',     ntuplename = 'muon_ptvarcone30[1]/muon_pt[1]',     bins = 50, minval = 0.0,  maxval = 1.0) )
  #vardb.registerVar( Variable(shortname = 'Mu0d0sig',  	 latexname = '|d_{0}^{sig}| lead #mu',  		   ntuplename = 'muon_trkd0sig[0]',		    bins = 40, minval = 0.0,  maxval = 10.0,) )
  #vardb.registerVar( Variable(shortname = 'Mu1d0sig',  	 latexname = '|d_{0}^{sig}| 2nd lead #mu',		   ntuplename = 'muon_trkd0sig[1]',		    bins = 40, minval = 0.0,  maxval = 10.0,) )
  #vardb.registerVar( Variable(shortname = 'Mu0z0sintheta',	 latexname = 'z_{0}*sin(#theta) lead #mu [mm]', 	    ntuplename = 'muon_trkz0sintheta[0]',	     bins = 20, minval = -1.0,  maxval = 1.0,) )
  #vardb.registerVar( Variable(shortname = 'Mu1z0sintheta',   latexname = 'z_{0}*sin(#theta) 2nd lead #mu [mm]',	 ntuplename = 'muon_trkz0sintheta[1]',  	  bins = 20, minval = -1.0,  maxval = 1.0,) )
  #vardb.registerVar( Variable(shortname = 'Mu0isTag', 	  latexname = 'lead #mu IsTag',        ntuplename = 'muon_isTag[0]',	    bins = 2, minval = -0.5,  maxval = 1.5,) )
  #vardb.registerVar( Variable(shortname = 'Mu1isTag',  	 latexname = '2nd lead #mu IsTag',    ntuplename = 'muon_isTag[1]',	   bins = 2, minval = -0.5,  maxval = 1.5,) )

# -------------------------------------------------
# Alterantive ranges and binning for the histograms
# -------------------------------------------------
midstatsbin = {
    'MMC': (25, 0., 250.),
    'mvis': (25, 0., 250.),
    'mT': (30, 0., 120.),
    'MET': (25, 0., 100.),
    'leppt': (30, 17., 77.),
    'taupt': (25, 20., 70.),
    'jetpt': (25, 25., 125.),
}
lowstatsbin = {
    'MMC': (12, 0., 240.),
    'mvis': (12, 0., 240.),
    'mT': (12, 0., 120.),
    'MET': (12, 0., 120.),
    'leppt': (12, 17., 77.),
    'taupt': (12, 20., 80.),
    'jetpt': (12, 25., 121.),
}

# ---------------------
# A list of systematics
# ---------------------
if args.doSyst:
    # if doTwoLepSR or doTwoLepLowNJetCR or dottWCR:
    #	 vardb.registerSystematics( Systematics(name='CFsys',	   eventweight='sys_weight_CF_') ) ## uncertainties on the kfactors used to normalize the various MC distributions
    if doMM:
        #vardb.registerSystematics( Systematics(name='MMrsys',	   eventweight='sys_weight_MMr_') )
    	#vardb.registerSystematics( Systematics(name='MMfsys',	   eventweight='sys_weight_MMf_') )
        vardb.registerSystematics( Systematics(name='MMrsys',	   eventweight='MMWeight') )
    	vardb.registerSystematics( Systematics(name='MMfsys',	   eventweight='MMWeight') )
    if doFF:
    	#vardb.registerSystematics( Systematics(name='FFsys',	   eventweight='sys_weight_FF_') )
    	vardb.registerSystematics( Systematics(name='FFsys',	   eventweight='FFWeight') )

    '''
    vardb.registerSystematics( Systematics(name='PU',		  eventweight='evtsel_sys_PU_rescaling_') )
    vardb.registerSystematics( Systematics(name='el_reco',	  eventweight='evtsel_sys_sf_el_reco_') )
    vardb.registerSystematics( Systematics(name='el_id',	  eventweight='evtsel_sys_sf_el_id_') )
    vardb.registerSystematics( Systematics(name='el_iso',	  eventweight='evtsel_sys_sf_el_iso_') )
    vardb.registerSystematics( Systematics(name='mu_id',	  eventweight='evtsel_sys_sf_mu_id_') )
    vardb.registerSystematics( Systematics(name='mu_iso',	  eventweight='evtsel_sys_sf_mu_iso_') )
    vardb.registerSystematics( Systematics(name='lep_trig',	  eventweight='evtsel_sys_sf_lep_trig_') )
    vardb.registerSystematics( Systematics(name='bjet_b',	  eventweight='evtsel_sys_sf_bjet_b_') )
    vardb.registerSystematics( Systematics(name='bjet_c',	  eventweight='evtsel_sys_sf_bjet_c_') )
    vardb.registerSystematics( Systematics(name='bjet_m',	  eventweight='evtsel_sys_sf_bjet_m_') )

    vardb.registerSystematics( Systematics(name='METSys',	  treename='METSys') )
    vardb.registerSystematics( Systematics(name='ElEnResSys',	  treename='ElEnResSys') )
    vardb.registerSystematics( Systematics(name='ElES_LowPt',	  treename='ElES_LowPt') )
    vardb.registerSystematics( Systematics(name='ElES_Zee',	  treename='ElES_Zee') )
    vardb.registerSystematics( Systematics(name='ElES_R12',	  treename='ElES_R12') )
    vardb.registerSystematics( Systematics(name='ElES_PS',	  treename='ElES_PS') )
    vardb.registerSystematics( Systematics(name='EESSys',	  treename='EESSys') )
    vardb.registerSystematics( Systematics(name='MuSys',	  treename='MuSys') )
    vardb.registerSystematics( Systematics(name='JES_Total',	  treename='JES_Total') )
    vardb.registerSystematics( Systematics(name='JER',  	  treename='JER') )
    '''
# -------------------------------------------------------------------
# Definition of the categories for which one wants produce histograms
# -------------------------------------------------------------------

# ------------
# SRs
# ------------
if doTwoLepSR :

    # when using MM or FF for non-prompt bkg estimate, make sure you plot
    # only pure prompt MC (to avoid double counting of fake background events!)
    #
    if ( args.fakeMethod == 'MM' or args.fakeMethod == 'FF' ):
	 # MuMu region
	 #
	 vardb.registerCategory( MyCategory('MuMuSS_SR_DataDriven',  cut = vardb.getCuts(['TrigDec', 'TrigMatch', 'NBJet', '2Lep', 'SS', 'MuMu_Event', '2Lep_PurePromptEvent', 'NJet2L']) ) )     # 'TauVeto',
	 # OF region
	 #
	 vardb.registerCategory( MyCategory('OFSS_SR_DataDriven',    cut = vardb.getCuts(['TrigDec', 'TrigMatch', 'NBJet', '2Lep', 'SS', 'OF_Event', '2Lep_PurePromptEvent', 'OF_ElEtaCut', 'NJet2L']) ) )      # 'TauVeto',
	 # ElEl region
	 #
	 vardb.registerCategory( MyCategory('ElElSS_SR_DataDriven',  cut = vardb.getCuts(['TrigDec', 'TrigMatch', 'NBJet', '2Lep', 'SS', 'ElEl_Event', '2Lep_PurePromptEvent', 'TrigMatch', 'SF_ElEtaCut', 'NJet2L']) ) )   # 'TauVeto',

    else:
         vardb.registerCategory( MyCategory('MuMuSS_SR',             cut = vardb.getCuts(['TrigDec', 'TrigMatch', 'NBJet', '2Lep', 'SS', 'MuMu_Event', 'TauVeto',  	         'NJet2L']) ) )
         vardb.registerCategory( MyCategory('OFSS_SR',		     cut = vardb.getCuts(['TrigDec', 'TrigMatch', 'NBJet', '2Lep', 'SS', 'OF_Event',   'TauVeto', 'OF_ElEtaCut', 'NJet2L']) ) )
         vardb.registerCategory( MyCategory('ElElSS_SR',	     cut = vardb.getCuts(['TrigDec', 'TrigMatch', 'NBJet', '2Lep', 'SS', 'ElEl_Event', 'TauVeto', 'SF_ElEtaCut', 'NJet2L']) ) )
         #
	 # 2lep+tau region
	 #
	 vardb.registerCategory( MyCategory('TwoLepSSTau_SR',        cut = vardb.getCuts(['NBJet', '2LepTau', 'SS', 'NJet2L', 'OneTau', 'TrigMatch', 'Zsidescut']) ) )

if doThreeLepSR:
    vardb.registerCategory( MyCategory('ThreeLep_SR',    cut = vardb.getCuts(['TrigDec', 'TrigMatch', 'NBJet', '3Lep', 'Zsidescut', 'NJet3L']) ) )

if doFourLepSR:
    vardb.registerCategory( MyCategory('FourLep_SR',     cut = vardb.getCuts(['TrigDec', 'TrigMatch', 'NBJet', '4Lep', 'NJet4L']) ) )

# -------------
# low N-jet CRs
# -------------
if doTwoLepLowNJetCR :

    if ( args.fakeMethod == 'MM' or args.fakeMethod == 'FF' ):
	 # MuMu region
	 #
	 vardb.registerCategory( MyCategory('MuMuSS_LowNJetCR_DataDriven',    cut = vardb.getCuts(['TrigDec', 'TrigMatch', 'NBJet', '2Lep', 'SS', 'MuMu_Event', '2Lep_PurePromptEvent', 'LowJetCR']) ) )   # 'TauVeto',
	 # OF region
	 #
	 vardb.registerCategory( MyCategory('OFSS_LowNJetCR_DataDriven',      cut = vardb.getCuts(['TrigDec', 'TrigMatch', 'NBJet', '2Lep', 'SS', 'OF_Event', '2Lep_PurePromptEvent', 'OF_ElEtaCut', 'LowJetCR']) ) )    # 'TauVeto',
	 # ElEl region
	 #
	 vardb.registerCategory( MyCategory('ElElSS_LowNJetCR_DataDriven',    cut = vardb.getCuts(['TrigDec', 'TrigMatch', 'NBJet', '2Lep', 'SS', 'ElEl_Event', '2Lep_PurePromptEvent', 'TrigMatch', 'SF_ElEtaCut', 'LowJetCR']) ) ) # 'TauVeto',

    else:
    	 vardb.registerCategory( MyCategory('MuMuSS_LowNJetCR',	     cut = vardb.getCuts(['TrigDec', 'TrigMatch', 'NBJet', '2Lep',    'SS', 'MuMu_Event', 'TauVeto',                 'LowJetCR']) ) )
    	 vardb.registerCategory( MyCategory('OFSS_LowNJetCR',	     cut = vardb.getCuts(['TrigDec', 'TrigMatch', 'NBJet', '2Lep',    'SS', 'OF_Event',   'TauVeto',  'OF_ElEtaCut', 'LowJetCR']) ) )
    	 vardb.registerCategory( MyCategory('ElElSS_LowNJetCR',	     cut = vardb.getCuts(['TrigDec', 'TrigMatch', 'NBJet', '2Lep',    'SS', 'ElEl_Event', 'TauVeto',  'SF_ElEtaCut', 'LowJetCR']) ) )
	 vardb.registerCategory( MyCategory('TwoLepSSTau_LowNJetCR', cut = vardb.getCuts(['TrigDec', 'TrigMatch', 'NBJet', '2LepTau', 'SS',               'OneTau',   'Zsidescut',   'LowJetCR']) ) )

if doThreeLepLowNJetCR:
    # take OS pairs
    #
    vardb.registerCategory( MyCategory('ThreeLep_LowNJetCR',   cut = ( vardb.getCuts(['TrigDec', 'TrigMatch', 'NBJet', '3Lep', 'LowJetCR','ZOSsidescut']) & -vardb.getCut('SS') ) ) )

# -------------
# other CRs
# -------------

if doWZonCR:
    vardb.registerCategory( MyCategory('WZonCR',      cut = ( vardb.getCuts(['TrigDec', 'TrigMatch', 'BJetVeto',   '3Lep',  		  'Zpeakcut'])  & -vardb.getCut('SS') ) ) )

if doWZoffCR:
    vardb.registerCategory( MyCategory('WZoffCR',     cut = ( vardb.getCuts(['TrigDec', 'TrigMatch', 'BJetVeto',   '3Lep',  		  'Zsidescut']) & -vardb.getCut('SS') ) ) )

if doWZHFonCR:
    vardb.registerCategory( MyCategory('WZHFonCR',    cut = ( vardb.getCuts(['TrigDec', 'TrigMatch', 'NBJet',      '3Lep',  		  'Zpeakcut'])  & -vardb.getCut('SS') ) ) )

if doWZHFoffCR:
    vardb.registerCategory( MyCategory('WZHFoffCR',   cut = ( vardb.getCuts(['TrigDec', 'TrigMatch', 'NBJet',      '3Lep',  		  'Zsidescut']) & -vardb.getCut('SS') ) ) )

if dottZCR:
    vardb.registerCategory( MyCategory('ttZCR',       cut = ( vardb.getCuts(['TrigDec', 'TrigMatch', 'NBJet',      '3Lep',   'NJet3L',    'Zpeakcut'])  & -vardb.getCut('SS') ) ) )

if dottWCR:
    #vardb.registerCategory( MyCategory('ttWCR',       cut =   vardb.getCuts(['TrigDec', 'TrigMatch', 'LargeNBjet', '2Lep',  'LowJetCR',  'TauVeto', 'SS']) ) )
    vardb.registerCategory( MyCategory('ttWCR',       cut = vardb.getCuts(['TrigDec', 'TrigMatch', 'LowJetCR', 'LargeNBJet', '2LepRelaxed', 'TauVeto']) ) )
    vardb.registerCategory( MyCategory('ttWCR_TT',    cut = vardb.getCuts(['TrigDec', 'TrigMatch', 'LowJetCR', 'LargeNBJet', '2LepRelaxed', 'TauVeto', 'TightLeptons_2Lep']) ) )

if doZSSpeakCR:
    vardb.registerCategory( MyCategory('ZSSpeakCR_ElEl',   cut = vardb.getCuts(['TrigDec', 'TrigMatch', '2Lep', 'SS', 'ElEl_Event', 'Zpeakcut', 'SF_ElEtaCut']) ) )
    vardb.registerCategory( MyCategory('ZSSpeakCR_MuMu',   cut = vardb.getCuts(['TrigDec', 'TrigMatch', '2Lep', 'SS', 'MuMu_Event', 'Zpeakcut']) ) )

# ------------------------------------
# Special CR for Data/MC control plots
# ------------------------------------

if doDataMCCR:

    # ----------------------------------------------------
    # Inclusive OS dilepton (ee,mumu)
    #
    # for v022, nbjet cut is dummy
    #
    # 1.)  mumu
    #
    vardb.registerCategory( MyCategory('DataMC_InclusiveOS_MuMu',          cut = ( vardb.getCuts(['2LepRelaxed', 'TrigDec', 'TrigMatch', 'MuMu_Event', 'NBJet', 'Zmincut']) & -vardb.getCut('SS') ) ) )
    # this is the Real CR
    #vardb.registerCategory( MyCategory('DataMC_MuMu_RealCR',              cut = ( vardb.getCuts(['2Lep', 'TrigDec', 'TrigMatch', 'MuMu_Event', 'NBJet', 'LowJetCR']) & -vardb.getCut('SS') ) ) )
    # this is the Fake CR
    #vardb.registerCategory( MyCategory('DataMC_MuMu_FakeCR',              cut = vardb.getCuts(['2Lep', 'TrigDec', 'TrigMatch', 'MuMu_Event', 'NBJet', 'LowJetCR', 'SS'])  ) )
    #
    # 2.) elel
    #
    vardb.registerCategory( MyCategory('DataMC_InclusiveOS_ElEl',          cut = ( vardb.getCuts(['2LepRelaxed', 'TrigDec', 'TrigMatch', 'ElEl_Event', 'NBJet', 'Zmincut']) & -vardb.getCut('SS') ) ) )
    # this is the Real CR
    #vardb.registerCategory( MyCategory('DataMC_ElEl_RealCR',              cut = ( vardb.getCuts(['2Lep', 'TrigDec', 'TrigMatch', 'ElEl_Event', 'NBJet', 'LowJetCR']) & -vardb.getCut('SS') ) ) )
    # this is the Fake CR
    #vardb.registerCategory( MyCategory('DataMC_ElEl_FakeCR',              cut = vardb.getCuts(['2Lep', 'TrigDec', 'TrigMatch', 'ElEl_Event', 'NBJet', 'LowJetCR', 'SS'])  ) )

    # ----------------------------------------------------
    # OS ttbar ( top dilepton) (ee,mumu,emu)
    #
    #vardb.registerCategory( MyCategory('DataMC_OS_ttbar', 	          cut = vardb.getCuts(['2LepRelaxed', 'TrigDec', 'TrigMatch', 'NJet4L', 'NBJet', 'Zsidescut']) & -vardb.getCut('SS') ) )
    # this is the Real CR
    #vardb.registerCategory( MyCategory('DataMC_OF_RealCR', 	          cut = vardb.getCuts(['2Lep', 'TrigDec', 'TrigMatch', 'OF_Event','NBJet', 'LowJetCR']) & -vardb.getCut('SS') ) )

# ----------------------------------------------
# CRs where r/f rates for MM method are measured
# ----------------------------------------------

# ---------------------------------------------------------------
#  electron(muon) REAL rate measurement region:
#
#  -) OS
#  -) elel(mumu) || OF (where the electron(muon) is the probe)
#
#  electron(muon) FAKE rate measurement region:
#  -) SS
#  -) elel(mumu) || OF (where the electron(muon) is the probe)
#
#   NB: for MC samples we want to plot only the prompt (i.e., the prompt ch-flip? needs reviewing!!) contribution
#      (i.e, what will be subtracted to measure FAKE rate)
#
# Side note:
#	in these events, there is by construction only one probe
#	lepton and one tag lepton.
#	The vectorial-component notation 'el_probe_*[0]' is kept only
#	for consistency with the other sections of the code.
#
# ---------------------------------------------------------------
if doMMRates or doMMClosureRates:

    vardb.registerCut( Cut('ElRealFakeRateCR',	'( isProbeElEvent == 1 )') )
    vardb.registerCut( Cut('ElProbeTight',      '( el_probe_isTightSelected[0] == 1 )') )
    vardb.registerCut( Cut('ElProbeAntiTight',  '( el_probe_isTightSelected[0] == 0 )') )
    #vardb.registerCut( Cut('ElProbeAntiTight',  '( el_probe_isMediumSelected[0] == 0 )') )

    vardb.registerCut( Cut('MuRealFakeRateCR',	'( isProbeMuEvent == 1 )') )
    vardb.registerCut( Cut('MuProbeTight',      '( muon_probe_isTightSelected[0] == 1 )') )
    vardb.registerCut( Cut('MuProbeAntiTight',  '( muon_probe_isTightSelected[0] == 0 )') )
    #vardb.registerCut( Cut('MuProbeAntiTight',  '( muon_probe_isMediumSelected[0] == 0 )') )

    # -----------------------------------------------------------------------------------------------------------------
    # want the tag lepton to be always trigger matched
    vardb.registerCut( Cut('LepTagTrigMatched', '( lep_tag_isTrigMatched[0] == 1 && ( ( lep_tag_flavour[0] == 11 && lep_tag_pt[0] > 25e3 ) || ( lep_tag_flavour[0] == 13 && lep_tag_pt[0] > 22e3 ) ) )') )

    # NB:
    # To reduce charge flip contamination, in the FAKE CR require the tag electron eta < 1.37 (in regions where there is a tag electron)
    # and for FAKE el region, additionally require the SS leptons to be outside Z peak (+- 10 GeV)
    #
    vardb.registerCut( Cut('ElTagEtaCut_ProbeElEvent', '( nel == 1 || ( nel == 2 && TMath::Abs(el_tag_eta[0]) < 1.37 ) )') )
    vardb.registerCut( Cut('ElTagEtaCut_ProbeMuEvent', '( nel == 0 || ( nel == 1 && TMath::Abs(el_tag_eta[0]) < 1.37 ) )') )

    # define regions with at least one muon/electron
    #
    mu_region = ( vardb.getCut('MuMu_Event') | vardb.getCut('OF_Event') )
    el_region = ( vardb.getCut('ElEl_Event') | vardb.getCut('OF_Event') )

    # ---------------------------------------
    # Special plots for MM real/fake rate CRs
    # ---------------------------------------

    #vardb.registerVar( Variable(shortname = 'ElTagPt',     latexname = 'p_{T}^{tag e} [GeV]',	  ntuplename = 'el_tag_pt[0]/1e3',		  bins = 90,  minval = 25.0, maxval = 205.0,) )
    #vardb.registerVar( Variable(shortname = 'ElTagEta',    latexname = '#eta^{tag e}',  	  ntuplename = 'TMath::Abs( el_tag_eta[0] )',	  bins = 8,   minval = 0.0,  maxval = 2.6, manualbins = [ 0.0 , 0.5 , 0.8 , 1.1 , 1.37 , 1.52 , 2.0 , 2.25 , 2.6]) )
    vardb.registerVar( Variable(shortname = 'ElProbePt',   latexname = 'p_{T}^{probe e} [GeV]',   ntuplename = 'el_probe_pt[0]/1e3',		  bins = 90,  minval = 25.0, maxval = 205.0,) ) #maxval = 310.0,) )
    vardb.registerVar( Variable(shortname = 'ElProbeEta',  latexname = '#eta^{probe e}',	  ntuplename = 'TMath::Abs( el_probe_eta[0] )',   bins = 8,   minval = 0.0,  maxval = 2.6, manualbins = [ 0.0 , 0.5 , 0.8 , 1.1 , 1.37 , 1.52 , 2.0 , 2.25 , 2.6]) )

    #vardb.registerVar( Variable(shortname = 'MuTagPt',     latexname = 'p_{T}^{tag #mu} [GeV]',   ntuplename = 'muon_tag_pt[0]/1e3',		  bins = 90, minval = 25.0,  maxval = 205.0,) )
    #vardb.registerVar( Variable(shortname = 'MuTagEta',    latexname = '#eta^{tag #mu}',	  ntuplename = 'TMath::Abs( muon_tag_eta[0] )',   bins = 8,  minval = 0.0,   maxval = 2.5, manualbins = [ 0.0 , 0.1 , 0.4 , 0.7, 1.0,  1.3 , 1.6 , 1.9, 2.2, 2.5 ]) )
    vardb.registerVar( Variable(shortname = 'MuProbePt',   latexname = 'p_{T}^{probe #mu} [GeV]', ntuplename = 'muon_probe_pt[0]/1e3',		  bins = 90, minval = 25.0,  maxval = 205.0) ) # maxval = 310.0,) )
    vardb.registerVar( Variable(shortname = 'MuProbeEta',  latexname = '#eta^{probe #mu}',	  ntuplename = 'TMath::Abs( muon_probe_eta[0] )', bins = 8,  minval = 0.0,   maxval = 2.5, manualbins = [ 0.0 , 0.1 , 0.4 , 0.7, 1.0,  1.3 , 1.6 , 1.9, 2.2, 2.5 ]) )

    # -----------------------------------------------------------------------------------------------------------------
    # Prompt/ch-flip subtraction in Fake SS CR: make sure you only plot:
    #
    # ---> to account for ttV: use '2Lep_PurePromptEvent' (this does not take into account charge flips!)
    #	OR
    # ---> to account for charge flip background : use '2Lep_ChFlipEvent'
    #
    truth_sub_SS = ( vardb.getCut('2Lep_PurePromptEvent') | vardb.getCut('2Lep_ChFlipEvent') )
    truth_sub_OS = ( vardb.getCut('DummyCut') )

    # Use this when extracting FAKE rates from simulation, or if doing MMClosure (--> use MC events w/ at least 1 non-prompt, but veto charge flips)
    # Use this when extracting REAL rates from simulation, or if doing MMClosure (--> use MC events w/ only prompt leptons, and veto on charge flips)
    #
    if ( doMMClosureRates or args.ratesFromMC ) :

       if doMMClosureRates:
          print '*********************************\n Doing MMClosure : looking at ttbar only! \n*********************************'
       elif args.ratesFromMC:
          print '*********************************\n Measuring rates from MC simulation! \n*********************************'

       truth_sub_SS = ( vardb.getCut('2Lep_NonPromptEvent') ) # --> if tag/probe assignment has been done w/ truth, then the probe will be automatically a !prompt and not charge flip (DEFAULT)
       truth_sub_OS = ( vardb.getCut('2Lep_PurePromptEvent') )
       if ( args.doChFlipRate ):
          print '*********************************\nMEASURING CHARGE FLIP RATE IN MC\n*********************************'
          truth_sub_SS = vardb.getCut('2Lep_ChFlipEvent')     # --> if tag/probe assignment has been done w/ truth, then the probe will be automatically a charge flip

    # elctron/muon R/F region(s)
    #

    # combine OF + SF
    vardb.registerCategory( MyCategory('FakeCRMuL',    cut = ( vardb.getCuts(['TrigDec',  'LepTagTrigMatched',  'NBJet', '2Lep', 'SS', 'LowJetCR', 'MuRealFakeRateCR',  'ElTagEtaCut_ProbeMuEvent',  'MuProbeAntiTight']) & mu_region & truth_sub_SS ) ) )
    vardb.registerCategory( MyCategory('FakeCRMuT',    cut = ( vardb.getCuts(['TrigDec',  'LepTagTrigMatched',  'NBJet', '2Lep', 'SS', 'LowJetCR', 'MuRealFakeRateCR',  'ElTagEtaCut_ProbeMuEvent',  'MuProbeTight'    ]) & mu_region & truth_sub_SS ) ) )
    vardb.registerCategory( MyCategory('RealCRMuL',    cut = ( vardb.getCuts(['TrigDec',  'LepTagTrigMatched',  'NBJet', '2Lep',       'LowJetCR', 'MuRealFakeRateCR',  			     'MuProbeAntiTight']) & mu_region & truth_sub_OS & -vardb.getCut('SS') ) ) )
    vardb.registerCategory( MyCategory('RealCRMuT',    cut = ( vardb.getCuts(['TrigDec',  'LepTagTrigMatched',  'NBJet', '2Lep',       'LowJetCR', 'MuRealFakeRateCR',  			     'MuProbeTight'    ]) & mu_region & truth_sub_OS & -vardb.getCut('SS') ) ) )
    #
    vardb.registerCategory( MyCategory('FakeCRElL',    cut = ( vardb.getCuts(['TrigDec', 'LepTagTrigMatched',  'NBJet', '2Lep', 'SS', 'LowJetCR', 'ElRealFakeRateCR',  'ElTagEtaCut_ProbeElEvent',  'ElProbeAntiTight', 'Zsidescut']) & el_region & truth_sub_SS ) ) )
    vardb.registerCategory( MyCategory('FakeCRElT',    cut = ( vardb.getCuts(['TrigDec', 'LepTagTrigMatched',  'NBJet', '2Lep', 'SS', 'LowJetCR', 'ElRealFakeRateCR',  'ElTagEtaCut_ProbeElEvent',  'ElProbeTight',     'Zsidescut']) & el_region & truth_sub_SS ) ) )
    vardb.registerCategory( MyCategory('RealCRElL',    cut = ( vardb.getCuts(['TrigDec', 'LepTagTrigMatched',  'NBJet', '2Lep',       'LowJetCR', 'ElRealFakeRateCR',				    'ElProbeAntiTight'		  ]) & truth_sub_OS & el_region & -vardb.getCut('SS') ) ) )
    vardb.registerCategory( MyCategory('RealCRElT',    cut = ( vardb.getCuts(['TrigDec', 'LepTagTrigMatched',  'NBJet', '2Lep',       'LowJetCR', 'ElRealFakeRateCR',				    'ElProbeTight'		  ]) & truth_sub_OS & el_region & -vardb.getCut('SS') ) ) )

    # SF only
    vardb.registerCategory( MyCategory('MuMuFakeCRMuL',  cut =   vardb.getCuts(['TrigDec',  'LepTagTrigMatched',  'NBJet', '2Lep', 'SS', 'LowJetCR', 'MuRealFakeRateCR', 			      'MuProbeAntiTight',      'MuMu_Event']) & truth_sub_SS ) )
    vardb.registerCategory( MyCategory('MuMuFakeCRMuT',  cut =   vardb.getCuts(['TrigDec',  'LepTagTrigMatched',  'NBJet', '2Lep', 'SS', 'LowJetCR', 'MuRealFakeRateCR', 			      'MuProbeTight',          'MuMu_Event']) & truth_sub_SS ) )
    vardb.registerCategory( MyCategory('MuMuRealCRMuL',  cut = ( vardb.getCuts(['TrigDec',  'LepTagTrigMatched',  'NBJet', '2Lep',       'LowJetCR', 'MuRealFakeRateCR',			      'MuProbeAntiTight', 'MuMu_Event']) & truth_sub_OS & -vardb.getCut('SS') ) ) )
    vardb.registerCategory( MyCategory('MuMuRealCRMuT',  cut = ( vardb.getCuts(['TrigDec',  'LepTagTrigMatched',  'NBJet', '2Lep',       'LowJetCR', 'MuRealFakeRateCR',			      'MuProbeTight',	  'MuMu_Event']) & truth_sub_OS & -vardb.getCut('SS') ) ) )
    #
    """
    vardb.registerCategory( MyCategory('ElElFakeCRElL',  cut =   vardb.getCuts(['TrigDec', 'LepTagTrigMatched',  'NBJet', '2Lep', 'SS', 'LowJetCR', 'ElRealFakeRateCR',  'ElTagEtaCut_ProbeElEvent',  'ElProbeAntiTight', 'ElEl_Event', 'Zsidescut']) & truth_sub_SS ) )
    vardb.registerCategory( MyCategory('ElElFakeCRElT',  cut =   vardb.getCuts(['TrigDec', 'LepTagTrigMatched',  'NBJet', '2Lep', 'SS', 'LowJetCR', 'ElRealFakeRateCR',  'ElTagEtaCut_ProbeElEvent',  'ElProbeTight', 	 'ElEl_Event', 'Zsidescut']) & truth_sub_SS ) )
    vardb.registerCategory( MyCategory('ElElRealCRElL',  cut = ( vardb.getCuts(['TrigDec', 'LepTagTrigMatched',  'NBJet', '2Lep',	  'LowJetCR', 'ElRealFakeRateCR',			     'ElProbeAntiTight', 'ElEl_Event'		  ]) & truth_sub_OS & -vardb.getCut('SS') ) ) )
    vardb.registerCategory( MyCategory('ElElRealCRElT',  cut = ( vardb.getCuts(['TrigDec', 'LepTagTrigMatched',  'NBJet', '2Lep',	  'LowJetCR', 'ElRealFakeRateCR',			     'ElProbeTight',	 'ElEl_Event'		  ]) & truth_sub_OS & -vardb.getCut('SS') ) ) )
    """

    # OF only
    """
    vardb.registerCategory( MyCategory('OFFakeCRMuL',	cut =	vardb.getCuts(['TrigDec',  'LepTagTrigMatched',  'NBJet', '2Lep', 'SS', 'LowJetCR', 'MuRealFakeRateCR',  'ElTagEtaCut_ProbeMuEvent', 'MuProbeAntiTight', 'OF_Event'  ]) & truth_sub_SS ) )
    vardb.registerCategory( MyCategory('OFFakeCRMuT',	cut =	vardb.getCuts(['TrigDec',  'LepTagTrigMatched',  'NBJet', '2Lep', 'SS', 'LowJetCR', 'MuRealFakeRateCR',  'ElTagEtaCut_ProbeMuEvent', 'MuProbeTight',     'OF_Event'  ]) & truth_sub_SS ) )
    vardb.registerCategory( MyCategory('OFRealCRMuL',	cut = ( vardb.getCuts(['TrigDec',  'LepTagTrigMatched',  'NBJet', '2Lep',	  'LowJetCR', 'MuRealFakeRateCR',			     'MuProbeAntiTight', 'OF_Event'  ]) & truth_sub_OS & -vardb.getCut('SS') ) ) )
    vardb.registerCategory( MyCategory('OFRealCRMuT',	cut = ( vardb.getCuts(['TrigDec',  'LepTagTrigMatched',  'NBJet', '2Lep',	  'LowJetCR', 'MuRealFakeRateCR',			     'MuProbeTight',	 'OF_Event'  ]) & truth_sub_OS & -vardb.getCut('SS') ) ) )
    """
    #"""
    vardb.registerCategory( MyCategory('OFFakeCRElL',	cut =	vardb.getCuts(['TrigDec', 'LepTagTrigMatched',  'NBJet', '2Lep', 'SS', 'LowJetCR', 'ElRealFakeRateCR',			     'ElProbeAntiTight', 'OF_Event',   'Zsidescut']) & truth_sub_SS ) )
    vardb.registerCategory( MyCategory('OFFakeCRElT',	cut =	vardb.getCuts(['TrigDec', 'LepTagTrigMatched',  'NBJet', '2Lep', 'SS', 'LowJetCR', 'ElRealFakeRateCR',			     'ElProbeTight',	 'OF_Event',   'Zsidescut']) & truth_sub_SS ) )
    vardb.registerCategory( MyCategory('OFRealCRElL',	cut = ( vardb.getCuts(['TrigDec', 'LepTagTrigMatched',  'NBJet', '2Lep',	 'LowJetCR', 'ElRealFakeRateCR',			     'ElProbeAntiTight', 'OF_Event'		  ]) & truth_sub_OS & -vardb.getCut('SS') ) ) )
    vardb.registerCategory( MyCategory('OFRealCRElT',	cut = ( vardb.getCuts(['TrigDec', 'LepTagTrigMatched',  'NBJet', '2Lep',	 'LowJetCR', 'ElRealFakeRateCR',			     'ElProbeTight',	 'OF_Event'		  ]) & truth_sub_OS & -vardb.getCut('SS') ) ) )
    #"""

if doMMClosureTest:
    print ''

    if ( args.fakeMethod == 'MM' or args.fakeMethod == 'FF' ):
        #
        # MuMu region
        #
        #vardb.registerCategory( MyCategory('MuMuSS_SR_HighJet_DataDriven_Closure',         cut = vardb.getCuts(['TrigMatch', 'TrigDec', 'NBJet', '2Lep', 'SS', 'MuMu_Event',  'NJet2L']) ) )
        #vardb.registerCategory( MyCategory('MuMuSS_SR_LowJet_DataDriven_Closure',          cut = vardb.getCuts(['TrigMatch', 'TrigDec', 'NBJet', '2Lep', 'SS', 'MuMu_Event',  'LowJetCR']) ) )
        vardb.registerCategory( MyCategory('MuMuSS_SR_AllJet_DataDriven_Closure',          cut = vardb.getCuts(['TrigMatch', 'TrigDec', 'NBJet', '2Lep', 'SS', 'MuMu_Event']) ) )
        #
	# OF region
	#
	#vardb.registerCategory( MyCategory('OFSS_SR_HighJet_DataDriven_Closure',     cut = vardb.getCuts(['TrigMatch', 'TrigDec', 'NBJet', '2Lep', 'SS', 'OF_Event',   'NJet2L', ]) ) )   # 'OF_ElEtaCut',
	#vardb.registerCategory( MyCategory('OFSS_SR_LowJet_DataDriven_Closure',      cut = vardb.getCuts(['TrigMatch', 'TrigDec', 'NBJet', '2Lep', 'SS', 'OF_Event',   'LowJetCR', ]) ) ) # 'OF_ElEtaCut',
	vardb.registerCategory( MyCategory('OFSS_SR_AllJet_DataDriven_Closure',      cut = vardb.getCuts(['TrigMatch', 'TrigDec', 'NBJet', '2Lep', 'SS', 'OF_Event']) ) ) # ,  'OF_ElEtaCut'
	#
	# ElEl region
	#
	#vardb.registerCategory( MyCategory('ElElSS_SR_HighJet_DataDriven_Closure',   cut = vardb.getCuts(['TrigMatch', 'TrigDec', 'NBJet', '2Lep', 'SS', 'ElEl_Event', 'NJet2L']) ) )     #   'SF_ElEtaCut',
	#vardb.registerCategory( MyCategory('ElElSS_SR_LowJet_DataDriven_Closure',    cut = vardb.getCuts(['TrigMatch', 'TrigDec', 'NBJet', '2Lep', 'SS', 'ElEl_Event', 'LowJetCR']) ) ) #   'SF_ElEtaCut',
        vardb.registerCategory( MyCategory('ElElSS_SR_AllJet_DataDriven_Closure',    cut = vardb.getCuts(['TrigMatch', 'TrigDec', 'NBJet', '2Lep', 'SS', 'ElEl_Event']) ) ) # ,  'SF_ElEtaCut'

    if ( args.fakeMethod == 'ABCD' ):
        #
        # MuMu region
        #
        vardb.registerCategory( MyCategory('MuMuSS_SR_HighJet_DataDrivenABCD_Closure',   cut = vardb.getCuts(['TrigMatch', 'TrigDec', 'NBJet', '2Lep', 'SS', 'MuMu_Event', 'NJet2L']) ) )
        #
	# OF region
	#
	vardb.registerCategory( MyCategory('OFSS_SR_HighJet_DataDrivenABCD_Closure',     cut = vardb.getCuts(['TrigMatch', 'TrigDec', 'NBJet', '2Lep', 'SS', 'OF_Event',  'NJet2L']) ) )    # 'OF_ElEtaCut',
	#
	# ElEl region
	#
	vardb.registerCategory( MyCategory('ElElSS_SR_HighJet_DataDrivenABCD_Closure',   cut = vardb.getCuts(['TrigMatch', 'TrigDec', 'NBJet', '2Lep', 'SS', 'ElEl_Event', 'NJet2L']) ) )  # 'SF_ElEtaCut',

# ------------------------------------------------------------
# TTHBackgrounds2015 is the class used to manage each process:
#
#   Pass the input informations and the definitions and it
#   will perform the background estimationTTBarClosu
# ------------------------------------------------------------

ttH2015 = TTHBackgrounds2015(inputs, vardb)

# ------------------------------------
# Set the integrated luminosity (fb-1)
# ------------------------------------

# period A3,A4,C2,C3,C4,C5 GRL (EPS)
#ttH2015.luminosity = 0.0849676

# period D1-D6
#ttH2015.luminosity = 0.0803592

# period D-E, GRL v65
#ttH2015.luminosity = 0.3224
#ttH2015.luminosity = 0.278979
#ttH2015.lumi_units = 'pb-1'

# period D1-J6, GRL v71

#ttH2015.luminosity = 3.343 # EOYE GRL

if doRelaxedBJetCut:
  ttH2015.luminosity = 3.25 # v022 ntuples
else:
  ttH2015.luminosity = 3.302 # v021 ntuples

ttH2015.lumi_units = 'fb-1'

# for MM closure
if doMMClosureTest or doMMClosureRates:
	ttH2015.luminosity = 5.4
	ttH2015.lumi_units = 'fb-1'

# --------------------
# set the event weight
# --------------------

# MC generator event weight
#
weight_generator = 'mcEventWeight'

# PRW weight
#
weight_pileup = '1.0'
if not ( doMMClosureTest or doMMClosureRates ):
	weight_pileup = 'weight_pileup'

weight_glob = str(weight_generator) + ' * ' + str(weight_pileup)

print "\t Global eventweight (apply to ALL categories) - MC only --> ", weight_glob

ttH2015.eventweight = weight_glob

# ------------------------------------

ttH2015.useZCorrections = False

if doTwoLepSR or doTwoLepLowNJetCR or dottWCR or doZSSpeakCR or doMMClosureTest :
    ttH2015.channel = 'TwoLepSS'
elif doThreeLepSR or doThreeLepLowNJetCR or dottZCR or doWZonCR or doWZoffCR or doWZHFonCR or doWZHFoffCR:
    ttH2015.channel = 'ThreeLep'
elif doFourLepSR:
    ttH2015.channel = 'FourLep'
elif doDataMCCR or doMMRates or doMMClosureRates :
    ttH2015.channel = 'TwoLepCR'

cut = None
systematics = None
systematicsdirection = None # 'UP', 'DOWN'

events = {}
hists  = {}
# --------------------------------------
# Dictionary with systematics histograms
# --------------------------------------
systs = {}

# ----------------------------------
# List of the backgrounds considered
# ----------------------------------

samplenames = { 'Observed':'observed',
                'TTBarH':'signal',
		'TTBarW':'ttbarwbkg',
		'TTBarZ':'ttbarzbkg',
		'Top':'topbkg',
		'TTBar':'ttbarbkg',
		'TTBarClosureMM':'ttbarbkg',
		'TopCF':'topcfbkg',
		'Diboson':'dibosonbkg',
		'PowhegDiboson':'powhegdibosonbkg',
		'PowhegDibosonWW':'powhegdibosonwwbkg',
		'PowhegDibosonWZ':'powhegdibosonwzbkg',
		'PowhegDibosonZZ':'powhegdibosonzzbkg',
		'DibosonCF':'dibosoncfbkg',
		'HtoZZ':'htozzbkg',
		'Zjets':'zjetsbkg',
		'Zeejets':'zeejetsbkg',
		'Zmumujets':'zmumujetsbkg',
		'Ztautaujets':'ztautaujetsbkg',
		'ZjetsLF':'zjetsbkg',
		'MadGraphZjets':'madgraphzjetsbkg',
		'MadGraphZeejets':'madgraphzeejetsbkg',
		'MadGraphZmumujets':'madgraphzmumujetsbkg',
		'MadGraphZtautaujets':'madgraphztautaujetsbkg',
		'SherpaZjets':'sherpazjetsbkg',
		'SherpaZeejets':'sherpazeejetsbkg',
		'SherpaZmumujets':'sherpazmumujetsbkg',
		'SherpaZtautaujets':'sherpaztautaujetsbkg',
		'SherpaZjetsBFilter':'sherpazjetsbfilter',
		'SherpaZjetsCFilterBVeto':'sherpazjetsbfiltercveto',
		'SherpaZjetsCVetoBVeto':'sherpazjetscvetobveto',
		'SherpaZeejetsBFilter':'sherpazeejetsbfilter',
		'SherpaZeejetsCFilterBVeto':'sherpazeejetsbfiltercveto',
		'SherpaZeejetsCVetoBVeto':'sherpazjetscvetobveto',
		'SherpaZmumujetsBFilter':'sherpazmumujetsbfilter',
		'SherpaZmumujetsCFilterBVeto':',sherpazmumujetsbfiltercveto',
		'SherpaZmumujetsCVetoBVeto':'sherpazmumujetscvetobveto',
		'SherpaZtautaujetsBFilter':'sherpaztautaujetsbfilter',
		'SherpaZtautaujetsCFilterBVeto':',sherpaztautaujetsbfiltercveto',
		'SherpaZtautaujetsCVetoBVeto':',sherpaztautaujetscvetobveto',
		'Wjets':'wjetsbkg',
		'PowhegPythiaWjets':'powhegpythiawjets',
		'MadGraphWjets':'madgraphwjets',
		'MadGraphWenujets':'madgraphwenujets',
		'MadGraphWmunujets':'madgraphwmunujets',
		'MadGraphWtaunujets':'madgraphwtaunujets',
		'SherpaWjets':'sherpawjets',
		'SherpaWenujets':'sherpawenujets',
		'SherpaWmunujets':'sherpawmunujets',
		'SherpaWtaunujets':'sherpawtaunujets',
		'SherpaWjetsBFilter':'sherpawjetsbfilter',
		'SherpaWjetsCFilterBVeto':'sherpawjetsbfiltercveto',
		'SherpaWjetsCVetoBVeto':'sherpawjetscvetobveto',
		'SherpaWenujetsBFilter':'sherpawenujetsbfilter',
		'SherpaWenujetsCFilterBVeto':'sherpawenujetsbfiltercveto',
		'SherpaWenujetsCVetoBVeto':'sherpawenujetscvetobveto',
		'SherpaWmunujetsBFilter':'sherpawmunujetsbfilter',
		'SherpaWmunujetsCFilterBVeto':'sherpawmunujetsbfiltercveto',
		'SherpaWmunujetsCVetoBVeto':'sherpawmunujetscvetobveto',
		'SherpaWtaunujetsBFilter':'sherpawtaunujetsbfilter',
		'SherpaWtaunujetsCFilterBVeto':'sherpawtaunujetsbfiltercveto',
		'SherpaWtaunujetsCVetoBVeto':'sherpawtaunujetscvetobveto',
		'Prompt':'promptbkg',
		'ChargeFlip':'chargeflipbkg',
		'ChargeFlipMC':'chargeflipbkg',
		'FakesFF':'fakesbkg',
		'FakesMM':'fakesbkg',
                'FakesClosureMM':'fakesbgk',
                'FakesClosureABCD':'fakesbgk',
	      }
#
# Override colours!
#
colours      = {'Observed':kBlack,
        	'TTBarH':kBlack,
        	'TTBarW':kRed-4,
        	'TTBarZ':kRed-7,
        	'Top':kAzure+1,
        	'TTBar':kAzure+8,
		'TTBarClosureMM':kAzure+8,
        	'TopCF':kAzure-4,
        	'Diboson':kYellow-9,
		'PowhegDiboson':kYellow-9,
		'PowhegDibosonWW':kYellow-7,
		'PowhegDibosonWZ':kYellow-4,
		'PowhegDibosonZZ':kYellow-3,
        	'DibosonCF':kOrange-3,
        	'HtoZZ':kTeal+9,
        	'Zjets':kGreen,
		'Zeejets':kGreen-7,
		'Zmumujets':kTeal+2,
		'Ztautaujets':kTeal,
        	'ZjetsLF':kGreen,
		'MadGraphZjets':kGreen,
		'MadGraphZeejets':kGreen-7,
		'MadGraphZmumujets':kTeal+2,
		'MadGraphZtautaujets':kTeal,
		'SherpaZjets':kGreen,
		'SherpaZeejets':kGreen-7,
		'SherpaZmumujets':kTeal+2,
		'SherpaZtautaujets':kTeal,
		'SherpaZjetsBFilter':kGreen,
		'SherpaZjetsCFilterBVeto':kGreen,
		'SherpaZjetsCVetoBVeto':kGreen,
		'SherpaZeejetsBFilter':kGreen-7,
		'SherpaZeejetsCFilterBVeto':kGreen-7,
		'SherpaZeejetsCVetoBVeto':kGreen-7,
		'SherpaZmumujetsBFilter':kTeal+2,
		'SherpaZmumujetsCFilterBVeto':kTeal+2,
		'SherpaZmumujetsCVetoBVeto':kTeal+2,
		'SherpaZtautaujetsBFilter':kTeal,
		'SherpaZtautaujetsCFilterBVeto':kTeal,
		'SherpaZtautaujetsCVetoBVeto':kTeal,
        	'Wjets':kWhite,
		'PowhegPythiaWjets':kWhite,
		'MadGraphWjets':kWhite,
		'MadGraphWenujets':kGray,
		'MadGraphWmunujets':kGray+1,
		'MadGraphWtaunujets':kGray+2,
		'SherpaWjets':kWhite,
		'SherpaWenujets':kGray,
		'SherpaWmunujets':kGray+1,
		'SherpaWtaunujets':kGray+2,
		'SherpaWjetsBFilter':kWhite,
		'SherpaWjetsCFilterBVeto':kWhite,
		'SherpaWjetsCVetoBVeto':kWhite,
		'SherpaWenujetsBFilter':kGray,
		'SherpaWenujetsCFilterBVeto':kGray,
		'SherpaWenujetsCVetoBVeto':kGray,
		'SherpaWmunujetsBFilter':kGray+1,
		'SherpaWmunujetsCFilterBVeto':kGray+1,
		'SherpaWmunujetsCVetoBVeto':kGray+1,
		'SherpaWtaunujetsBFilter':kGray+2,
		'SherpaWtaunujetsCFilterBVeto':kGray+2,
		'SherpaWtaunujetsCVetoBVeto':kGray+2,
        	'Prompt':kOrange,
        	'ChargeFlip':kAzure-4,
        	'ChargeFlipMC':kAzure-4,
        	'FakesFF':kAzure-9,
        	'FakesMM':kTeal-9,
                'FakesClosureMM':kTeal+1,
		'FakesClosureABCD':kCyan - 9,
              }

if ( doSR or doLowNJetCR ):

    if not doFourLepSR:

    	if doMM:
    	    #plotbackgrounds	= [ 'TTBarW', 'TTBarZ', 'Top', 'TopCF', 'Diboson', 'DibosonCF', 'ZjetsLF', 'FakesMM']
    	    #ttH2015.backgrounds = [ 'TTBarW', 'TTBarZ', 'Top', 'TopCF', 'Diboson', 'DibosonCF', 'ZjetsLF', 'FakesMM']

    	    # MadGraph W/Z+jets
    	    #
	    # ---> using charge flip estimate from MC until we have an estimate from data
    	    plotbackgrounds	= ['Top','TTBar','MadGraphZeejets','MadGraphZmumujets','MadGraphZtautaujets','Diboson','MadGraphWjets','TTBarW','TTBarZ', 'ChargeFlipMC', 'FakesMM']
    	    ttH2015.backgrounds = ['Top','TTBar','MadGraphZeejets','MadGraphZmumujets','MadGraphZtautaujets','Diboson','MadGraphWjets','TTBarW','TTBarZ', 'ChargeFlipMC', 'FakesMM']
	    ttH2015.signals     = [ ] #['TTBarH']

	elif doFF:
    	    plotbackgrounds	= [ 'TTBarW', 'TTBarZ', 'Top', 'TopCF', 'Diboson', 'DibosonCF', 'ZjetsLF', 'FakesFF']
    	    ttH2015.backgrounds = [ 'TTBarW', 'TTBarZ', 'Top', 'TopCF', 'Diboson', 'DibosonCF', 'ZjetsLF', 'FakesFF']
    	else:
    	    # MC based estimate of fakes
    	    plotbackgrounds	= [ 'TTBarW', 'TTBarZ', 'Top', 'TopCF', 'Diboson', 'DibosonCF', 'ZjetsLF']
    	    ttH2015.backgrounds = [ 'TTBarW', 'TTBarZ', 'Top', 'TopCF', 'Diboson', 'DibosonCF', 'ZjetsLF']

    else:
        # no fakes in 4lep
        plotbackgrounds	    = [ 'TTBarW', 'TTBarZ', 'Top', 'TopCF', 'Diboson', 'DibosonCF', 'ZjetsLF']
        ttH2015.backgrounds = [ 'TTBarW', 'TTBarZ', 'Top', 'TopCF', 'Diboson', 'DibosonCF', 'ZjetsLF']

if doMMRates or doDataMCCR:

    # PowhegPythia Z+jets
    #
    #plotbackgrounds     = ['Top','TTBar','Zeejets','Zmumujets','Ztautaujets','Diboson','SherpaWjets','TTBarW','TTBarZ']
    #ttH2015.backgrounds = ['Top','TTBar','Zeejets','Zmumujets','Ztautaujets','Diboson','SherpaWjets','TTBarW','TTBarZ']

    # Sherpa W/Z+jets
    #
    #plotbackgrounds	= ['Top','TTBar','SherpaZeejets','SherpaZmumujets','SherpaZtautaujets','Diboson','SherpaWjets','TTBarW','TTBarZ']
    #ttH2015.backgrounds = ['Top','TTBar','SherpaZeejets','SherpaZmumujets','SherpaZtautaujets','Diboson','SherpaWjets','TTBarW','TTBarZ']

    # MadGraph W/Z+jets
    #
    plotbackgrounds     = ['Top','TTBar','MadGraphZeejets','MadGraphZmumujets','MadGraphZtautaujets','Diboson','MadGraphWjets','TTBarW','TTBarZ']
    ttH2015.backgrounds = ['Top','TTBar','MadGraphZeejets','MadGraphZmumujets','MadGraphZtautaujets','Diboson','MadGraphWjets','TTBarW','TTBarZ']

    ttH2015.signals     = [ ] #['TTBarH']

    ttH2015.observed    = ['Observed']
    if args.ratesFromMC:
        ttH2015.observed    = []

if doMMClosureRates:
      plotbackgrounds	  = ['TTBar']
      ttH2015.backgrounds = ['TTBar']
      ttH2015.signals	  = []
      ttH2015.observed    = []

if doMMClosureTest:
    if doMM:
      plotbackgrounds	  = ['FakesClosureMM']
      ttH2015.backgrounds = ['FakesClosureMM'] # truth cuts done internally in FakesClosureMM class
      ttH2015.signals     = []#['FakesClosureABCD']
      ttH2015.observed    = ['TTBarClosureMM'] # truth cuts done internally in TTBarClosureMM class
      #ttH2015.observed    = ['TTBar']
    elif doFF:
      plotbackgrounds	  = ['FakesFF']
      ttH2015.backgrounds = ['FakesFF']
      ttH2015.signals     = []
      ttH2015.observed    = ['TTBar']
    elif doABCD:
      plotbackgrounds	  = ['FakesClosureABCD']
      ttH2015.backgrounds = ['FakesClosureABCD'] # truth cuts done internally in FakesClosureABCD class
      ttH2015.signals     = []
      ttH2015.observed    = ['TTBarClosureMM'] # truth cuts done internally in TTBarClosureMM class
      #ttH2015.observed    = ['FakesClosureMM'] # truth cuts done internally in TTBarClosureMM class
    else:
      plotbackgrounds	  = ['TTBar']
      ttH2015.backgrounds = ['TTBar']
      ttH2015.signals	  = []
      ttH2015.observed    = []
      #ttH2015.observed    = ['TTBar']


if args.noSignal:
    ttH2015.signals = []


isblinded = False
# Make blinded plots in SR
#
if doSR and not doMMClosureTest:
        ttH2015.observed = []
        isblinded=True

# -------------------------------------------------------
# Filling histname with the name of the variables we want
#
# Override colours as well
# -------------------------------------------------------
histname   = {'Expected':'expected'}
histcolour = {'Expected':kBlack}
for samp in ttH2015.backgrounds:
        histname[samp]  = samplenames[samp]
        histcolour[samp] = colours[samp]
	#
	# Will override default colour based on the dictionary provided above
	#
	ttH2015.str_to_class(samp).colour = colours[samp]
for samp in ttH2015.observed:
        histname[samp]  = samplenames[samp]
        histcolour[samp] = colours[samp]
	#
	# Will override default colour based on the dictionary provided above
	#
	ttH2015.str_to_class(samp).colour = colours[samp]
for samp in ttH2015.signals:
        histname[samp]  = samplenames[samp]
        histcolour[samp] = colours[samp]
	#
	# Will override default colour based on the dictionary provided above
	#
	ttH2015.str_to_class(samp).colour = colours[samp]
print histname
print histcolour



# ---------------------------------
# Processing categories in sequence
# ---------------------------------
for category in vardb.categorylist:

    print "Making plots in category: {0}".format( category.name )
    if ( category.cut != None ):
        print " defined by cuts --> {0}".format( category.cut.cutname )

    signalfactor = 1.0
    background = ttH2015

    # NB: *must* initialise this to 1.0 !!
    #
    lepSF_weight  = '1.0'

    if not ("TightLeptons") in category.cut.cutname :

	if not ( doMMClosureTest or doMMClosureRates ):

	    if ("ElEl_Event") in category.cut.cutname :

	       lepSF_weight = 'weight_electron_RecoEff_SF[0] * weight_electron_PIDEff_SF_LHLoose[0] * weight_electron_trig[0]'
    	       print "\t Category contains \'ElEl_Event\': apply this extra weight to events - MC only --> ", lepSF_weight

    	    elif ("MuMu_Event") in category.cut.cutname :

	       lepSF_weight = 'weight_muon_RecoEff_SF[0] * weight_muon_IsoEff_SF_Loose[0] * weight_muon_trig[0]'
    	       print "\t Category contains \'MuMu_Event\': apply this extra weight to events - MC only --> ", lepSF_weight

    	    elif ( ("MuEl_Event"in category.cut.cutname)  or ("ElMu_Event" in category.cut.cutname) or ("OF_Event" in category.cut.cutname) ):

	       lepSF_weight = 'weight_electron_RecoEff_SF[0] * weight_electron_PIDEff_SF_LHLoose[0] * weight_muon_RecoEff_SF[0] * weight_muon_IsoEff_SF_Loose[0] * weight_muon_trig[0]'
    	       print "\t Category contains (\'MuEl_Event\' || \'ElMu_Event\' || \'OF_Event\'): apply this extra weight to events - MC only --> ", lepSF_weight

    # ------------------------------
    # Processing different variables
    # ------------------------------
    for idx,var in enumerate(vardb.varlist, start=0):

	# NB: *must* initialise this to 1.0 !!
        #
        bjetSF_weight = '1.0'
        combined_SF_weight = '1.0'

        print "\t now plotting variable: ", var.shortname, "\n"

        # When looking at jet multiplicity distributions w/ bjets, BTag SF must be applied also to categories w/o any bjet cut
        #
	if not ( doMMClosureTest or doMMClosureRates ):
           if  ( ("BJet") in category.cut.cutname and not doRelaxedBJetCut ) or ("BJet") in var.shortname:
              bjetSF_weight = 'weight_jet__MV2c20_SFFix77[0]'
              print "\t Category contains \'BJet\', or plotting variable \'Bjet\' : apply this extra weight to events - MC only --> ", bjetSF_weight

        combined_SF_weight = str(lepSF_weight) + ' * ' + str(bjetSF_weight)

        print "**************************\n Combined SF weight for events in category:\n ", category.name ,"\n for variable:\n ", var.shortname ,"\n --> ", combined_SF_weight, "\n**************************\n"

        #if idx is 0:
        #    Get event yields for *this* category. Do it only for the
        #    first variable in the list
        #
        #    events[category.name] = background.events(cut=cut, eventweight=combined_SF_weight, category=category, hmass=['125'], systematics=systematics, systematicsdirection=systematicsdirection)

	# --------------------------
	# Avoid making useless plots
	# --------------------------

	if ( ("MuMu") in category.name and ("El") in var.shortname ) or ( ("ElEl") in category.name and ("Mu") in var.shortname ):
            print "\t skipping variable: ", var.shortname
	    continue
	if ( ( ("MuEl") in category.name or ("ElMu") in category.name or ("OF") in category.name ) and ( ("El1") in var.shortname or ("Mu1") in var.shortname ) ) :
            print "\t skipping variable: ", var.shortname
	    continue
        if doMMRates:
	    # if probe is a muon, do not plot ElProbe* stuff!
	    if ( ( ("MuRealFakeRateCR") in category.cut.cutname ) and ( ("ElProbe") in var.shortname ) ):
               print "\t skipping variable: ", var.shortname
	       continue
	    # if probe is an electron, do not plot MuProbe* stuff!
	    if ( ( ("ElRealFakeRateCR") in category.cut.cutname ) and ( ("MuProbe") in var.shortname ) ):
               print "\t skipping variable: ", var.shortname
	       continue
	    # be smart when looking at OF regions!
	    if ( ("OF") in category.name and( ("MuRealFakeRateCR") in category.cut.cutname ) and ( ("MuTag") in var.shortname ) ):
               print "\t skipping variable: ", var.shortname
	       continue
	    if ( ("OF") in category.name and( ("ElRealFakeRateCR") in category.cut.cutname ) and ( ("ElTag") in var.shortname ) ):
               print "\t skipping variable: ", var.shortname
	       continue

	# ---------------------------------------------------------
        # Creating a directory for the category if it doesn't exist
	# ---------------------------------------------------------
        fakeestimate=''
        if doMM:
                fakeestimate='_MM'
        if doFF:
                fakeestimate='_FF'

        dirname =  'OutputPlots' + args.selection + fakeestimate + '_' + args.outdirname + '/'

	# If specified a cut before entering the loop, it will be applied
	# Otherwise, all the cuts registered above for *this* category will be applied
	#
        if cut:
            dirname = dirname  + category.name + ' ' + cut.cutname
        else:
            dirname = dirname  + category.name
	if args.doLogScaleX:
	        var.logaxisX = True # activate X-axis log scale in plot
		dirname += '_LOGX'
	if args.doLogScaleY:
	        var.logaxis  = True # activate Y-axis log scale in plot
		dirname += '_LOGY'
        dirname = dirname.replace(' ', '_')
        try:
            os.makedirs(dirname)
        except:
            pass

	# -----------------------------------------------
        # Making a plot with ( category + variable ) name
	# -----------------------------------------------
        plotname = dirname + '/' + category.name + ' ' + var.shortname
        plotname = plotname.replace(' ', '_')

	if ( args.debug ):
	   print "plotname: ", plotname

	wantooverflow = True

	list_formats = [ plotname + '.png' ] #, plotname + '_canvas.root' ]
	if args.doEPS:
	    list_formats.append( plotname + '.eps' )

	doShowRatio = not isblinded

	#
	# Here is where the plotting is actually performed!
	#
        hists[category.name + ' ' + var.shortname] = background.plot( var,
								      cut=cut,
								      eventweight=combined_SF_weight,
	       							      category=category,
								      signal='',#'125',
								      signalfactor=signalfactor,
								      overridebackground=plotbackgrounds,
								      systematics=systematics,
								      systematicsdirection=systematicsdirection,
								      overflowbins=wantooverflow,
								      showratio=doShowRatio,
								      wait=False,
								      save=list_formats,
								      log=None,
								      logx=None
								    )

        # Creating a file with the observed and expected distributions and systematics.
	# We fit them for TES uncertainty studies
        #
	foutput = TFile(plotname + '.root','RECREATE')
        if ( 'Mll01' in var.shortname ) or ( 'NJets' in var.shortname ):
		outfile = open(plotname + '_yields.txt', 'w')

	if args.doSyst:

	    #
	    # systematics go into a different folder
            #
	    dirname = dirname.replace(' ', '_') + '_Syst'

	    #
	    # loop on the defined systematics
	    #
	    total_syst      = 0.0
	    total_syst_up   = 0.0
	    total_syst_down = 0.0
            histograms_syst = {}

	    for syst in vardb.systlist:
                try:
                    os.makedirs(dirname)
                except:
                    pass
                plotname = dirname + '/' + category.name + ' ' + var.shortname + ' ' + syst.name
                plotname = plotname.replace(' ', '_')
                #
		# plotSystematics is the function which takes care of the systematics
                #
		systs[category.name + ' ' + var.shortname] = background.plotSystematics( syst,
											 var=var,
											 cut=cut,
								                         eventweight=combined_SF_weight,
											 category=category,
											 overflowbins=wantooverflow,
											 showratio=True,
											 wait=False,
											 save=[plotname+'.png']
										       )
		#
                # Obtains the total MC histograms with a particular systematics shifted and saving it in the ROOT file
                #

		print 'plotname: ', plotname
		systobs, systnom, systup, systdown, systlistup, systlistdown = systs[category.name + ' ' + var.shortname]

		print 'systematic: ', syst.name

                histograms_syst['Expected_'+syst.name+'_up']=systup
                histograms_syst['Expected_'+syst.name+'_up'].SetNameTitle(histname['Expected']+'_'+syst.name+'_up','')
                histograms_syst['Expected_'+syst.name+'_up'].SetLineColor(histcolour['Expected'])
                histograms_syst['Expected_'+syst.name+'_up'].Write()
                histograms_syst['Expected_'+syst.name+'_down']=systdown
                histograms_syst['Expected_'+syst.name+'_down'].SetNameTitle(histname['Expected']+'_'+syst.name+'_down','')
                histograms_syst['Expected_'+syst.name+'_down'].SetLineColor(histcolour['Expected'])
                histograms_syst['Expected_'+syst.name+'_down'].Write()
                for samp in ttH2015.backgrounds:
                        histograms_syst[samp+'_'+syst.name+'_up'] = systlistup[samp]
                        histograms_syst[samp+'_'+syst.name+'_up'].SetNameTitle(histname[samp]+'_'+syst.name+'_up','')
                        histograms_syst[samp+'_'+syst.name+'_up'].SetLineColor(histcolour[samp])
                        histograms_syst[samp+'_'+syst.name+'_up'].Write()
                        histograms_syst[samp+'_'+syst.name+'_down'] = systlistdown[samp]
                        histograms_syst[samp+'_'+syst.name+'_down'].SetNameTitle(histname[samp]+'_'+syst.name+'_down','')
                        histograms_syst[samp+'_'+syst.name+'_down'].SetLineColor(histcolour[samp])
                        histograms_syst[samp+'_'+syst.name+'_down'].Write()
                #ACTUALLY THE CODE DOES NOT CONSIDER SYSTEMATICS FOR THE SIGNAL. PUT IT AMONG THE BACKGROUNDS IF YOU WANT SYST ON IT
		if ( 'Mll01' in var.shortname ) or ( 'NJets' in var.shortname ):
			outfile.write('Integral syst: \n')
			outfile.write('syst %s up:   delta_yields = %f \n' %(syst.name,(systup.Integral()-systnom.Integral())))
			outfile.write('syst %s down: delta_yields = %f \n' %(syst.name,(systdown.Integral()-systnom.Integral())))
			if ( args.debug ):
				outfile.write('GetEntries syst: \n')
				outfile.write('syst %s up:   delta_entries %f \n' %(syst.name,(systup.GetEntries()-systnom.GetEntries())))
				outfile.write('syst %s down: delta_entries %f \n' %(syst.name,(systdown.GetEntries()-systnom.GetEntries())))
		total_syst = total_syst + (systup.Integral()-systdown.Integral())/2.0*(systup.Integral()-systdown.Integral())/2.0
		total_syst_up   += (systup.Integral()-systnom.Integral())*(systup.Integral()-systnom.Integral())
		total_syst_down += (systdown.Integral()-systnom.Integral())*(systdown.Integral()-systnom.Integral())

	    total_syst      = math.sqrt(total_syst)
	    total_syst_up   = math.sqrt(total_syst_up)
	    total_syst_down = math.sqrt(total_syst_down)

	    if ( 'Mll01' in var.shortname ) or ( 'NJets' in var.shortname ):
		    outfile.write('yields total syst UP: %f \n' %(total_syst_up))
		    outfile.write('yields total syst DN: %f \n' %(total_syst_down))
		    outfile.write('yields total syst: %f \n' %(total_syst))

        # Obtains the histograms correctly normalized
	#
        mclist, expected, observed, signal, _ = hists[category.name + ' ' + var.shortname]
        histograms = {}

	for samp in ttH2015.observed:
                 histograms[samp] = observed
        if ttH2015.backgrounds:
	        histograms['Expected']=expected
                for samp in ttH2015.backgrounds:
                        histograms[samp] = mclist[samp]
                        #in case you have to add other histograms you maybe prefer to use the method clone:
                        #histograms[samp] = mclist[samp].Clone(histname[samp])
        if ttH2015.signals:
	        for samp in ttH2015.signals:
                        histograms[samp] = signal

	#print histograms

        for samp in histograms.keys():
                histograms[samp].SetNameTitle(histname[samp],'')
                histograms[samp].SetLineColor(histcolour[samp])

	if ( 'Mll01' in var.shortname ) or ( 'NJets' in var.shortname ):
		print 'Category: ', category.name
		print 'Variable: ', var.shortname
		print 'Integral: '
		outfile.write('Category: %s \n' %(category.name))
		outfile.write('Variable: %s \n' %(var.shortname))
		outfile.write('Integral: \n')
		err=Double(0)  # integral error
		value=0        # integral value
                for samp in histograms.keys():
			print '%s: %f' %(histname[samp], histograms[samp].Integral())
			value=histograms[samp].IntegralAndError(1,histograms[samp].GetNbinsX(),err)
			outfile.write('yields %s: %f +- %f \n' %(histname[samp], value, err))
		print 'GetEntries: '
		outfile.write('GetEntries: \n')
                for samp in histograms.keys():
			print '%s: %f' %(histname[samp], histograms[samp].GetEntries())
			outfile.write('entries %s: %f \n' %(histname[samp], histograms[samp].GetEntries()))

        for samp in histograms.keys():
                histograms[samp].Write()
        foutput.Close()

	if ( 'Mll01' in var.shortname ) or ( 'NJets' in var.shortname ):
		outfile.close()

