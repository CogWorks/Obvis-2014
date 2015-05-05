#!/usr/bin/env python

"""Read Sim Files"""

import os, numpy
cwd = os.getcwd()

Sims_p = numpy.ndarray((1000,1000))
Sims_s = numpy.ndarray((1000,1000))
Sim_files = [['pair_wise_distances.txt','Sims_p'], ['sims_prop_50_smpl_01_colr_03', 'Sims_s']]
def read_sim_files():
    for lst in Sim_files:
        fn = cwd + "/Similarity_files/" + lst[0]
        f = open(fn,'r')
        lines = f.readlines()
        for l in lines:
            item = l.split(' ')
            if lst[1] == 'Sims_p':
                Sims_p[int(item[0])-1][int(item[1])-1] = float(item[2])
                Sims_p[int(item[1])-1][int(item[0])-1] = float(item[2])
            else:
                Sims_s[int(item[0])-1][int(item[1])-1] = float(item[2])
    return
    
read_sim_files()