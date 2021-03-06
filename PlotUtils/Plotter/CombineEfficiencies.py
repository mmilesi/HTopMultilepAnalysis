#!/usr/bin/env python

import os, argparse

parser = argparse.ArgumentParser(description="Combine efficiency histograms from different files into a unique file. This will be the input to the MM code.")

trigmatch_opts = ["UNBIASED","YES_TM","NOT_TM"]

parser.add_argument("dest", metavar="dest",type=str,
                  help="Directory where output will be stored.")
parser.add_argument("--triggerMatching", dest="triggerMatching", action="store", default=trigmatch_opts[0], const=trigmatch_opts[0], type=str, nargs="?",
                  help="Specify whether the input efficiencies are trigger-dependent (unbiased, TM or anti-TM). Available add-ons to this option: [" + ",".join( "{0}".format( s ) for s in trigmatch_opts ) + "]). If no add-on to this option is specified, default will be {0}".format(trigmatch_opts[0]))

args = parser.parse_args()

from ROOT import ROOT, TFile
print("\nRunning w/ option:\n--triggerMatching={0}\n".format(args.triggerMatching))


def copyMuon():

  # Real muon eff from T&P (OS, em,me, SLT)

  if ( args.triggerMatching == "UNBIASED" ):
    path_r_mu = "./PLOTS_25ns_v26/MMClosure_v26_SUSYTP/OutputPlots_MMClosureRates_25ns_v26_LeptonCutBased_410501/"
  elif ( args.triggerMatching == "YES_TM" ):
    path_r_mu = "./PLOTS_25ns_v26/MMClosure_v26_SUSYTP/OutputPlots_MMClosureRates_25ns_v26_LeptonCutBased_410501_TRIGMATCH_EFF/"
  elif ( args.triggerMatching == "NOT_TM" ):
    path_r_mu = "./PLOTS_25ns_v26/MMClosure_v26_SUSYTP/OutputPlots_MMClosureRates_25ns_v26_LeptonCutBased_410501_NOT_TRIGMATCH_EFF/"

  file_r_mu = TFile(path_r_mu + "LeptonEfficiencies.root")

  hist_r_mu_pt = file_r_mu.Get("Real_Mu_Pt_Efficiency_expectedbkg")

  hist_r_mu_pt.SetDirectory(0)

  # Fake muon eff from likelihood (SS, mm, DLT)

  if ( args.triggerMatching == "UNBIASED" ) :
    path_f_mu = "./PLOTS_25ns_v26/MMClosure_v26_LikelihoodFit/OutputPlots_MMClosureRates_LHFit_DLT_25ns_v26_LeptonCutBased_410501/"
  elif ( args.triggerMatching == "YES_TM" ):
    path_f_mu = "./PLOTS_25ns_v26/MMClosure_v26_LikelihoodFit/OutputPlots_MMClosureRates_LHFit_DLT_25ns_v26_LeptonCutBased_410501_TRIGMATCH_EFF/"
  elif ( args.triggerMatching == "NOT_TM" ):
    path_f_mu = "./PLOTS_25ns_v26/MMClosure_v26_LikelihoodFit/OutputPlots_MMClosureRates_LHFit_DLT_25ns_v26_LeptonCutBased_410501_NOT_TRIGMATCH_EFF/"

  file_f_mu = TFile(path_f_mu + "LeptonEfficiencies_LH/LH_mumu/LH_efficiencies_fake_mu_mumu.root")

  hist_f_mu_pt = file_f_mu.Get("f_hist")

  hist_f_mu_pt.SetName("Fake_Mu_Pt_Efficiency_expectedbkg")

  hist_f_mu_pt.SetDirectory(0)

  histlist = [hist_r_mu_pt,hist_f_mu_pt]

  return histlist

def copyElectron():

  # Real electron eff from T&P (OS, em,me, SLT)

  if ( args.triggerMatching == "UNBIASED" ):
    path_r_el = "./PLOTS_25ns_v26/MMClosure_v26_SUSYTP/OutputPlots_MMClosureRates_25ns_v26_LeptonCutBased_410501/"
  elif ( args.triggerMatching == "YES_TM" ):
    path_r_el = "./PLOTS_25ns_v26/MMClosure_v26_SUSYTP/OutputPlots_MMClosureRates_25ns_v26_LeptonCutBased_410501_TRIGMATCH_EFF/"
  elif ( args.triggerMatching == "NOT_TM" ):
    path_r_el = "./PLOTS_25ns_v26/MMClosure_v26_SUSYTP/OutputPlots_MMClosureRates_25ns_v26_LeptonCutBased_410501_NOT_TRIGMATCH_EFF/"

  file_r_el = TFile(path_r_el + "LeptonEfficiencies.root")

  hist_r_el_pt  = file_r_el.Get("Real_El_Pt_Efficiency_expectedbkg")
  hist_r_el_eta = file_r_el.Get("Real_El_Eta_Efficiency_expectedbkg")
  hist_r_el_AVG = file_r_el.Get("Real_El_Pt_Efficiency_expectedbkg_AVG")

  hist_r_el_pt.SetDirectory(0)
  hist_r_el_eta.SetDirectory(0)
  hist_r_el_AVG.SetDirectory(0)

  # Fake electron eff from T&P (SS, em,me (muon tag), SLT)

  hist_f_el_pt  = file_r_el.Get("Fake_El_Pt_Efficiency_expectedbkg")
  hist_f_el_eta = file_r_el.Get("Fake_El_Eta_Efficiency_expectedbkg")
  hist_f_el_AVG = file_r_el.Get("Fake_El_Pt_Efficiency_expectedbkg_AVG")

  hist_f_el_pt.SetDirectory(0)
  hist_f_el_eta.SetDirectory(0)
  hist_f_el_AVG.SetDirectory(0)

  histlist = [hist_r_el_pt,hist_f_el_pt,hist_r_el_eta,hist_f_el_eta,hist_r_el_AVG,hist_f_el_AVG]

  return histlist


if __name__ == "__main__":

  if not args.triggerMatching in trigmatch_opts:
    err = "the add-on \"{0}\"".format(args.triggerMatching) + " specified for option --triggerMatching is unknown. Must be one of: [" + ",".join( "{0}".format( s ) for s in trigmatch_opts ) + "]"
    raise ValueError(err)

  append = ""
  if ( args.triggerMatching == "YES_TM" ):
    append = "_TRIGMATCH_EFF"
  elif ( args.triggerMatching == "NOT_TM" ):
    append = "_NOT_TRIGMATCH_EFF"

  basedir = args.dest
  if basedir.endswith('/'):
    basedir = basedir[:-1]

  outputpath = basedir + append
  if not os.path.exists(outputpath):
    print("Creating directory: {0}".format(outputpath))
    os.makedirs(outputpath)

  outputfile = outputpath + "/" + "LeptonEfficiencies.root"

  print("Storing efficiency histograms in:\n{0}".format(outputfile))

  f = TFile(outputfile,"RECREATE")

  h_mu = copyMuon()
  h_el = copyElectron()

  h_all = h_mu + h_el

  f.cd()

  for h in h_all:
    h.Write()

  f.Close()
