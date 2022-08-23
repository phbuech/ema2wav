import sys
import os
from venv import create
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.uic import *

import json
from scipy.io import wavfile
import numpy as np
import ema2wav_core



# function defintion
def open_EMA_directory():
    #open dialog
    path = QFileDialog.getExistingDirectory()
    #add path of ema file to line
    w.ema_directory_line_edit.setText(path+"/")
    # filter file list
    try:
        file_list = os.listdir(path)
        ema_files = [file_list[i] for i in range(len(file_list)) if file_list[i].endswith(".pos")]
        ema_files.sort()
        
        model =  w.ema_files_view.model()
        # delete rows if any
        if model.rowCount() != 0:
            while (model.rowCount() > 0):
                model.removeRow(model.rowCount()-1)
        # add items to listview
        for i in ema_files:
            item = QStandardItem(i)
            model.appendRow(item)

        ema_fs, ema_channels, ema_device = ema2wav_core.read_header(w.ema_directory_line_edit.text()+ema_files[0])
        w.ema_device_info.setText(ema_device)
        w.ema_samplerate_info.setText(str(ema_fs)+" Hz")
        w.ema_channel_info.setText(str(ema_channels))
    except:
        err = QMessageBox()
        err.setIcon(QMessageBox.Critical)
        err.setText("Error")
        err.setInformativeText("No ema data found")
        err.setWindowTitle("Error")
        err.exec_()


def open_WAVE_directory():
    #open dialog
    path = QFileDialog.getExistingDirectory()
    #add path of ema file to line
    w.wave_directory_line_edit.setText(path+"/")
    # filter file list
    try:
        file_list = os.listdir(path)
        wave_files = [file_list[i] for i in range(len(file_list)) if file_list[i].endswith(".wav") or file_list[i].endswith(".WAV")]
        wave_files.sort()
        
        model = w.wave_files_view.model()
        
        # delete rows if any
        if model.rowCount() != 0:
            while (model.rowCount() > 0):
                model.removeRow(model.rowCount()-1)

        # add items to listview
        for i in wave_files:
            item = QStandardItem(i)
            model.appendRow(item)
    
        wave_fs, data = wavfile.read(path+"/"+wave_files[0])
        try:
            if len(data.shape) == 1:
                w.wave_channel_info.setText("1")
            elif len(data.shape) != 1:
                w.wave_channel_info.setText(str(data.shape[1]))
        except:
            pass
        w.wave_samplerate_info.setText(str(wave_fs) + " Hz")
        
    except:
        err = QMessageBox()
        err.setIcon(QMessageBox.Critical)
        err.setText("No wav files found")
        err.setWindowTitle("Error")
        err.exec_()

def open_output_directory():
    path = QFileDialog.getExistingDirectory()
    w.output_dir_line_input.setText(path+"/")





def channel_table_add_row():
    number_of_rows = w.channel_table.rowCount()
    w.channel_table.insertRow(number_of_rows)
    num_of_channels = w.ema_channel_info.text()
    if num_of_channels != "":
        num_of_channels = int(num_of_channels)
        
        channel_options = np.arange(1,num_of_channels+1,1)    
        comboBox = QComboBox()
        for i in range(len(channel_options)): comboBox.addItem(str(channel_options[i]))
                    
        w.channel_table.setCellWidget(number_of_rows,1,comboBox)
    

def parameter_table_add_row():
    number_of_rows = w.parameter_table.rowCount()
    num_of_channels = w.channel_table.rowCount()
    if num_of_channels != 0:
        w.parameter_table.insertRow(number_of_rows)
        channel_names = [w.channel_table.item(i,0).text() for i in range(num_of_channels)]
        number_of_names = len(channel_names)
        for i in range(number_of_names):
            for ii in range(number_of_names):
                if channel_names[i] != channel_names[ii] and channel_names[ii]+"+"+channel_names[i] not in channel_names:
                    channel_names.append(channel_names[i]+"+"+channel_names[ii])
        params = ema2wav_core.allowed_params
        channel_name_comboBox = QComboBox()
        for i in range(len(channel_names)): channel_name_comboBox.addItem(str(channel_names[i]))
        w.parameter_table.setCellWidget(number_of_rows,0,channel_name_comboBox)
        params_comboBox = QComboBox()
        for i in range(len(params)): params_comboBox.addItem(str(params[i]))
        w.parameter_table.setCellWidget(number_of_rows,1,params_comboBox)

    


