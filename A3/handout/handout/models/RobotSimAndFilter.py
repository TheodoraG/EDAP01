
import random
import numpy as np

from models import TransitionModel,ObservationModel,StateModel


#
# Add your Robot Simulator here
#
class RobotSim:
    def __init__(self,sm):
        self.__sm = sm
        self.__tm = TransitionModel(self.__sm)
        self.__om = ObservationModel(self.__sm)



    def movingStrategyNew(self,state):
        #get the transition matrix
        t = self.__tm.get_T()
        indexes  = np.nonzero(t[state,:])[0] #the neighbors states
        #probab=t[state,indexes]/sum(t[state,indexes])
        probab = t[state,indexes]
        #choose just one possible state/neighbor according to the probability
        chosen_state  = np.random.choice(indexes,1,p=probab)
        #return the chosen state/neighbor
        return chosen_state[0]


    def sensor(self,state):
        #get the probabilities for the sensor to have produced reading "reading" when in state "state"
        probab = [self.__om.get_o_reading_state(reading, state) for reading in range(self.__sm.get_num_of_readings())]
        #choose just one possible reading according to the probability
        returned_reading = np.random.choice(self.__sm.get_num_of_readings(),p=probab)
        
        #test if there is no sensor reading
        if returned_reading == self.__sm.get_num_of_readings() - 1:
            returned_reading = None
        
        return returned_reading
        
#

        
#
# Add your Filtering approach here (or within the Localiser, that is your choice!)
#


class HMMFilter:
    def __init__(self):
        print("Hello again, World")
    
    
    
    
        
        
        
