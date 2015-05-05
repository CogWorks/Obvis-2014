#!/usr/bin/env python

"""Process obvis data"""
print __doc__


import sys, time, random, os, math,re
import pdb
import numpy
import argparse
#import pygame
import glob

from Obvis_Trials import Trial_Objects_2, Trial_Objects_4
from read_sims import Sims_p,Sims_s


from velocity_fixation import EyeSample, extract_fixations,write_fixations


cwd = os.getcwd()
DirName = os.path.join(cwd,'ProcessData/')

class EyeData():
    def __init__(self,tm,x,y):
        self.tm = int(float(tm))
        self.xpos = int(x)
        self.ypos = int(y)
        return


class ObvisTrial():
    
    def __init__(self, lst,exp):
        self.trial_id = lst[4]
        self.target_id = lst[2]
        self.trgt_cnd = lst[0]
        self.distractor_type = lst[1]
        if exp == 'experiment-4':
            self.sim_distractors = lst[5]
            self.disim_distractors = lst[6]
        elif self.distractor_type == 'SIMILAR':
            self.sim_distractors = lst[3]
            self.disim_distractors = []
        else:
            self.sim_distractors = []
            self.disim_distractors = lst[3]


class ExpTrial():
    def __init__(self, subj_id, s_trial_id, e_trial_id):
        self.subjid = subj_id
        self.trial_num = s_trial_id #trial-targ-start
        self.exp_trial_id = e_trial_id #trial-targ-start
        self.stim_pos = [] #trial-stimuli-start
        self.trgt_id = None #trial-stimuli-start
        self.distract_cnd = None #trial-stimuli-start
        self.num_fixations = 0
        self.subj_rsp_tm = None  #trial-stimuli-start - trial-stimuli-end
        self.trgt_cnd = None #trial-stumuli-end
        self.rsp_state = None #trial-stumuli-end
        self.trial_targ_pos = None #trial-target-location
        self.subj_rsp_pos = None #trial-target-location
        self.fixations = []
        self.d0 = None
        self.d1 = None
        self.d2 = None
        self.d3 = None
        self.d4 = None
        self.d5 = None
        self.d6 = None
        self.d7 = None
        self.stim_start_tm = None
        self.stim_end_tm = None


