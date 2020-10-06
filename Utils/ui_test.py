# -*- coding: utf-8 -*-
import time

# =============================================================================
#   Test functions
# =============================================================================
def vertival_test(window, ch):
    f=open("Test/Vertical_test_log_" + str(ch) + ".txt", "w")
    # Test oscilloscope connection : Required to continue
    try:
        connection=window.instrument_connect()
        f.write("Connection to oscilloscope : SUCCESS\n")
    except:
        f.write("Connection to oscilloscope : FAILED\n")
    if (connection==1):
        # Channel 1
        eval("window.ui.channel" + str((ch-1)%4+1) + ".setChecked(1)")
        eval("window.ui.channel" + str((ch-1+1)%4+1) + ".setChecked(0)")
        eval("window.ui.channel" + str((ch-1+2)%4+1) + ".setChecked(0)")
        eval("window.ui.channel" + str((ch-1+3)%4+1) + ".setChecked(0)")
        # Test position
        eval("window.ui.ch" + str(ch) + "_pos.setText('1.5000')")
        window.apply_vertical()
        time.sleep(1)
        test=float((window.oscilloscope.query("CH" + str(ch) + ":POS?")).rstrip())
        time.sleep(1)
        if (test==float(eval("window.ui.ch" + str(ch) + "_pos.text()"))):
            f.write("Channel " + str(ch) + " position : SUCCESS\n")
        else:
            f.write("Channel " + str(ch) + " position : FAILED==>\nCh" + str(ch) + "_pos ->" + eval("window.ui.ch" + str(ch) + "_pos.text()") + "; read from oscilloscope ->" + str(test) + "\n")
        window.ui.ch1_pos.setText("0")
        for i in range(0, eval("window.ui.ch" + str(ch) + "_sca.count()")):
            eval("window.ui.ch" + str(ch) + "_sca.setCurrentIndex(i)")
            window.apply_vertical()
            time.sleep(1)
            test=float((window.oscilloscope.query("CH" + str(ch) + ":SCA?")).rstrip())
            time.sleep(1)
            if (test==float(eval("window.ui.ch" + str(ch) + "_sca.currentText()"))):
                f.write("Channel " + str(ch) + " scale " + str(i) + " : SUCCESS\n")
            else:
                f.write("Channel " + str(ch) + " scale " + str(i) + " : FAILED==>\nCh" + str(ch) + "_pos ->" + eval("window.ui.ch" + str(ch) + "_sca.currentText()") + "; read from oscilloscope ->" + str(test) + "\n")
    window.instrument_disconnect()
    f.close()
    
def Trigger_test(window):
    f=open("Test/Trigger_test_log.txt", "w")
    # Test oscilloscope connection : Required to continue
    try:
        connection=window.instrument_connect()
        f.write("Connection to oscilloscope : SUCCESS\n")
    except:
        f.write("Connection to oscilloscope : FAILED\n")
    if (connection==1):
        window.ui.trig_lvl.setText('1.5000')
        window.apply_trigger()
        time.sleep(1)
        test=float((window.oscilloscope.query("TRIGger:A:LEVel?")).rstrip())
        time.sleep(1)
        if (test==float(window.ui.trig_lvl.text())):
            f.write("Trigger position : SUCCESS\n")
        else:
            f.write("Trigger position : FAILED --> " + window.ui.trig_lvl.text() + " --> " + str(test) + "\n")
        window.ui.trig_lvl.setText('0')
        for i in range(0, window.ui.trig_sou.count()):
            window.ui.trig_sou.setCurrentIndex(i)
            f.write("Trigger source channel " + str(i) + " :\n")
            for j in range(0, window.ui.trig_cou.count()):
                window.ui.trig_cou.setCurrentIndex(j)
                f.write("--> Trigger coupling " + str(j) + " :\n")
                for k in range(0, window.ui.trig_slo.count()):
                    window.ui.trig_slo.setCurrentIndex(k)
                    f.write("--> Trigger slope : " + str(k))
                    window.apply_trigger()
                    time.sleep(1)
                    slo=(window.oscilloscope.query("TRIGger:A:EDGE:SLOpe?")).rstrip()
                    time.sleep(1)
                    cou=(window.oscilloscope.query("TRIGger:A:EDGE:COUPling?")).rstrip()
                    time.sleep(1)
                    sou=(window.oscilloscope.query("TRIGger:A:EDGE:SOURCE?")).rstrip()
                    if (sou==window.ui.trig_sou.currentText()):
                        f.write("SUCCESS ")
                    else:
                        f.write("FAILED --> " + sou + " --> " + window.ui.trig_sou.currentText() + " ")
                    if (cou==window.ui.trig_cou.currentText()):
                        f.write("SUCCESS ")
                    else:
                        f.write("FAILED --> " + cou + " --> " + window.ui.trig_cou.currentText() + " ")
                    if (slo==window.ui.trig_slo.currentText()):
                        f.write("SUCCESS\n")
                    else:
                        f.write("FAILED --> " + slo + " --> " + window.ui.trig_slo.currentText() + "\n")
    window.instrument_disconnect()
    f.close()
    
