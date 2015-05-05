import os,argparse,time,pdb, numpy,glob

cwd = os.getcwd()
BaseDir = os.path.join(cwd,'ProcessData/')

im_pos = ['d' + str(i) for i in range(8)]
header =  ['subjid','trial_num', 'trgt_cnd','distract_cnd','subj_result','trgt_num', 'num_look','sim_look','sim_no_look']
header_all =  ['exp','vers','subjid','trial_num', 'trgt_cnd','distract_cnd','subj_result','trgt_num', 'num_look','sim_look_p','sim_no_look_p','sim_look_s','sim_no_look_s']


exp_roles = [[], ["distractor"], ["sim_distr", "dis_distr"],[],["sim_distr", "dis_distr"]]
Sims_p = numpy.ndarray((1000,1000))
Sims_s = numpy.ndarray((1000,1000))

class AlgoTrial():
    trgt_id = None
    tot_sim = 0
    
    def __init__(self,d,exp,v):
        self.roles = exp_roles[int(exp)]
        self.exp = exp
        self.vers = v
        self.subjid = d['subjid']
        self.trial_num = d['trial_num']
        self.seq = []
        self.seq_num = 0
        self.trgt_cnd = d['trgt_cnd'] if exp != '1' else 'Present'
        self.distract_cnd = d['distract_cnd']
        self.trgt_id = d['trgt_id']
        self.tot_sim = 0
        self.subj_result = "1" if d['trial_targ_pos'] == d['subj_rsp_pos'] else "0"
        self.trgt_1 = "NA"
        self.trgt_last = "NA"
        self.trgt_num = 0
        self.items = []
        self.num_look = 0
        self.look = []
        self.no_look = []
        self.sim_look = []
        self.sim_no_look = []
        self.sim_look_p = []
        self.sim_no_look_s = []
        self.sim_look_p = []
        self.sim_no_look_s = []
        for pos in im_pos:
            self.items.append(d[pos])
        if d['trial_phase'] == "find":
                self.seq.append(d['role'])
                self.seq_num  = str(len(self.seq))
                if d['role'] == 'target':
                    self.trgt_num +=1
                    if self.trgt_num == 1:
                        self.trgt_1 = len(self.seq)
                    else:
                        self.trgt_last = len(self.seq)
                elif d['role'] in self.roles:
                    im_id = self.items[im_pos.index(d['aoi'])]
                    if im_id not in self.look:
                        self.num_look += 1
                        self.look.append(im_id)
        
    def add_role(self,d,exp):
        if d['trial_phase'] == 'find':
            self.seq.append(d['role'])
            self.seq_num = str(len(self.seq))
            if d['role'] == 'target':
                self.trgt_num +=1
                if self.trgt_num == 1:
                    self.trgt_1 = len(self.seq)
                else:
                    self.trgt_last = len(self.seq)
            elif d['role'] in self.roles:
                im_id = self.items[im_pos.index(d['aoi'])]
                if im_id not in self.look:
                    self.num_look += 1
                    self.look.append(im_id)
                    
    def set_no_look(self):
        for i in im_pos:
            im_id = self.items[im_pos.index(i)] #image index
            if im_id not in self.look:
                self.no_look.append(im_id)
                
    def get_sims(self,source,sim_lst,sims):
        for item in source:
            sim_lst.append(sims[int(self.trgt_id)-1][int(item)-1])
                    
    def calc_mean_sims(self,w):
        self.get_sims(self.look,self.sim_look,Sims)
        self.get_sims(self.no_look,self.sim_no_look,Sims)
        #print(self.num_look,self.look,self.sim_look)
        self.sim_look = numpy.mean(self.sim_look) if len(self.sim_look) > 0 else 0
        self.sim_no_look = numpy.mean(self.sim_no_look) if len(self.sim_no_look) > 0 else 0
        
    def calc_mean_sims_both(self,w):
        self.get_sims(self.look,self.sim_look,Sims_p)
        self.get_sims(self.no_look,self.sim_no_look,Sims_p)
        self.sim_look_p = numpy.mean(self.sim_look) if len(self.sim_look) > 0 else 0
        self.sim_no_look_p = numpy.mean(self.sim_no_look) if len(self.sim_no_look) > 0 else 0
        self.get_sims(self.look,self.sim_look,Sims_s)
        self.get_sims(self.no_look,self.sim_no_look,Sims_s)
        if w == 'position':
            sim.look = map(lambda x: x * (1 / sim.look.index(x)),sim.look)
        self.sim_look_s = numpy.mean(self.sim_look) if len(self.sim_look) > 0 else 0
        self.sim_no_look_s = numpy.mean(self.sim_no_look) if len(self.sim_no_look) > 0 else 0