class Process_Eye_Data():
    
    fix_header = ['subjid','trial_num','trial_phase','fix_num','start_tm','end_tm','duration','x_cog','y_cog', 'role','distance', 'aoi', 'image_id','psim','ssim']
    
    trial_header = ['subjid','trial_num','exp_trial_id','trgt_id', 'distract_cnd', 'd0', 'd1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd7', 'trgt_cnd', 'rsp_state',  'trial_targ_pos', 'subj_rsp_pos', 'subj_rsp_tm']
    '''
        subjid = 4-digit
        trial_num = (0 - 399) for experiment-2,4, (0 - 499) for experiment-1
        exp_trial_id = identifies the pre-determined trial data: Target - present or absent
                                                                 Distractor type  - similar, disimilar or equal (experiment 4 only)
                                                                 List of distractors
        trgt_id = 0 - 999 index to target data base
        distract_cnd = similar, disimilar or equal (experiment 4 only)
        trgt_cnd = present or absent
        rsp_state = present or absent
        trial_targ_pos = d0 - d7 position of target
        subj_rsp_pos = d0 - d7 position selected by subject
        subj_rsp_tm = time in ms from the start fo the find phase to pushing the present or absent button
        trial_phase  = sniff (target image displayed in center position) or find for location target on dial
                       The dial is labeled d0 - d7 with d0 being at 3 o'clock and then moving clockwise
        fix_num = fixation number for center postion  or dial positions
        start_tm = time in ms of first sample in fixation
        end_tm = time in ms of last sample in fixation
        duration = time in ms ftrom first to last sample in fixation
        x_cog = x coordinate of center of fixation
        y_cog = y coordinate of center of fixation
        aoi = image center nearest to x_cog,y_cog
        distance = distance in pixels from aoi to fixation center
        role = sim_distr or dis_distr or target or empty for Experiment 2 and 4, target or distractor or empty for Experiment 1
            empty means that the fixation was on the center position during the find phase
        image_id = id of image that was fixated
    '''
    
    
    def __init__(self,args):
        self.exp_name = args.exp_name
        self.output_type = args.out_file
        self.fs = None
        self.fs1 = None
        self.display_trial = args.display
        self.vel_fix_accum = []
        
        self.trial_def_objs = []
        self.trials = []
        self.current_trial = None
        self.gaze_accum = []
        self.gazes = []
        self.eyetracker_time = 0

    def dist (self,p1,q1,p2,q2):
        dx,dy = p1 - q1, p2 - q2
        return(math.sqrt(dx*dx + dy*dy))
    
    
    def write_exp_header(self):
        fname = DirName + self.exp_name + '_base.txt'
        self.fs = open(fname,'w')
        header = self.trial_header + self.fix_header[2:]
        self.fs.write("\t".join(header))
        self.fs.write("\n")
    
    def write_tr_header(self):
        fname = DirName + self.exp_name + '_trials.txt'
        self.fs1 = open(fname,'w')
        header = self.trial_header
        self.fs1.write("\t".join(header))
        self.fs1.write("\n")
    
    def write_trial_data(self,trials):
        for trial in trials:
            for k in self.trial_header:
                self.fs1.write(str(trial.__dict__[k]))
                if k != self.trial_header[-1]:
                    self.fs1.write("\t")
                else:
                    self.fs1.write("\n")
    '''
    def write_subject_data(self,trials):
        for trial in trials:
            if len(trial.fixations) > 0:
                for o in trial.fixations:
                    if o.trial_phase == 'sniff' or o.trial_phase == 'find':
                        for k in self.trial_header:
                            self.fs.write(str(trial.__dict__[k]))
                            self.fs.write("\t")
                        for k in self.fix_header [2:]:
                            self.fs.write(str(o.__dict__[k]))
                            if k != self.fix_header[-1]:
                                self.fs.write("\t")
                            else:
                                self.fs.write("\n")
    '''                            
    def write_subject_data(self,trials):
        for trial in trials:
            if len(trial.fixations) > 0:
                sniff_fl,find_fl = False,False
                for o in trial.fixations:
                    if o.trial_phase == 'sniff':
                        sniff_fl = True
                    elif o.trial_phase == 'find':
                        find_fl = True
                    if o.trial_phase == 'sniff' or o.trial_phase == 'find':
                        for k in self.trial_header:
                            self.fs.write(str(trial.__dict__[k]))
                            self.fs.write("\t")
                        for k in self.fix_header [2:]:
                            self.fs.write(str(o.__dict__[k]))
                            if k != self.fix_header[-1]:
                                self.fs.write("\t")
                            else:
                                self.fs.write("\n")
            
                if not find_fl:
                    self.write_null_fix(trial, 'find')
                elif not sniff_fl:
                    self.write_null_fix(trial, 'sniff')
            else:
                self.write_null_fix(trial, 'sniff')
                self.write_null_fix(trial, 'find')
    
    def write_null_fix(self,trial, phase):
        for k in self.trial_header:
            self.fs.write(str(trial.__dict__[k]))
            self.fs.write("\t")
        self.fs.write(phase)
        self.fs.write("\t")
        for k in self.fix_header [3:]:
            self.fs.write('N/A')
            if k != self.fix_header[-1]:
                self.fs.write("\t")
            else:
                self.fs.write("\n")

    def proc_experiment_data(self):
        print(self.exp_name)
        fn = DirName_raw + '*.xls'
        filenames = glob.glob(fn)
        for l in Trial_Objects:
            self.trial_def_objs.append(ObvisTrial(l,self.exp_name))
        self.write_exp_header() if self.output_type == 'fix' else self.write_tr_header()
        fn = DirName + self.exp_name + '-classifications.txt'
        fs = open(fn,'r')
        self.gazes = fs.readlines()
        for g in self.gazes[1:]:
            temp = re.sub('"',' ',g)
            self.gaze_accum.append(temp.split())
        for f in filenames:
            print(os.path.basename(f))
            fs = open(f,'r')
            lines = fs.readlines()     
            self.process_log_file(lines)    
            cnt = 0
            for tr in self.trials:
                if tr.trial_targ_pos != tr.subj_rsp_pos:
                    cnt += 1
                for o in tr.fixations:
                    if o.image_id == 'NA': o.image_id = tr.trgt_id
                    if self.exp_name == 'experiment-1' and o.trial_phase == 'find' and o.aoi != 'c':
                        o.role = 'target' if o.aoi == tr.trial_targ_pos else 'distractor'
                    if o.role == 'distractor' or o.role == 'sim_distr' or o.role == 'dis_distr':
                        o.psim = Sims_p[int(tr.trgt_id)-1][int(o.image_id)-1]
                        o.ssim = Sims_s[int(tr.trgt_id)-1][int(o.image_id)-1]
            print('Num Errors = ', cnt)
            self.write_subject_data(self.trials) if self.output_type == 'fix' else self.write_trial_data()
            self.vel_fix_accum = []
            self.trials = []

    def assign_object(self,fix):
        if fix.trial_phase == 'find':
            for k,v in TD.stimuli_pos.iteritems():
                temp = self.dist(fix.x_cog,v[0],fix.y_cog,v[1])
                if temp < fix.distance:
                    fix.aoi = k
                    fix.distance = temp
            fix.distance = int(fix.distance)
            if fix.aoi != 'c' and self.exp_name != 'experiment-1' and self.current_trial.stim_pos:
                #print(fix.aoi,self.current_trial.stim_pos,self.current_trial.trial_num)
                id = int(self.current_trial.stim_pos[int(fix.aoi[-1])]) #fix.aoi is a string
                fix.image_id = id
                for o in self.trial_def_objs:
                    if o.trial_id == int(self.current_trial.exp_trial_id):
                        if id in o.sim_distractors:
                            fix.role = 'sim_distr'
                        elif id in o.disim_distractors:
                            fix.role = 'dis_distr'
                        else:
                            fix.role = 'target'
                        break
            elif fix.aoi == 'c':
                fix.role = 'empty'
                fix.image_id = 'None'
            elif self.exp_name == 'experiment-1':
                fix.image_id = int(self.current_trial.stim_pos[int(fix.aoi[-1])]) if self.current_trial.stim_pos else 'NA' #fix.aoi is a string
                
        else:
            fix.role = 'target'
            fix.aoi = 'c'
            fix.image_id = 'NA'
            fix.distance = int(self.dist(fix.x_cog,TD.stimuli_pos['c'][0],fix.y_cog,TD.stimuli_pos['c'][1]))
            if fix.distance > 280:
                #print(fix.aoi, fix.distance)
                return(False)
        return(True)



    def extract_stim_start_info(self, ln):
        if self.exp_name != 'experiment-1':
            self.current_trial.stim_pos = ln[8:16]
            self.current_trial.trgt_id = ln[16]
            self.current_trial.distract_cnd = ln[17]
            self.current_trial.subj_rsp_tm = int(ln[2])
        else:
            self.current_trial.stim_pos = ln[7:15]
            self.current_trial.trgt_id = ln[15]
            self.current_trial.distract_cnd = 'random'
            self.current_trial.subj_rsp_tm = int(ln[2])
        self.current_trial.d0 = self.current_trial.stim_pos[0]
        self.current_trial.d1 = self.current_trial.stim_pos[1]
        self.current_trial.d2 = self.current_trial.stim_pos[2]
        self.current_trial.d3 = self.current_trial.stim_pos[3]
        self.current_trial.d4 = self.current_trial.stim_pos[4]
        self.current_trial.d5 = self.current_trial.stim_pos[5]
        self.current_trial.d6 = self.current_trial.stim_pos[6]
        self.current_trial.d7 = self.current_trial.stim_pos[7]
        '''
        for f in self.vel_fix_accum:
            if not f.image_id and f.role == 'target':
                f.image_id = self.current_trial.trgt_id
        '''

    def conv_pos(self, pos):
        if pos !='NIL':
            return('d' + str(pos))
        return('F/A')

    def extract_targ_loc_info(self,ln):
        if self.exp_name != 'experiment-1':
            self.current_trial.trial_targ_pos =  self.conv_pos(ln[8])
            self.current_trial.subj_rsp_pos = self.conv_pos(ln[9])
        else:
            self.current_trial.trial_targ_pos = self.conv_pos(ln[7])
            self.current_trial.subj_rsp_pos = self.conv_pos(ln[8])

    def extract_stim_end_info(self, ln):
        self.current_trial.stim_end_tm = self.eyetracker_time
        if self.exp_name != 'experiment-1':
            self.current_trial.trgt_cnd = ln[8]
            self.current_trial.rsp_state = ln[9]
        else:
            self.current_trial.trgt_cnd = 'N/A'
            self.current_trial.rsp_state = 'N/A'

    def compare_subjids(self,str1,str2):
        return(int(str1.replace("-","")) == int(str2.replace("-","")))
        
    def process_log_file(self,lines):
        self.vel_fix_accum = []
        num = 0
        sac_tm = 0
        fix = None
        collect = False
        obj_type = None
        fnum_targ = 0
        fnum_stim = 0
        cnt = 0
        bad_cnt = 0
        subj_id = re.sub('"',' ',lines[0]).split()[0]
        gazes = [g for g in self.gaze_accum if self.compare_subjids(g[0],subj_id)]
        num_gazes = len(gazes)
        print(num_gazes,subj_id)
        if num_gazes == 0: pdb.set_trace()
        for l in lines:
            temp = re.sub('"',' ',l)
            ln = temp.split()
            if ln[4] == 'EG-DATA':
                
                if int(ln[5]) == 0: bad_cnt += 1
                sample = EyeSample (ln[2],ln[7],ln[8],ln[10],ln[5],self.current_trial,obj_type) #mac-time, x, y, pc-time,status,trial,obj_type
                self.eyetracker_time = ln[10]
                '''
                for g in gazes:
                    if g[3] == ln[10]:
                        sample.classification = g[4]
                        break
                '''
                sample.classification = gazes[cnt][4]
                cnt += 1
                fix,num,sac_tm,saccade = extract_fixations(sample,fix,num,sac_tm)
                
                if fix and saccade:
                    self.assign_object(fix)
                    
                    if fix.trial_phase == 'sniff': 
                        fix.fix_num = fnum_targ
                        fnum_targ += 1
                    elif fix.trial_phase == 'find': 
                        fix.fix_num = fnum_stim
                        fnum_stim += 1
                    fix.subjid = subj_id
                    self.vel_fix_accum.append(fix)
                    fix = None
            elif ln[4] == 'trial-target-start':
                fnum_targ = 1
                collect = True
                subj_id = str(ln[0])[-4:]
                if self.current_trial:
                    #print('trial ', self.current_trial.trial_num,self.current_trial.stim_start_tm)
                    for f in self.vel_fix_accum:
                        if f.trial:
                            if int(f.trial_num) < int(ln[6]): f.trial_num = ln[6]
                            #print(f.trial.trial_num,f.trial_phase,f.start_tm,f.end_tm)
                        #else:
                            #print('no trial',f.trial_phase,f.start_tm,f.end_tm)
                    self.current_trial.fixations = self.vel_fix_accum
                    self.vel_fix_accum = []
                self.current_trial = ExpTrial(subj_id,ln[6],ln[7]) if self.exp_name != 'experiment-1' else ExpTrial(subj_id,ln[6],'N/A')
                self.trials.append(self.current_trial)
                obj_type = 'sniff'
                self.current_trial.stim_start_tm = self.eyetracker_time
            elif ln[4] == 'trial-mask-start':
                collect = False
                obj_type = None
            elif ln[4] == 'trial-stimuli-start':
                self.extract_stim_start_info(ln)
                fnum_stim = 1
                collect = True
                obj_type = 'find'
            elif ln[4] == 'trial-stimuli-end':
                #print(ln)
                if self.current_trial.subj_rsp_tm:
                    self.current_trial.subj_rsp_tm = int(ln[2]) - self.current_trial.subj_rsp_tm
                else:
                    self.current_trial.subj_rsp_tm = 'Bad'
                self.extract_stim_end_info(ln)
                obj_type = None
                collect = False
                
            elif ln[4] == 'trial-buttons-start':
                pass
            elif ln[4] == 'trial-target-location':
                self.extract_targ_loc_info(ln)
            elif ln[4] == 'trial-buttons-end':
                self.extract_targ_loc_info(ln)
                '''
                print('trial ', self.current_trial.trial_num,self.current_trial.stim_start_tm)
                for f in self.vel_fix_accum:
                    if f.trial:
                        print(f.trial.trial_num,f.trial_phase,f.start_tm)
                    else:
                        print('no trial',f.trial_phase,f.start_tm)
                self.current_trial.fixations = self.vel_fix_accum
                self.vel_fix_accum = []
                '''
        #pdb.set_trace()
        print('data quality', round( 100 * (1.0 - (bad_cnt / float(cnt)))))
        
    

