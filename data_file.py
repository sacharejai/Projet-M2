from array import array
from ROOT import TFile, TTree
from data_simulation import ClusterSimulator


#Background signal = 2MIP
#Pure signal = MIP

class file:
    
    def cfile(name,ngen):

        simulator=ClusterSimulator("config1.json")
        f = TFile('data_root/'+name + '.root', "RECREATE")
        tsgn = TTree("tsgn", "sgn")
        tbkg = TTree("tbkg", "bkg")

        clusSize = simulator.r #to be link to data_simulation
        
        xsng = array('f',[0]*clusSize)
        xbkg = array('f',[0]*clusSize)
       
        tbkg.Branch("clus", xbkg, "xbkg[{0}]/F".format(clusSize))
        tsgn.Branch("clus", xsng, "xbkg[{0}]/F".format(clusSize))    
        
        #for i in range(clusSize):
        #    tbkg.Branch("clus_" + str(i), xbkg[i], "clus_" + str(i) + "/F")
        #    tsgn.Branch("clus_" + str(i), xsng[i], "clus_" + str(i) + "/F")
               

        for i in range(ngen):
            onemip = simulator.generate_MIP_cluster(2)
            for i in range(len(onemip)):
                xsng[i] = onemip[i]
            twomip = simulator.generate_2MIP_cluster(1)
            for i in range(len(onemip)):
                xbkg[i] = twomip[i]
            tsgn.Fill()
            tbkg.Fill()
        f.Write()
        f.Print()
        f.Close()   
