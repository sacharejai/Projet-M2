import ROOT
from ROOT import TMVA, TFile, TH1F, TCanvas, kRed, kBlue
from training import train
from simple_algorithm import SimpleAlgo
import array
import json

anwser="n"  #Default value


def comparison(name,type,ngen,epoch,batch): #type = integrer

    #RNN
    training=train()
    T=training.execute(type , batch, epoch, ngen,name,1) #Default value : use_type=3 , batchSize=100, maxepochs=10, name='',method=1
    use_type=training.use_type


    #Plot

    roc_curve = T[0].GetROCCurve(T[1])
    roc_curve.Draw()
    roc_curve.Update()  # Necessary to ensure the canvas is fully drawn

   #Simple Algo plot
    algo = SimpleAlgo(name,ngen)

    sng_e, bkg_r = algo.evaluate_performance("width") #change width to whatever hypothesis test variables you want
    
    sum=0
    for i in range(len(sng_e)-1):

        delta_x = sng_e[i + 1] - sng_e[i]
        delta_y = (bkg_r[i] + bkg_r[i + 1]) / 2.0
        sum += delta_x * delta_y


    #Add Simple Algo results

    graph = ROOT.TGraph(len(sng_e), array.array('d', sng_e), array.array('d', bkg_r))
    graph.SetLineColor(4)
    graph.SetLineWidth(2)
    graph.Draw("SAME")

    legend = ROOT.TLegend(0.15, 0.3, 0.32, 0.36)
    legend.AddEntry(graph, 'width_hyp', "l")
    legend.Draw()
    roc_curve.Update()

    # Calculate and display AUC values
    rnn_types = ["TMVA_RNN", "TMVA_LSTM", "TMVA_GRU"]
    use_rnn_type = [1, 1, 1]

    auc_text = ROOT.TLatex()
    auc_text.SetTextSize(0.03)
    auc_text.SetTextColor(ROOT.kBlack)

    if 0 <= use_type < 3:
        use_rnn_type = [0, 0, 0]
        use_rnn_type[use_type] = 1

    for i in range(3):
        if use_rnn_type[i]:
            auc = T[0].GetROCIntegral(T[1], rnn_types[i])
            auc_text.DrawLatex(0.37, 0.1 + i * 0.04, f'AUC for {rnn_types[i]}: {auc:.4f}')
    
    auc_text.DrawLatex(0.37, 0.1 + 3 * 0.04, f'AUC for width: {sum:.4f}')    

    roc_curve.Update()
    roc_curve.Print('prints/ROC_data_'+name+'.png')

def hist_hyp(name,type,ngen): #type = "integral" ; "charge" ; "width" ; "position"; "ratio"

        hyp = SimpleAlgo(name, ngen) #name , ngen
        s_sng, s_bkg = hyp.hyp_t(type)

        c2 = TCanvas()

        h1 = TH1F('h1', '',hyp.bins, hyp.vmin, hyp.vmax)
        h2 = TH1F('h2', '', hyp.bins, hyp.vmin, hyp.vmax)

        for j in s_sng:
            h1.Fill(j)
        for j in s_bkg:
            h2.Fill(j)

        h2.SetLineColor(kBlue)
        h2.SetFillColorAlpha(kBlue, 0.5)
        h2.SetFillStyle(3005)

        h1.SetLineColor(kRed)
        h1.SetFillColorAlpha(kRed, 0.5)
        h1.SetFillStyle(3004)


        h1.Draw()
        h2.Draw('same')
        legend = ROOT.TLegend(0.1, 0.75, 0.3, 0.9)  # Adjust the coordinates for top left position
        legend.SetFillStyle(3001)
        legend.AddEntry(h1, "signal", "f")
        legend.AddEntry(h2, "background", "f")


        legend.Draw()
        c2.Draw()
        c2.Print("prints/Hyp_" +type +'_'+ name + '.png')

name="TEST"
ngen=1000
T=["integral" , "charge" , "width" , "position", "ratio"]

for i in T:
    hist_hyp(name,i,ngen)
    
comparison(name,3,ngen,50,100)

"""
print("By default only the ROC curves of the different RNN methods used will be displayed.")

anwser=input("Do you want to have access to hypothesis tests and plot their respective ROC curves ? (y/n) :")


if anwser=='y':
    hyp=input("Type which element(s) you want to observe (use space to seperate elemens) : integral | charge | width | postion | ratio :")
    elements = hyp.split()
name = input("Please enter a file name :")
ngen = int(input("Please enter the number of samples :"))

bits=[63,255,1023]  #Bits to use in the ADC
resol=[10,30,100]   #Resolution of the clusters
epochs=[5,50,120]   #Epochs to use
batchs=[10,100,500] #Batch size to use

T=1 #change its value if you want to see the impact of the variables on the RNN methods, default: T=1
P=0 #change is value if you want to have ROC curve for the differents values of the variables, default: P=0


if bool(T):
    
    
    with open('config1.json', 'r') as file:
        data = json.load(file)

    data["b"] = bits[1]
    data["r"] = resol[0]

    with open('config1.json', 'w') as file:
        json.dump(data, file, indent=4) 

    file=name+"_b"+str(bits[1])+"_r"+str(resol[0])

    if anwser=="y":
        for i in elements:
            hist_hyp(file,i,ngen)

    comparison(file,3,ngen,epochs[1],batchs[1])

else: #Test all variables (will take a long time to run)

    L=["integral", "charge", "width","postion", "ratio"]

    for i in bits:

        with open('config1.json', 'r') as file:
            data = json.load(file)

        data["b"] = i

        with open('config1.json', 'w') as file:
            json.dump(data, file, indent=4) 

        for j in resol:
            
            with open('config1.json', 'r') as file:
                data = json.load(file)

            data["r"] = j

            with open('config1.json', 'w') as file:
                json.dump(data, file, indent=4) 
                
            file=name+"_b"+str(i)+"_r"+str(j)
            for m in L:
                hist_hyp(file,m,ngen)
            if bool(P):
                for k in batchs:
                    for l in epochs:
                        comparison(file,3,ngen,l,k)


tmvagui=input("Do you want to show TMVAGui to have access to all plots (/dataset/plots/) ? (y/n) :")
f=input("Enter the name of the file ('data_root/your_file_name') :")
h = ROOT.TFile(f, "READ")
h.Close()
import subprocess

if tmvagui == "y":
    # Command to execute
    command = 'root -l -e \'TMVA::TMVAGui('+f+')\''

    # Execute the command
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Command failed with return code {e.returncode}: {e}")"""


#Execute this line in a console to use TMVAGui

#root -l -e 'TMVA::TMVAGui("data_root/data_RNN_your_name.root")'