class TaskDisplay():
    
    colors = {
        'Black':(0, 0, 0),
        'White':(255, 255, 255),
        'Red':(255, 0, 0),
        'Green':(0, 255, 0),
        'Blue':(0, 0, 255),
        'Yellow':(255, 255, 0),
        'Purple':(148, 0, 211),
        'Grey':(211, 211, 211),
        'Aqua':(0, 255, 255),
        'Snow1':(238, 233, 233),
        'Snow2':(205, 201, 201)
    }
    
    stimuli_pos = {
        'd0': (844,400) ,'d1': (852,612) ,'d2': (640,700) ,'d3': (331,612) ,'d4': (244,400) ,'d5': (331,187) ,'d6': (640,100),'d7': (852,187) , 'c': (640,400)
    }
    fullscreen = False
    screen = None
    
    def __init__(self):
        #pygame.init()
        #info = pygame.display.Info()
        #print(info.current_w,info.current_h)
        self.trial = None
        self.current_fixations = []
        self.current_eye = None
        self.current_screen =None

    '''
    def make_screen(self):
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0,0)
        self.screen = pygame.display.set_mode((1280,960),pygame.RESIZABLE)
        self.background = self.colors['Grey']
        self.screen.fill(self.background)
        self.mid_x = self.screen.get_width() / 2
        self.mid_y = self.screen.get_height() / 2
        self.end_x = self.screen.get_width()
        self.end_y = self.screen.get_height()
        pygame.display.set_caption("Task")
        pygame.mouse.set_visible(False)
        pygame.display.update()
    
    def show_a_trial(self,fix_accum,col):
        if not self.screen:
            self.make_screen()
        self.trial = raw_input('Enter trial id: ')
        self.screen.fill(self.background)
        cnt = 0
        for d in fix_accum:
            if d.trial == int(self.trial) and d.trial_phase == 'find':
                self.draw_fix(d,self.colors[col])
                cnt += 1
                if cnt > 100:
                    inp = raw_input('Enter 0 to stop, 1 to continue ')
                    if inp == 0:
                        break
                    cnt = 0
                    pygame.display.update()
        pygame.display.update()
        inp = raw_input('Enter 0 to stop, 1 to continue ')
            
    def draw_fixdata_by_time(self, fix_accum,start, end):
        for d in fix_accum:
            if d.start_tm >= start and d.end_tm <= end:
                self.draw_fix(d, self.colors['Green'])
                self.current_fixations.append(d)
                pygame.display.update()
        
    def draw_fix(self,fix,col):
        r = int(fix.duration / 10.0)
        self.current_eye = (fix.x_cog, fix.y_cog)
        if r < 3:
            print (self.current_eye,r)
        pygame.draw.circle(self.screen,col,self.current_eye,r,0)
'''        
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser( formatter_class = argparse.ArgumentDefaultsHelpFormatter )
    parser.add_argument( '-D', '--display', action = "store", dest = "display", default = 'none', help = 'display trial' )
    parser.add_argument( '-E', '--experiment', action = 'store', dest = "exp_name", default = 'experiment-4', help = 'experiment -1,2,4')
    parser.add_argument( '-O', '--output', action = 'store', dest = "out_file", default = 'fix', help = 'fix or trial')
    parser.add_argument( '-F', '--fix_threshold', action = 'store', dest = "fix_threshold", default = 50, help = 'minimum duration for fixation')
    
    args = parser.parse_args()
    

    DirName_raw = os.path.join(DirName, args.exp_name) + '/'
    
    Trial_Objects = Trial_Objects_4 if args.exp_name == 'experiment-4' else Trial_Objects_2
    

    PED = Process_Eye_Data(args)
    TD = TaskDisplay()
    #E = PyMouseEvent()
    #E.start()
    
    PED.proc_experiment_data()
        