def channel_table_remove_row():
    current_row = w.channel_table.currentRow()
    if current_row != -1:
        w.channel_table.removeRow(current_row)
    else:
        pass

def parameter_table_remove_row():
    current_row = w.parameter_table.currentRow()
    if current_row != -1:
        w.parameter_table.removeRow(current_row)
    else:
        pass




#filter setup

def enable_moving_average():
    #disable other filters
    w.no_filter_radio_btn.setChecked(False)
    w.butter_lp_btn.setChecked(False)
    w.butter_lp_cutoff_input.setEnabled(False)
    w.butter_lp_cutoff_input.setText("cutoff")
    w.butter_lp_order_input.setEnabled(False)
    w.butter_lp_order_input.setText("order")

    #enable 
    w.moving_average_btn.setChecked(True)
    w.moving_average_window_input.setEnabled(True)

def enable_no_filter():
    #disable other filters
    w.moving_average_btn.setChecked(False)
    w.moving_average_window_input.setEnabled(False)
    w.moving_average_window_input.setText("window size")

    w.butter_lp_btn.setChecked(False)
    w.butter_lp_cutoff_input.setEnabled(False)
    w.butter_lp_cutoff_input.setText("cutoff")
    w.butter_lp_order_input.setEnabled(False)
    w.butter_lp_order_input.setText("order")

    #enable
    w.no_filter_radio_btn.setChecked(True)

def enable_butter_filter():
    #disable other filters
    w.moving_average_btn.setChecked(False)
    w.moving_average_window_input.setEnabled(False)
    w.moving_average_window_input.setText("window size")

    w.no_filter_radio_btn.setChecked(False)

    #enable
    w.butter_lp_btn.setChecked(True)
    w.butter_lp_cutoff_input.setEnabled(True)
    w.butter_lp_order_input.setEnabled(True)



def collect_conversion_information():
    conversion_dict = {}
    

    #output parameters
    conversion_dict["export_audio+ema"] = w.export_audio_ema_checkbox.isChecked()
    conversion_dict["ema_device_info"] = w.ema_device_info.text()
    conversion_dict["export_to_csv"] = w.export_csv_checkbox.isChecked()
    conversion_dict["export_raw_ema"] = w.export_raw_ema_checkbox.isChecked()
    conversion_dict["output_directory"] = w.output_dir_line_input.text()


    #get ema file input
    conversion_dict["ema_input_directory"] = w.ema_directory_line_edit.text()
    conversion_dict["ema_samplerate"] = int(w.ema_samplerate_info.text().split(" ")[0])
    conversion_dict["ema_channels"] = int(w.ema_channel_info.text())

    #get audio file input
    if w.export_audio_ema_checkbox.isChecked() == True:
        conversion_dict["audio_input_directory"] = w.wave_directory_line_edit.text()
        conversion_dict["audio_samplerate"] = int(w.wave_samplerate_info.text().split(" ")[0])
        conversion_dict["audio_channels"] = int(w.wave_channel_info.text())
    
    # collect channel allocation
    channel_rows = w.channel_table.rowCount()
    tmp_dict = {}
    for i in range(0,channel_rows): tmp_dict[w.channel_table.item(i,0).text()] = int(w.channel_table.cellWidget(i,1).currentText())
    conversion_dict["channel_allocation"] = tmp_dict

    # collect parameters of interest
    parameter_rows = w.parameter_table.rowCount()
    tmp_dict = {}
    for i in range(0,parameter_rows): tmp_dict[str(i)+"_"+w.parameter_table.cellWidget(i,0).currentText()] = w.parameter_table.cellWidget(i,1).currentText()
    conversion_dict["parameters_of_interest"] = tmp_dict

    # ema filter
    if w.no_filter_radio_btn.isChecked() == True:
        conversion_dict["filter"] = None
    elif w.moving_average_btn.isChecked() == True:
        conversion_dict["filter"] = {"moving_average" : int(w.moving_average_window_input.text())}
    elif w.butter_lp_btn.isChecked() == True:
        conversion_dict["filter"] = {"butter": [float(w.butter_lp_cutoff_input.text()),float(w.butter_lp_order_input.text())]}



    return conversion_dict


