from data_simulation import ClusterSimulator
import tensorflow
import os
import keras
import ROOT
from ROOT import TMVA, TFile
from data_file import file

#Classification

class Classification:
    
    def __init__(self, name , ngen, writeOutputFile=True):
        
        self.simulator=ClusterSimulator("config1.json")
        self.name=name
        self.ngen=ngen
        #Utilisation of GPU if avaible, else CPU is used
        self.useGPU = ROOT.gSystem.GetFromPipe("root-config --has-tmva-gpu") == "yes"
        self.archString = "GPU" if self.useGPU else "CPU"
        
        #Input file to use
        self.inputFileName = 'data_root/'+self.name +'.root'
        fileDoesNotExist = ROOT.gSystem.AccessPathName(self.inputFileName)
        
        #Checking if it does exist
        if fileDoesNotExist:
            file.cfile(self.name,self.ngen)

        self.inputFile = TFile.Open(self.inputFileName)
        if self.inputFile is None:
            raise ROOT.Error("Error opening input file %s - exit", self.inputFileName.Data())

        print("--- RNNClassification  : Using input file: {}".format(self.inputFile.GetName()))

        self.outfileName = "data_root/data_RNN_" + self.name + ".root"
        self.outputFile = None

        if writeOutputFile:
            self.outputFile = TFile.Open(self.outfileName, "RECREATE") 
    
    #RNN , LSTM, GRU    
    def tmva(self, use_type , batchSize, maxepochs, pB, pS): #Default values
        
        self.use_type=use_type
        self.batchSize=batchSize
        self.maxepochs=maxepochs
        self.pB=pB
        self.pS=pS        

        rnn_types = ["RNN", "LSTM", "GRU"]
        use_rnn_type = [1, 1, 1]
        
        if 0 <= self.use_type < 3:
            use_rnn_type = [0, 0, 0]
            use_rnn_type[self.use_type] = 1

        factory = TMVA.Factory(
            "TMVAClassification",
            self.outputFile,
            V=False,
            Silent=False,
            Color=True,
            DrawProgressBar=True,
            Transformations=None,
            Correlations=False,
            AnalysisType="Classification",
            ModelPersistence=True,
        )

        dataloader = TMVA.DataLoader("dataset")

        signalTree = self.inputFile.Get("tsgn")
        background = self.inputFile.Get("tbkg")

        ninputs = self.simulator.r 

        dataloader.AddVariablesArray("clus", ninputs)

        nTrainSig = self.pS * self.ngen
        nTrainBkg = self.pB * self.ngen

       # Apply additional cuts on the signal and background samples (can be different)
        mycuts = ""  # for example: TCut mycuts = "abs(var1)<0.5 && abs(var2-0.5)<1";
        mycutb = ""                                             
        
        dataloader.AddSignalTree(signalTree, 1.0)
        dataloader.AddBackgroundTree(background, 1.0)

        # build the string options for DataLoader::PrepareTrainingAndTestTree
        dataloader.PrepareTrainingAndTestTree(
            mycuts,
            mycutb,
            nTrain_Signal=nTrainSig,
            nTrain_Background=nTrainBkg,
            SplitMode="Random",
            SplitSeed=100,
            NormMode="NumEvents",
            V=False,
            CalcCorrelations=False,
        )
        
        
        for i in range(3):
                if not use_rnn_type[i]:
                    continue
        
                rnn_type = rnn_types[i]
        
                ## Define RNN layer layout
                ##  it should be   LayerType (RNN or LSTM or GRU) |  number of units | number of inputs | time steps | remember output (typically no=0 | return full sequence
                rnnLayout = str(rnn_type) + "|8|" + "1" + "|" + str(ninputs) + "|0|1,RESHAPE|FLAT,DENSE|64|TANH,LINEAR"
        
                ## Defining Training strategies. Different training strings can be concatenate. Use however only one
                trainingString1 = "LearningRate=1e-3,Momentum=0.0,Repetitions=1,ConvergenceSteps=5,BatchSize=" + str(self.batchSize)
                trainingString1 += ",TestRepetitions=1,WeightDecay=1e-2,Regularization=None,MaxEpochs=" + str(self.maxepochs)
                trainingString1 += "Optimizer=ADAM,DropConfig=0.0+0.+0.+0."
        
                ## define the inputlayout string for RNN
                ## the input data should be organize as   following:
                ##/ input layout for RNN:    time x ndim
                ## add after RNN a reshape layer (needed top flatten the output) and a dense layer with 64 units and a last one
                ## Note the last layer is linear because  when using Crossentropy a Sigmoid is applied already
                ## Define the full RNN Noption string adding the final options for all network
                rnnName = "TMVA_" + str(rnn_type)
                factory.BookMethod(
                    dataloader,
                    TMVA.Types.kDL,
                    rnnName,
                    H=False,
                    V=True,
                    ErrorStrategy="CROSSENTROPY",
                    VarTransform=None,
                    WeightInitialization="XAVIERUNIFORM",
                    ValidationSize=0.2,
                    RandomSeed=1234,
                    InputLayout=str(ninputs) + "|" + "1",
                    Layout=rnnLayout,
                    TrainingStrategy=trainingString1,
                    Architecture=self.archString
                )
        return [factory,dataloader,self.outputFile]
                
    #Keras
    def PyMVA(self, use_type=3 , batchSize=100, maxepochs=10, pB=0.8, pS=0.8): #Default values

        rnn_types = ["RNN", "LSTM", "GRU"]  #use_type = 0;1;2 (3=all)
        use_rnn_type = [1, 1, 1]
        
        if 0 <= use_type < 3:
            use_rnn_type = [0, 0, 0]
            use_rnn_type[use_type] = 1

        factory = TMVA.Factory(
            "TMVAClassification",
            self.outputFile,
            V=False,
            Silent=False,
            Color=True,
            DrawProgressBar=True,
            Transformations=None,
            Correlations=False,
            AnalysisType="Classification",
            ModelPersistence=True,
        )

        dataloader = TMVA.DataLoader("dataset")

        signalTree = self.inputFile.Get("tsgn")
        background = self.inputFile.Get("tbkg")

        ninputs = self.simulator.r #must be link to nb of cluster in data_simulation   

        dataloader.AddVariablesArray("clus", ninputs)

        nTrainSig = pS * self.ngen
        nTrainBkg = pB * self.ngen

       # Apply additional cuts on the signal and background samples (can be different)
        mycuts = ""  # for example: TCut mycuts = "abs(var1)<0.5 && abs(var2-0.5)<1";
        mycutb = ""                                             
        
        dataloader.AddSignalTree(signalTree, 1.0)
        dataloader.AddBackgroundTree(background, 1.0)

        # build the string options for DataLoader::PrepareTrainingAndTestTree
        dataloader.PrepareTrainingAndTestTree(
            mycuts,
            mycutb,
            nTrain_Signal=nTrainSig,
            nTrain_Background=nTrainBkg,
            SplitMode="Random",
            SplitSeed=100,
            NormMode="NumEvents",
            V=False,
            CalcCorrelations=False,
        )
        
        
        for i in range(3):
            if not use_rnn_type[i]:
                    continue
                    
            if use_rnn_type[i]:
                modelName = "model_" + rnn_types[i] + ".h5"
                trainedModelName = "trained_" + modelName
                print("Building recurrent keras model using a", rnn_types[i], "layer")
                # create python script which can be executed
                # create 2 conv2d layer + maxpool + dense
                from tensorflow.keras.models import Sequential
                from tensorflow.keras.optimizers import Adam
    
                # from keras.initializers import TruncatedNormal
                # from keras import initializations
                from tensorflow.keras.layers import Input, Dense, Dropout, Flatten, SimpleRNN, GRU, LSTM, Reshape, BatchNormalization
    
                model = Sequential()
                model.add(Reshape((ninputs,1), input_shape=(ninputs,)))
                # add recurrent neural network depending on type / Use option to return the full output
                if rnn_types[i] == "LSTM":
                    model.add(LSTM(units=10, return_sequences=True))
                elif rnn_types[i] == "GRU":
                    model.add(GRU(units=10, return_sequences=True))
                else:
                    model.add(SimpleRNN(units=10, return_sequences=True))
                # m.AddLine("model.add(BatchNormalization())");
                model.add(Flatten())  # needed if returning the full time output sequence
                model.add(Dense(64, activation="tanh"))
                model.add(Dense(1, activation="sigmoid"))
                model.compile(loss="binary_crossentropy", optimizer=Adam(learning_rate=0.001), weighted_metrics=["accuracy"])
                model.save(modelName)
                model.summary()
                print("saved recurrent model", modelName)
    
                if not os.path.exists(modelName):
                    print("Error creating Keras recurrent model file - Skip using Keras")
                else:
                    # book PyKeras method only if Keras model could be created
                    print("Booking Keras  model ", rnn_types[i])
                    factory.BookMethod(
                        dataloader,
                        TMVA.Types.kPyKeras,
                        "PyKeras_" + rnn_types[i],
                        H=True,
                        V=False,
                        VarTransform=None,
                        FilenameModel=modelName,
                        FilenameTrainedModel=trainedModelName,
                        NumEpochs=self.maxepochs,
                        BatchSize=batchSize,
                        GpuOptions="allow_growth=True",
                    )
        return factory



