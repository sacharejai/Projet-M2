# Projet-M2

# CMS_RNN
Recurrent Neural Network for CMS

##################################
###        DEPENDENCIES        ###
##################################

> python
> ROOT

##################################
###        ARCHITECTURE        ###
##################################

config1.json
|
|_ data_simulation.py
        |
        |_data_file.py 
        |         |
        |         |_simple_algorithm.py  ________________
        |         |                                      |         
        |         |_RNN.py                               |_results.py               
        |             |                                  |             
        |             |_training.py _____________________|
        |
        |_draw.py  

##################################
###        How to use it       ###
##################################

 Beforehand, you'll need to install python, ROOT and the packages used in 
the various files (time, numpy, random, json, array, matplotlib.pyplot, tensorflow, keras). 
Then you can launch "python results.py" in a console. 
Results.py can be personalize by the user to extract the desired plot(s).