def create_error_list():
    #check input and display error message if necessary
    errors = []
    #check for input paths
    if w.ema_directory_line_edit.text() == "":
        errors.append("- No input path for EMA data")
    if w.wave_directory_line_edit.text() == "":
        errors.append("- No input path for audio data")
    
    #check for input files

    #EMA
    model = w.ema_files_view.model()
    print(model)
    number_of_ema_files = model.rowCount()
    if number_of_ema_files == 0:
        errors.append("- No EMA files found")
    
    #audio
    model = w.wave_files_view.model()
    number_of_wave_files = model.rowCount()
    if number_of_wave_files == 0:
        errors.append("- No audio files found")
    
    #check channel table
    rows = w.channel_table.rowCount()
    for i in range(0,rows):
        if w.channel_table.item(i,0) == None or w.channel_table.cellWidget(i,1).currentText() == None:
            errors.append("- Channel allocation error")
    
    #check channel allocation
    rows = w.channel_table.rowCount()
    channel_names = np.unique(np.array([w.channel_table.item(i,0) for i in range(rows)]),return_counts=True)[1]
    for i in range(len(channel_names)):
        if int(channel_names[i]) > 1:
            errors.append("- Channel allocation error:\n2 or more channels have the same name!")
            
    channel_numbers = np.unique(np.array([w.channel_table.cellWidget(i,1).currentText() for i in range(rows)]),return_counts=True)[1]
    for i in range(len(channel_numbers)):
        if int(channel_numbers[i]) > 1:
            errors.append("- Channel allocation error:\n2 or more channels have the same number!")
            

    #check parameter table
    rows = w.parameter_table.rowCount()
    for i in range(0,rows):
        if w.parameter_table.cellWidget(i,0).currentText() == None or w.parameter_table.cellWidget(i,1).currentText() == None:
            errors.append("- Parameter of Interest error")
    
    channel_names = np.array([w.parameter_table.cellWidget(i,0).currentText() for i in range(rows)])
    parameter_names = np.array([w.parameter_table.cellWidget(i,1).currentText() for i in range(rows)])
    
    for i in range(rows):
        if parameter_names[i] == "eucl" and "+" not in channel_names[i]:
            errors.append("- Euclidean distance can not be applied to a single channel!")
        elif parameter_names[i] != "eucl" and "+" in channel_names[i]:
            errors.append("- "+parameter_names[i] + " can only be extracted for a single channel!")


    if w.output_dir_line_input == None or w.output_dir_line_input.text() == "":
        errors.append("- No output directory selected")

    return errors


def conversion():
    
    errors = create_error_list()

    if len(errors) != 0:
        errbox = QMessageBox()
        errbox.setIcon(QMessageBox.Critical)
        if len(errors) == 1:
            errbox.setText("The following error was encountered:")
        elif len(errors) > 1:
            errbox.setText("The following errors were encountered:")
        line = "\n".join(errors)
        errbox.setInformativeText(line)
        errbox.setWindowTitle("Error")
        errbox.exec_()
    else:
        #collect parameters

        
        conversion_dictionary = collect_conversion_information()
        json_config = json.dumps(conversion_dictionary,indent=4)
        config_output = open(w.output_dir_line_input.text()+"config.json","w")
        config_output.write(json_config)
        config_output.close()
        ema2wav_core.ema2wav_conversion(w.output_dir_line_input.text()+"config.json")
        
        msgbox = QMessageBox()
        msgbox.setIcon(QMessageBox.Information)
        msgbox.setText("Files successfully converted")
        msgbox.exec_()
        
        
        

