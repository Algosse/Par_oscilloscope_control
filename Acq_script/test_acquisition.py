# =============================================================================
# from Utils import oscilloscope_control as osc
from Utils import dictionnary_operation as dic
from Utils import test_vector as tv
from Utils import nucleo
import numpy as np
import os
import time
from serial import *

from PyQt5.QtCore import QThread, pyqtSignal
# =============================================================================

# =============================================================================
# class External(QThread):
#     
#     countChanged = pyqtSignal(float)
# 
# =============================================================================
def run(window):
    parameters = {}
    dic.load_dico('Acq_script/test_acquisition.dat', parameters)
    
# =============================================================================
# Creation of the file structure
# =============================================================================
    if not(os.path.exists("Acquisition/PAr116/" + parameters['date'])): # Test if analysis path exists
        os.makedirs("Acquisition/PAr116/" + parameters['date']) # Create the folder if needed
    os.chdir("Acquisition/PAr116/" + parameters['date']) # go to the analysis folder
    if not(os.path.exists(parameters['waveform_path'])): # Test if waveform folder exists
        os.makedirs(parameters['waveform_path']) # Create the folder if needed
    if os.path.exists('infos.dat'): # Test if info file exists
        dic.load_dico('infos.dat', parameters) # Update parameters if possible
# =============================================================================
# Creation or loading test vector
# =============================================================================
    key=tv.generate_key(**parameters) # Generate or load the key
    plaintext=tv.generate_plaintext(**parameters) # Generate or load plaintexts
    parameters['key generate'] = 0
    parameters['plaintext generate'] = 0
# =============================================================================
# Get trigger from dummy measurement on first measurement
# =============================================================================
    if parameters['get trigger']:
        window.oscilloscope.write("DAT:SOU " + window.ui.trig_sou.currentText()) # Change Data source of the oscilloscope
        window.oscilloscope.write("ACQ:STOPA SEQ")
        window.oscilloscope.write("ACQ:STATE ON")
        tmp = (window.oscilloscope.query("CURV?")).split(',') # Get trigger waveform from oscilloscope
        data = (';').join(tmp)
        with open(parameters['trigger_filename'] + '.' + parameters['file_extension'], 'a') as f:
            print(data, file=f, end='') 
        window.oscilloscope.write("DAT:SOU " + window.ui.data_sou.currentText()) # Change again the Data source to put measurement channel
        parameters['get trigger']=0 # Set get trigger to 0
        
# =============================================================================
# get Ymult from oscilloscope
# =============================================================================
    parameters['Ymult']=float(window.oscilloscope.query("WFMOutpre:YMUlt?"))

# =============================================================================
# Run AES and perform measurement
# =============================================================================
    
    
    
    
    with Serial(port='COM4',baudrate=115200,timeout=1,writeTimeout=1) as port_serie:
        time.sleep(2)
        for i in range(parameters['index'],parameters['nb_plain']):
            data=[]
            plain=str(plaintext[i][2:34])
            window.ui.log.append("XXXXXXXX"+plain)
            time.sleep(0.5)
            if port_serie.isOpen():
                port_serie.write(plain.encode('ascii'))
            
            for j in range(0, parameters['nb_curve']):
                # self.countChanged.emit((i*parameters['nb_curve']+j+1)/(parameters['nb_plain']*parameters['nb_curve'])*100)
                time.sleep(0.1)
    # =============================================================================
    #         osc.start_acquisition(oscillo) # Start oscilloscope acquisition
    # =============================================================================
                window.oscilloscope.write("ACQ:STOPA SEQ")
                window.oscilloscope.write("ACQ:STATE ON")
                try:
                    tmp = (window.oscilloscope.query("CURV?")).split(',') # Get trigger waveform from oscilloscope
                    data.append(list(map(int, tmp)))
                except:
                    j = j-1
                    window.ui.log.append("Waveform acquisition problem : plain " + str(i) + ", iteration " + str(j) + "\n")
                    with open("log.txt", "w") as log:
                        log.write(window.ui.log.toPlainText())
    # =============================================================================
    #         calcul de la moyenne des coubes
    # =============================================================================
            data=np.mean(data, axis=0)
            data=(';').join(list(map(str, data)))
            with open(parameters['waveform_path'] + "/" + parameters['wave_filename'] + "_" + str(i) + '.' + parameters['file_extension'], 'w') as f:
                print(data, file=f, end='')
            parameters['index']=i # Register new index to parameters in case the measurements fail
            dic.save_dico('infos.dat', **parameters) # Save parameters to restart if necessary
        
# =============================================================================
# Disconnexion of all peripherals and go back into main folder
# =============================================================================
    os.chdir('../../..') # Go back in parent folder
# =============================================================================
