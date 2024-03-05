from ROOT import TH1F, TCanvas, kBlue, kRed
from data_simulation import ClusterSimulator
import matplotlib.pyplot as plt

simulator=ClusterSimulator("config1.json")
ngen = 10
# draw the data simulation
print("")
print("------------------MIP--------------------------")
print("")
c2 = TCanvas()
c2 = TCanvas()
h = TH1F('h','',simulator.r,0,simulator.r)
for j in range(ngen):
    clus = simulator.generate_MIP_cluster(2)
    for i in range(len(clus)):
        h.SetBinContent(i+1,clus[i])
           
           
    h.SetLineColor(kRed)
    h.SetFillColorAlpha(kRed, 0.5) 
    h.SetFillStyle(3001) 
    
    h.Draw()
    c2.Update()
    c2.Modified()
    c2.Draw()
    c2.Print('clusters/clus_'+str(simulator.r)+'_MIP_'+str(j)+'.png')

print("")
print("--------------------2MIP---------------------------")
print("")
c2 = TCanvas()
h = TH1F('h','',simulator.r,0,simulator.r)
for j in range(ngen):
    clus = simulator.generate_2MIP_cluster(1)
    for i in range(len(clus)):
        h.SetBinContent(i+1,clus[i])
           
           
    h.SetLineColor(kBlue)
    h.SetFillColorAlpha(kBlue, 0.5) 
    h.SetFillStyle(3001) 
    
    h.Draw()
    c2.Update()
    c2.Modified()
    c2.Draw()
    c2.Print('clusters/clus_'+str(simulator.r)+'_2MIP_'+str(j)+'.png')


print("")
print("------------------END--------------------------")
print("")


for i in range(ngen):
    ###########
            
    # Initialisations pour le tracé
    plt.plot([0, simulator.w], [0, 0], 'k')  # Première droite
    plt.plot([0, simulator.w], [simulator.t, simulator.t], 'k')  # Deuxième droite
            
    # Tracer les droites et rectangles
    for i in range(simulator.r+1):
        plt.plot([i *(simulator.w/simulator.r), i *(simulator.w/simulator.r)], [0, simulator.t], 'k')  # Droites perpendiculaires
    L=simulator.charge(simulator.r,simulator.t,simulator.w,1)

    plt.plot(L[0], L[1], 'r-', linewidth=2)
    plt.xlabel('Width')
    plt.ylabel('Thickness')
    plt.savefig('trajectory_clus_'+str(simulator.r)+'_'+str(i)+'.png')
    plt.show()
    ############