def load_config():
    try:
        path = QFileDialog.getOpenFileName()[0]
    
        #set path to the config file in config_dir_line_input
        w.config_dir_line_input.setText(path)

        #load json file
        config_file = open(path)
        config_data = json.load(config_file)

        keys = list(config_data.keys())
        if "export_audio+ema" in keys:
            w.export_audio_ema_checkbox.setChecked(config_data["export_audio+ema"])
        if "export_to_csv" in keys:
            w.export_csv_checkbox.setChecked(config_data["export_to_csv"])
        if "export_raw_ema" in keys:
            w.export_raw_ema_checkbox.setChecked(config_data["export_raw_ema"])
        if "ema_device_info" in keys:
            w.ema_device_info.setText(str(config_data["ema_device_info"]))
        if "ema_samplerate" in keys:
            w.ema_samplerate_info.setText(str(config_data["ema_samplerate"]) + " Hz")
        if "ema_channels" in keys:
            w.ema_channel_info.setText(str(config_data["ema_channels"]))
        if "output_directory" in keys:
            w.output_dir_line_input.setText(config_data["output_directory"])
        if "filter" in keys:
            if config_data["filter"] == None:
                enable_no_filter()
            else:
                filter_keys = list(config_data["filter"].keys())
                if "moving_average" in filter_keys:
                    enable_moving_average()
                    w.moving_average_window_input.setText(str(int(config_data["filter"]["moving_average"])))
                elif "butter" in filter_keys:
                    enable_butter_filter()
                    w.butter_lp_cutoff_input.setText(str(int(config_data["filter"]["butter"][0])))
                    w.butter_lp_order_input.setText(str(int(config_data["filter"]["butter"][1])))
        if "ema_input_directory" in keys:
            w.ema_directory_line_edit.setText(config_data["ema_input_directory"])
            try:
                file_list = os.listdir(w.ema_directory_line_edit.text())
                ema_files = [file_list[i] for i in range(len(file_list)) if file_list[i].endswith(".pos")]
                ema_files.sort()

                model =  w.ema_files_view.model()
                # delete rows if any
                if model.rowCount() != 0:
                    while (model.rowCount() > 0):
                        model.removeRow(model.rowCount()-1)
                # add items to listview
                for i in ema_files:
                    item = QStandardItem(i)
                    model.appendRow(item)
            except:
                err = QMessageBox()
                err.setIcon(QMessageBox.Critical)
                err.setText("Error")
                err.setInformativeText("No ema data found under this path")
                err.setWindowTitle("Error")
                err.exec_()
        if "audio_input_directory" in keys:
            w.wave_directory_line_edit.setText(config_data["audio_input_directory"])
            try:
                file_list = os.listdir(w.wave_directory_line_edit.text())
                wave_files = [file_list[i] for i in range(len(file_list)) if file_list[i].endswith(".wav") or file_list[i].endswith(".WAV")]
                wave_files.sort()

                model = w.wave_files_view.model()
                # delete rows if any
                if model.rowCount() != 0:
                    while (model.rowCount() > 0):
                        model.removeRow(model.rowCount()-1)
                # add items to listview
                for i in wave_files:
                    item = QStandardItem(i)
                    model.appendRow(item)
            except:
                err = QMessageBox()
                err.setIcon(QMessageBox.Critical)
                err.setText("No wave files found under this path")
                err.setWindowTitle("Error")
                err.exec_()
        if "audio_samplerate" in keys:
            w.wave_samplerate_info.setText(str(config_data["audio_samplerate"]) + " Hz")
        if "audio_channels" in keys:
            w.wave_channel_info.setText(str(config_data["audio_channels"]))
        if "channel_allocation" in keys:
            #clear channel table
            while (w.channel_table.rowCount() > 0):
                w.channel_table.removeRow(0)
            #add channels to channel table
            tmp = config_data["channel_allocation"]
            tmp_keys = list(tmp.keys())
            
            for i in range(len(tmp_keys)):
                w.channel_table.insertRow(i)
                w.channel_table.setItem(i,0,QTableWidgetItem(str(tmp_keys[i])))
                number_of_channels = config_data["ema_channels"]
                channel_options = np.arange(1,number_of_channels+1,1)  
                comboBox = QComboBox()
                for j in range(len(channel_options)): comboBox.addItem(str(channel_options[j]))
                w.channel_table.setCellWidget(i,1,comboBox)
                w.channel_table.cellWidget(i,1).setCurrentIndex(config_data["channel_allocation"][tmp_keys[i]]-1)
                
                    
        if "parameters_of_interest" in keys:
            #clear parameter table
            while (w.parameter_table.rowCount() > 0):
                w.parameter_table.removeRow(0)
            #add parameters of interest to parameter table
            tmp = config_data["parameters_of_interest"]
            tmp_keys = list(tmp.keys())
            for i in range(len(tmp_keys)):
                w.parameter_table.insertRow(i)
                channel_names = list(config_data["channel_allocation"].keys())
                number_of_names = len(channel_names)
                for j in range(number_of_names):
                    for jj in range(number_of_names):
                        if channel_names[j] != channel_names[jj] and channel_names[jj]+"+"+channel_names[j] not in channel_names:
                            channel_names.append(channel_names[j]+"+"+channel_names[jj])
                
                
                channel_name_comboBox = QComboBox()
                for j in range(len(channel_names)): channel_name_comboBox.addItem(str(channel_names[j]))
                w.parameter_table.setCellWidget(i,0,channel_name_comboBox)
                
                index = channel_name_comboBox.findText(tmp_keys[i].split("_")[1])
                w.parameter_table.cellWidget(i,0).setCurrentIndex(index)
                
                params = ema2wav_core.allowed_params
                
                params_comboBox = QComboBox()
                for j in range(len(params)): params_comboBox.addItem(str(params[j]))
                w.parameter_table.setCellWidget(i,1,params_comboBox)
                
                index = params_comboBox.findText(config_data["parameters_of_interest"][tmp_keys[i]])
                w.parameter_table.cellWidget(i,1).setCurrentIndex(index)
                
    except:
        pass


