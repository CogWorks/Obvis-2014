#!/usr/bin/env python

"""Dispersion Fixation Algorithm"""
print __doc__

import math, pdb

class EyeSample():
    def __init__(self,tm,x_in,y_in,lc_time,status,tr, tr_step):
        self.data_time = int(lc_time)
        self.end_time = None
        self.x = int(x_in)
        self.y = int(y_in)
        self.decency = int(status)
        self.mac_time = int(tm)
        self.trial = int(tr.trial_num)
        self.trial_phase = tr_step

    def good_data_p(self):
        return(self.decency > 0 & self.x >= 0 & self.y >= 0)


class D_Fixation():
    def __init__(self):
        self.begin_mac = None
        self.end_mac = None
        self.samples_in = 0
        self.time_sample_out = None
        self.x_fix = 0
        self.y_fix = 0
        self.x_cog = 0
        self.y_cog = 0
        self.fix_num = 0
        self.start_tm = 0
        self.end_tm = 0
        self.duration = 0
        self.pupil = 0
        self.trial_num = None
        self.subjid = None
        self.aoi = None
        self.role = None
        self.distance = 9999
        self.trial_phase = None
        self.distractor_type = 'N/A'
        self.image_id = None
        self.psim = 'NA'
        self.ssim = 'NA'
        
    
    def within_current_fixation_p(self,ed,radius):
        return(radius > math.sqrt(math.pow(ed.x - self.x_cog,2) + math.pow(ed.y - self.y_cog,2)))
    
    def outlier_threshold_exceeded_p (self, ed,threshold):
        if self.time_sample_out:
            return (threshold >= ed.data_time - self.time_sample_out)
        else:
            self.time_sample_out = ed.data_time
            return(False)
    
    
    def fixation_in_progress_p(self):
        return(self.samples_in > 0)
                  
    def minimum_fixation_p(self, threshold):
        return(self.duration >= threshold)
                  
    def potential_gt_present_p (self, potential):  #self = present fixation
        return(potential.samples_in > self.samples_in)
    
    def add_new_point(self, sample):
        if self.trial_num and sample.trial == self.trial_num or not(self.trial_num):
            if self.trial_phase and self.trial_phase == sample.trial_phase or not(self.trial_phase):
                if not(self.trial_phase):
                    self.trial_phase = sample.trial_phase
                if not(self.trial_num):
                    self.trial_num = sample.trial
                self.samples_in += 1
                self.x_fix += sample.x
                self.y_fix += sample.y
                self.x_cog = int(self.x_fix / self.samples_in)
                self.y_cog = int(self.y_fix / self.samples_in)
                if self.start_tm == 0:
                    self.start_tm = sample.data_time
                    self.begin_mac = sample.mac_time
                self.end_tm = sample.data_time
                self.end_mac = sample.mac_time
                self.duration = self.end_tm - self.start_tm
                
            else:
                print('same not in same trial step', sample.data_time)
        else:
            print('sample not in same trial', sample.data_time)
                  
    def restore_out_points(self,to):  #self = from
        if self.samples_in > 0:
            to.samples_in += self.samples_in
            to.x_fix += self.x_fix
            to.y_fix += self.y_fix
            to.x_cog = to.x_fix / to.samples_in
            to.y_cog = to.y_fix / to.samples_in
            #print(to.end_tm,self.end_tm,self.fix_num)
            to.end_tm = self.end_tm
            to.end_mac = self.end_mac
            to.duration = to.end_tm - to.start_tm
            #print(to.end_tm,self.end_tm,to.start_tm,to.duration)



class DispersionAlgo():
    def __init__(self,fix_threshold = 100):
        self.fix_radius = 35
        self.time_bad_data = 0
        self.bad_data_threshold = 100
        self.fixation_threshold = fix_threshold #50 #100
        self.outlier_threshold = 17
        self.present_fix = D_Fixation()
        self.potential_fix = D_Fixation()
        self.good_fixation = None
                  
    def reset_potential(self):
        self.potential_fix = D_Fixation()
                  
    def finish_fixation(self):
        #print('finish', self.present_fix.x_cog, self.present_fix.y_cog)
        self.good_fixation = self.present_fix
        self.present_fix = D_Fixation()
                  
    def potential_to_present(self):
        self.present_fix = self.potential_fix
        self.potential_fix = D_Fixation()
                  
    def reset_fixations(self):
        self.present_fix = D_Fixation()
        self.potential_fix = D_Fixation()
    
    def terminate_fixation(self):
        self.good_fixation = False
        if (self.present_fix.fixation_in_progress_p() and
            self.present_fix.minimum_fixation_p(self.fixation_threshold)):
            self.finish_fixation()
        elif (self.potential_fix.fixation_in_progress_p() and
              self.potential_fix.minimum_fixation_p(self.fixation_threshold)):
                self.potential_to_present()
                self.finish_fixation()
        self.reset_fixations()
        return(self.good_fixation)
    
            

    
    
    def Disp_fix_Algo (self, ed):
        self.good_fixation = False
        step = []
        if ed.good_data_p():
            self.time_bad_data = 0
            step.append('good')
            #print(ed.data_time)
            if self.present_fix.fixation_in_progress_p():
                step.append('in progress')
                if self.present_fix.within_current_fixation_p(ed,self.fix_radius):
                     self.potential_fix.restore_out_points(self.present_fix)
                     self.reset_potential()
                     step.append('add')
                     self.present_fix.add_new_point(ed)
                else:
                    step.append('not in')
                    if (self.present_fix.outlier_threshold_exceeded_p(ed,self.outlier_threshold) and
                        self.present_fix.minimum_fixation_p(self.fixation_threshold)):
                        step.append('create fix')
                        self.finish_fixation()
                        self.potential_to_present()
                        if self.present_fix.within_current_fixation_p(ed,self.fix_radius):
                            step.append('adding to potential/present')
                            self.present_fix.add_new_point(ed)
                        else:
                            self.reset_potential()
                            step.append('add potential')
                            self.potential_fix.add_new_point(ed)
                    elif self.potential_fix.fixation_in_progress_p():
                        step.append('potential in prog')
                        if self.potential_fix.within_current_fixation_p(ed,self.fix_radius):
                            step.append('add to potential 2')
                            self.potential_fix.add_new_point(ed)
                            if self.potential_fix.minimum_fixation_p(self.fixation_threshold):
                                step.append('move to present')
                                self.potential_to_present()
                        else:
                            step.append('not in potential')
                            if self.present_fix.potential_gt_present_p(self.potential_fix):
                                step.append('move to present 2')
                                self.potential_to_present()
                            self.reset_potential()
                            self.potential_fix.add_new_point(ed)
                    else:
                        step.append('add to potential 3')
                        self.potential_fix.add_new_point(ed)
            else:
                step.append('new')
                self.present_fix.add_new_point(ed)
                #print('starting')
                self.reset_potential()
        else:
            step.append('bad')
            if self.time_bad_data == 0:
                self.time_bad_data = ed.data_time
            if (ed.data_time - self.time_bad_data) > self.bad_data_threshold:
                self.time_bad_data = 0
                if self.present_fix.minimum_fixation_p(self.fixation_threshold):
                    step.append('create fix 2')
                    self.finish_fixation()
                    self.reset_fixations()
                else:
                    step.append('reset')
                    self.reset_fixations()
        if self.good_fixation:
            step.append('godd fix')
        #print(step)
        return(self.good_fixation)



