##################

def write_compare_sim(accum,header,args):
    fname = BaseDir + "compare_sim_" + args.experiment + args.algo[0] + ".txt"
    fs = open(fname,'w')
    fs.write("\t".join(header))
    fs.write("\n")
    for obj in accum:
        obj.seq = "_".join(obj.seq) if len(obj.seq) > 0 else "NA"
        for k in header:
            if not isinstance(obj.__dict__[k],str): obj.__dict__[k] = str(obj.__dict__[k])
            fs.write(obj.__dict__[k])
            if k != header[-1]:
                fs.write("\t")
            else:
                fs.write("\n")
            
def open_output_file(header):
    fname = BaseDir + "compare_sim_all.txt"
    fs = open(fname,'a')
    fs.write("\t".join(header))
    fs.write("\n")
    return(fs)
    
def write_compare_all(accum,fs,header):
    for obj in accum:
        obj.seq = "_".join(obj.seq) if len(obj.seq) > 0 else "NA"
        for k in header:
            if not isinstance(obj.__dict__[k],str): obj.__dict__[k] = str(obj.__dict__[k])
            fs.write(obj.__dict__[k])
            if k != header[-1]:
                fs.write("\t")
            else:
                fs.write("\n")
 
def read_sim_file(args):
    fn = cwd + "/Similarity_files/" + args.sim_fn
    f = open(fn,'r')
    lines = f.readlines()
    for l in lines:
        item = l.split(' ')
        #pdb.set_trace()
        Sims[int(item[0])-1][int(item[1])-1] = float(item[2])
        if args.algo == 'parallel':
            Sims[int(item[1])-1][int(item[0])-1] = float(item[2])
    return
    
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
    
Exps = ['1','2','4']
Version = ['7'] #['5','5_50']

def run ():
    read_sim_files()
    output_fs = open_output_file(header_all)
    for exp in Exps:
        for v in Version:
            f = BaseDir + 'experiment-' + exp + '_base_v' + v + '.txt'
            print(f)
            fs = open(f,'r')
            trials = process_base_file(fs,exp,v)
            for tr in trials:
                tr.set_no_look()
                tr.calc_mean_sims_both(args.weight)
            write_compare_all(trials,output_fs,header_all)
            
def run_one(args):
    read_sim_file(args)
    f = BaseDir + 'experiment-' + args.experiment + '_base_v' + args.version + '.txt'
    print(f)
    fs = open(f,'r')
    trials = process_base_file(fs,args.experiment,args.version)
    for tr in trials:
        tr.set_no_look()
        tr.calc_mean_sims(args.weight)
    write_compare_sim(trials,header,args)
    
def process_base_file(fs,exp,v):
    cnt = 0
    accum = []
    algo = []
    bad_cnt = 0
    lines = fs.readlines()
    hd = lines[0].split()
    print(hd)
    trial_num = -1
    tm = time.time()
    for l in lines[1:]:
        ln = l.split('\t')
        cnt += 1
        dict = {}
        dict = dict.fromkeys(hd)
        if len(ln) > len(hd):
            pdb.set_trace()
        for i in range(len(ln)):
            k = hd[i]
            dict[k] = ln[i]
        if dict['trial_num'] != trial_num:
            algo.append(AlgoTrial(dict,exp,v))
            trial_num = dict['trial_num']
        else:
            if algo[-1].trial_num == dict['trial_num']:
                algo[-1].add_role(dict,exp)
            #accum.append(dict)
        #if cnt % 1000 == 0:
            #print(cnt)
    print(time.time() - tm)
    print('Number of trials ',trial_num,' Time elapsed ',time.time() - tm)
    return(algo)
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser( formatter_class = argparse.ArgumentDefaultsHelpFormatter )
    parser.add_argument( '-E', '--experiment', action = "store", dest = "experiment",default = '1', help = 'experiment num' )
    parser.add_argument( '-V', '--version', action = "store", dest = "version",default= 'vel', help = 'version' )
    parser.add_argument( '-S', '--sims', action = "store", dest = "sim_fn",default= 'sims_prop_50_smpl_01_colr_03', help = 'simularity file' )
    parser.add_argument( '-A', '--algo', action = "store", dest = "algo",default= 'sims', help = 'sims or parallel' )
    parser.add_argument( '-R', '--run', action = "store", dest = "fn",default= 'all', help = 'all or one' )
    parser.add_argument( '-W', '--weight', action = "store", dest = "weight",default= 'none', help = 'weight distractor, position or none' )
    args = parser.parse_args()
    if args.fn == 'all':
        run()
    else:
        run_one(args)