app = QApplication(sys.argv)

bundle_dir = getattr(sys, '_MEIPASS',
os.path.abspath(os.path.dirname(__file__)))
path_to_ui = os.path.abspath(os.path.join(bundle_dir, 'ema2wav_gui.ui'))
w = loadUi(path_to_ui)


#initialize file list
w.ema_files_view.setModel(QStandardItemModel())
w.wave_files_view.setModel(QStandardItemModel())

# initialize tables
w.channel_table.setColumnCount(2)
w.channel_table.setHorizontalHeaderLabels(["Name","Channel"])

w.parameter_table.setColumnCount(2)
w.parameter_table.setHorizontalHeaderLabels(["Name","Parameter"])


# directories
w.open_ema_dir_btn.clicked.connect(open_EMA_directory)
w.open_wave_dir_btn.clicked.connect(open_WAVE_directory)
w.open_output_directory_btn.clicked.connect(open_output_directory)

#button functionality for channel and parameter tables
w.add_channel_btn.clicked.connect(channel_table_add_row)
w.remove_channel_btn.clicked.connect(channel_table_remove_row)

w.add_parameter_btn.clicked.connect(parameter_table_add_row)
w.remove_parameter_btn.clicked.connect(parameter_table_remove_row)


#button functionality for buttons at the bottom

w.load_CONFIG_btn.clicked.connect(load_config)
#preview button follows

w.start_conversion_btn.clicked.connect(conversion)




# filter radio button functionality
w.moving_average_btn.clicked.connect(enable_moving_average)
w.no_filter_radio_btn.clicked.connect(enable_no_filter)
w.butter_lp_btn.clicked.connect(enable_butter_filter)

w.show()
sys.exit(app.exec_())