def horizontal_test(window):
    f=open("Test/Horizontal_test_log.txt", "w")
    # Test oscilloscope connection : Required to continue
    try:
        connection=window.instrument_connect()
        f.write("Connection to oscilloscope : SUCCESS\n")
    except:
        f.write("Connection to oscilloscope : FAILED\n")
    if (connection==1):
        window.ui.channel1.setChecked(1)
        window.ui.channel2.setChecked(0)
        window.ui.channel3.setChecked(0)
        window.ui.channel4.setChecked(0)
        window.ui.hor_pos.setText('10')
        window.apply_vertical()
        window.apply_horizontal()
        time.sleep(1)
        test=float((window.oscilloscope.query("HOR:POS?")).rstrip())
        time.sleep(1)
        if (test==float(window.ui.hor_pos.text())):
            f.write("Horizontal position : SUCCESS\n")
        else:
            f.write("Horizontal position : FAILED --> " +  window.ui.hor_pos.text() + " --> " + str(test) + "\n")
        window.ui.hor_pos.setText('50')
        window.ui.channel1.setChecked(0)
        window.ui.channel2.setChecked(0)
        window.ui.channel3.setChecked(0)
        window.ui.channel4.setChecked(0)
        window.apply_vertical()
        for i in range(1, 5):
            eval("window.ui.channel" + str(i) + ".setChecked(1)")
            f.write('Test for ' + str(i) + ' activated channel :\n')
            window.apply_vertical()
            for s in range(0, window.ui.hor_sca.count()):
                window.ui.hor_sca.setCurrentIndex(s)
                window.apply_horizontal()
                f.write("Test Scale " + str(s) + " :\n")
                f.write("Resolution to test : " + str(window.ui.hor_res.count()) + "\n")
                for r in range(0, window.ui.hor_res.count()):
                    window.ui.hor_res.setCurrentIndex(r)
                    f.write("Test Résolution " + str(r) + " -->")
                    window.apply_horizontal()
                    time.sleep(1)
                    sca=float((window.oscilloscope.query("HORizontal:SCAle?")).rstrip())
                    time.sleep(1)
                    res=float((window.oscilloscope.query("HORizontal:MAIn:SAMPLERate?")).rstrip())
                    time.sleep(1)
                    if (sca==float(window.ui.hor_sca.currentText())):
                        f.write(" SUCCESS ")
                    else:
                        f.write(" FAILED --> " + str(sca) + " --> " + window.ui.hor_sca.currentText() + " ")
                    if (res==float(window.ui.hor_res.currentText())):
                        f.write(" SUCCESS\n")
                    else:
                        f.write(" FAILED --> " + str(res) + " --> " + window.ui.hor_res.currentText() + "\n")
    window.instrument_disconnect()
    f.close()