

from data_simulation import ClusterSimulator
from data_file import file
from array import array
import ROOT
from ROOT import TFile, TTree

class SimpleAlgo:
   
    def __init__(self ,name ,ngen ):
        
        simulator=ClusterSimulator("config1.json")
        self.name=name
        self.ngen=ngen
        self.b=simulator.b
        self.r=simulator.r
        #Input file to use
        self.inputFileName = 'data_root/'+self.name +'.root'
        fileDoesNotExist = ROOT.gSystem.AccessPathName(self.inputFileName)
        
        #Checking if it does exist
        if fileDoesNotExist:
            file.cfile(self.name,self.ngen)

        self.inputFile = TFile.Open(self.inputFileName)
        if self.inputFile is None:
            raise ROOT.Error("Error opening input file %s - exit", self.inputFileName.Data())
        
        self.tsng_list=[]
        self.tbkg_list=[]

        f = TFile.Open(self.inputFileName)

        tsng = f.Get("tsgn")
        tbkg = f.Get("tbkg")
        
        clusSize = self.r
        
        xsng = array('f',[0]*clusSize)
        xbkg = array('f',[0]*clusSize)
        
        tsng.SetBranchAddress("clus",xsng)
        tbkg.SetBranchAddress("clus",xbkg)
        for i in range(self.ngen):
            tsng.GetEntry(i)
            tbkg.GetEntry(i)
            self.tsng_list.append([xsng[k] for k in range(clusSize)])
            self.tbkg_list.append([xbkg[k] for k in range(clusSize)])
        f.Close()  

    def is_signal(self,type, cluster, threshold):

        self.type=type
        self.threshold=threshold
        self.cluster=cluster
        
        # Check if the cluster is a signal based on hypothesis with a given threshold
        if self.type == "integral" :
            
            q_max=max(self.cluster)
            p_max=self.cluster.index(q_max) #position of the highest charge

            if p_max == 0:
                nq_max = self.cluster[p_max+1]
            elif p_max == len(self.cluster)-1:
                nq_max = self.cluster[p_max-1]
            else:
                nq_max = max([self.cluster[p_max-1],self.cluster[p_max+1]])

            mclus=self.cluster.copy()
            mclus=[x - q_max + nq_max for x in mclus] 

            if sum(i for i in mclus if i > 0) <= self.threshold:
                return True
            else:
                return False
            
        elif self.type == "charge" : 
                
            if sum(self.cluster) <= self.threshold:
                return True
            else:
                return False
            
        elif self.type == "width" :
            
            fv=self.cluster.index(next(filter(lambda x: x!= 0, self.cluster),0))  #first non-zero value 

            lv= len(self.cluster)-self.cluster[::-1].index(next(filter(lambda x: x!= 0, self.cluster[::-1]),0)) #last non-zero value

            if len(self.cluster[fv:lv]) <= self.threshold:   #distance between the first non-zero value and the last non-zero value
                return True
            else:
                return False
        elif self.type == "position" :
             
             mclus=self.cluster.copy()
             mclus.sort()
             if abs(self.cluster.index(mclus[-1])-self.cluster.index(mclus[-2]))<=self.threshold:
                return True
             else:
                 return False
        elif self.type == "ratio":
            
            fv=self.cluster.index(next(filter(lambda x: x!= 0, self.cluster),0))

            lv= len(self.cluster)-self.cluster[::-1].index(next(filter(lambda x: x!= 0, self.cluster[::-1]),0))

            if sum(self.cluster)/len(self.cluster[fv:lv]) <= self.threshold:
                return True
            else:
                return False
    def hyp_t(self,type): #Hypothesis test

        bins,vmin,vmax=0,0,0  #variables used for histogram in results.py

        self.bins=bins
        self.vmin=vmin
        self.vmax=vmax
        self.type=type

        s_sng = [] 
        s_bkg = []
        
        if self.type=="integral":
               
            for i in range(self.ngen):

                sq_max=max(self.tsng_list[i])
                bq_max=max(self.tbkg_list[i])

                sp_max=self.tsng_list[i].index(sq_max) #position of the highest charge in signal
                bp_max=self.tbkg_list[i].index(bq_max)  #position of the highest charge in background
                
                if sp_max == 0:
                    snq_max = self.tsng_list[i][sp_max+1]
                elif sp_max == len(self.tsng_list[i])-1:
                    snq_max = self.tsng_list[i][sp_max-1]
                else:
                    snq_max = max([self.tsng_list[i][sp_max-1],self.tsng_list[i][sp_max+1]])

                if bp_max == 0:
                    bnq_max = self.tbkg_list[i][bp_max+1]
                elif bp_max == len(self.tbkg_list[i])-1:
                    bnq_max = self.tbkg_list[i][bp_max-1]
                else:
                    bnq_max = max([self.tbkg_list[i][bp_max-1],self.tbkg_list[i][bp_max+1]])

                s_mclus=self.tsng_list[i].copy()
                s_mclus=[x - sq_max + snq_max for x in s_mclus]     

                b_mclus=self.tbkg_list[i].copy()
                b_mclus=[x - bq_max + bnq_max for x in b_mclus]         

                s_sng.append(sum(j for j in s_mclus if j > 0))
                s_bkg.append(sum(j for j in b_mclus if j > 0))

            self.bins=50
            self.vmin=0
            self.vmax=max( max([sum(self.tsng_list[i]) for i in range(len(self.tsng_list))]), max([sum(self.tbkg_list[i]) for i in range(len(self.tbkg_list))])) #autoscale

        elif self.type=="charge": 

            for i in range(self.ngen):

                s_sng.append(sum(self.tsng_list[i]))
                s_bkg.append(sum(self.tbkg_list[i]))

            self.bins=50
            self.vmin=0
            self.vmax=max( max([sum(self.tsng_list[i]) for i in range(len(self.tsng_list))]), max([sum(self.tbkg_list[i]) for i in range(len(self.tbkg_list))])) #autoscale
            
        elif self.type=="width":
            
            self.bins=self.r
            self.vmin=0
            self.vmax=self.r

            for i in range(self.ngen):
                
                fv_sng=self.tsng_list[i].index(next(filter(lambda x: x!= 0, self.tsng_list[i]),0))
                lv_sng= len(self.tsng_list[i])-self.tsng_list[i][::-1].index(next(filter(lambda x: x!= 0, self.tsng_list[i][::-1]),0))

                fv_bkg=self.tbkg_list[i].index(next(filter(lambda x: x!= 0, self.tbkg_list[i]),0))
                lv_bkg= len(self.tbkg_list[i])-self.tbkg_list[i][::-1].index(next(filter(lambda x: x!= 0, self.tbkg_list[i][::-1]),0))


                s_sng.append(len(self.tsng_list[i][fv_sng:lv_sng]))
                s_bkg.append(len(self.tbkg_list[i][fv_bkg:lv_bkg])) 
        
        elif self.type == "position":
            
            self.bins=self.r
            self.vmin=0
            self.vmax=self.r

            for i in range(self.ngen):

                s_mclus=self.tsng_list[i].copy()
                s_mclus.sort()

                b_mclus=self.tbkg_list[i].copy()
                b_mclus.sort()

                s_sng.append(abs(self.tsng_list[i].index(s_mclus[-1])-self.tsng_list[i].index(s_mclus[-2])))
                s_bkg.append(abs(self.tbkg_list[i].index(b_mclus[-1])-self.tbkg_list[i].index(b_mclus[-2])))
        
        elif self.type == "ratio":

            self.bins=25
            self.vmin=0
            self.vmax=self.b

            for i in range(self.ngen):
               
                fv_sng=self.tsng_list[i].index(next(filter(lambda x: x!= 0, self.tsng_list[i]),0))
                lv_sng= len(self.tsng_list[i])-self.tsng_list[i][::-1].index(next(filter(lambda x: x!= 0, self.tsng_list[i][::-1]),0))

                fv_bkg=self.tbkg_list[i].index(next(filter(lambda x: x!= 0, self.tbkg_list[i]),0))
                lv_bkg= len(self.tbkg_list[i])-self.tbkg_list[i][::-1].index(next(filter(lambda x: x!= 0, self.tbkg_list[i][::-1]),0))


                s_sng.append(sum(self.tsng_list[i])/len(self.tsng_list[i][fv_sng:lv_sng]))
                s_bkg.append(sum(self.tbkg_list[i])/len(self.tbkg_list[i][fv_bkg:lv_bkg]))                

        return s_sng, s_bkg 
    
    def evaluate_performance(self, type):
        
        self.type=type
        if type == "integral":
            self.threshold=self.b*self.r
        elif type == "width" :
            self.threshold=self.r
        elif type== "charge" :
            self.threshold = self.b*self.r
        elif type == "ratio" :
            self.threshold = self.b
        elif type=="position" :
            self.threshold = self.r
        
        sng_e, bkg_r = [],[]
  
        tp,fp = 0,0  #true positive, false positive
        for i in range(self.threshold+1):  

            for j in range(self.ngen):

                if self.is_signal(self.type,self.tsng_list[j], i):
                    tp+=1
                    
                if self.is_signal(self.type,self.tbkg_list[j], i):
                    fp+=1
            # Append rates to lists
            sng_e.append(tp/self.ngen)
            bkg_r.append(1-fp/self.ngen)
            tp=0
            fp=0
        return sng_e, bkg_r
