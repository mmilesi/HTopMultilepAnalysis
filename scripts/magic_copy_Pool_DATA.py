#!/usr/bin/env python

""" magic_copy_Pool.py: parallelise xrdcp copy via multiprocessing.Pool """

__author__     = "Marco Milesi"
__email__      = "marco.milesi@cern.ch"
__maintainer__ = "Marco Milesi"

import glob, os, sys, subprocess, shutil

import multiprocessing

def listchunks(l, n):
    n = max(1, n)
    return [l[i:i + n] for i in range(0, len(l), n)]

def copy(sample):
    cmd = sample
    subprocess.call(cmd,shell=True)

if __name__ == '__main__':

    username = "mmilesi"

    version     = "25ns_v23/version_2"
    sample_type = "Data"

    basedir = "/coepp/cephfs/mel/mmilesi/ttH/GroupNTup/" + version + "/" + sample_type

    copylist = [
276262,
276329,
276336,
276416,
276511,
276689,
276778,
276790,
276952,
276954,
278880,
278912,
278968,
279169,
279259,
279279,
279284,
279345,
279515,
279598,
279685,
279813,
279867,
279928,
279932,
279984,
280231,
280273,
280319,
280368,
280423,
280464,
280500,
280520,
280614,
280673,
280753,
280853,
280862,
280977,
281070,
281074,
281075,
281317,
281385,
281411,
282625,
282631,
282712,
282784,
282992,
283074,
283155,
283270,
283429,
283608,
283780,
284006,
284154,
284213,
284285,
284420,
284427,
284484,
297730,
298595,
298609,
298633,
298687,
298690,
298771,
298773,
298862,
298967,
299055,
299144,
299147,
299184,
299243,
299584,
300279,
300345,
300415,
300418,
300487,
300540,
300571,
300600,
300655,
300687,
300784,
300800,
300863,
300908,
301912,
301918,
301932,
301973,
302053,
302137,
302265,
302269,
302300,
302347,
302380,
302391,
302393,
302737,
302831,
302872,
302919,
302925,
302956,
303007,
303079,
303201,
303208,
303264,
303266,
303291,
303304,
303338,
303421,
303499,
303560,
303638,
303832,
303846,
303892,
303943,
304006,
304008,
304128,
304178,
304198,
304211,
304243,
304308,
304337,
304409,
304431,
304494,
305380,
305543,
305571,
305618,
305671,
305674,
305723,
305727,
305735,
305777,
305811,
305920,
306269,
306278,
306310,
306384,
306419,
306442,
306448,
306451,
307126,
307195,
307259,
307354,
307394,
307454,
307514,
307539,
307569,
307601,
307619,
307656,
307710,
307732,
307861,
307935,
308047,
308084,
309375,
309390,
309440,
309516,
309640,
309759,
310015,
310247,
310249,
310341,
310370,
310405,
310468,
310473,
310634,
310691,
310809,
310863,
310872,
310969,
311071,
311170,
311244,
311287,
311321,
311402,
311473,
    ]

    cmdlist = []
    for sample in copylist:
        cmd = "cd " + basedir + " && mkdir -p 00" + str(sample) + " && cd $_ && xrdcp root://eospublic.cern.ch//eos/escience/UniTexas/HSG8/multileptons_ntuple_run2/" + version + "/" + sample_type + "/00" + str(sample) + ".root ."
        cmdlist.append(cmd)

    MAX_PARALLEL = 6

    #print listchunks(cmdlist,MAX_PARALLEL)

    for chunk in listchunks(cmdlist,MAX_PARALLEL):

        if not os.path.exists("/tmp/krb5cc_1016"):
	    print("Please get a Kerberos ticket first:")
	    krb_auth = "kinit " + username + "@CERN.CH"
	    subprocess.call(krb_auth,shell=True)
        subprocess.call("kinit -R",shell=True)

        print("Copying samples: ")
        print("\n".join("{0} - {1}".format(elem[0],elem[1].split()[5]) for elem in enumerate(chunk)))
        p = multiprocessing.Pool(MAX_PARALLEL)
        p.map(copy,chunk)
	p.close()
        p.join()

    os.chdir(basedir)
    print("Transfer finished!")
