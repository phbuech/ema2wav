import os
import shutil
import numpy as np
import scipy
from scipy import signal
from scipy.io import wavfile
from mutagen.wave import WAVE
from mutagen.id3 import COMM
import json


#function definitions

def read_header(path_to_pos_file):
    pos_file = open(path_to_pos_file,mode="rb")
    file_content = pos_file.read()
    pos_file.seek(0)
    pos_file.readline()
    header_size = int(pos_file.readline().decode("utf8"))
    header_section = file_content[0:header_size]
    header = header_section.decode("utf8").split("\n")
    device = header[0].split("x")[0] +"x"
    num_of_channels = int(header[2].split("=")[1])
    ema_samplerate = int(header[3].split("=")[1])
    return ema_samplerate, num_of_channels, device


def create_folder(path):
    # creates a folder for the output data and deletes a folder with same name prior to folder creation
    if os.path.isdir(path):
        shutil.rmtree(path)
    os.mkdir(path)

def get_file_list(input_path, data_type):
    file_list = os.listdir(input_path)
    if data_type == "audio":
        files = [file_list[i] for i in range(len(file_list)) if file_list[i].endswith("wav") or file_list[i].endswith("WAV")]
    elif data_type == "ema":
        files = [file_list[i] for i in range(len(file_list)) if file_list[i].endswith("pos")]
    files.sort()
    return files

def read_pos_file(path_to_pos_file):
    #read file
    pos_file = open(path_to_pos_file,mode="rb")
    file_content = pos_file.read()

    #read header
    pos_file.seek(0)
    pos_file.readline()
    header_size = int(pos_file.readline().decode("utf8"))
    header_section = file_content[0:header_size]
    header = header_section.decode("utf8").split("\n")
    device = header[0]
    num_of_channels = int(header[2].split("=")[1])
    ema_samplerate = int(header[3].split("=")[1])
    
    #read data
    data = file_content[header_size:]
    if "AG50x" in device:
        data = np.frombuffer(data,np.float32)
        data = np.reshape(data,newshape=(-1,112))
    return ema_samplerate, num_of_channels, data


def extract_ema_data(data,ema_channels,sample_order):
    """
    extracts the ema data for the x and y dimensions for all recorded channels (see channel_allocation)
    """
    # initialize dictionary
    channel_names = list(ema_channels.keys())
    ext_data = {}
    for i in range(len(channel_names)): ext_data[channel_names[i]+"_x"] = []
    for i in range(len(channel_names)): ext_data[channel_names[i]+"_y"] = []


    for sample_idx in range(len(data)):
        sample = data[sample_idx]
        sample = np.reshape(sample,newshape=(-1,len(sample_order)))

        for channel_name_idx in range(len(channel_names)):

            # get sample values for x and y
            channel_number = ema_channels[channel_names[channel_name_idx]]
            this_channel_x_sample = sample[channel_number-1,sample_order["x"]]
            this_channel_y_sample = sample[channel_number-1,sample_order["y"]]

            # add values
            ext_data[channel_names[channel_name_idx]+"_x"].append(this_channel_x_sample)
            ext_data[channel_names[channel_name_idx]+"_y"].append(this_channel_y_sample)

    return ext_data

def mean_filter(data,N):
    return np.convolve(data,np.ones(N)/N,mode="same")

def butter_lowpass(cutoff, nyq_freq, order=4):
    normal_cutoff = float(cutoff) / nyq_freq
    b, a = signal.butter(order, normal_cutoff, btype='lowpass')
    return b, a

def butter_lowpass_filter(data, cutoff_freq, nyq_freq, order):
    # Source: https://github.com/guillaume-chevalier/filtering-stft-and-laplace-transform
    b, a = butter_lowpass(cutoff_freq, nyq_freq, order=order)
    y = signal.filtfilt(b, a, data)
    return y

def smoothing(data,signal_filter,ema_fs):
    filter_type = list(signal_filter.keys())[0]
    
    if filter_type == "butter":
        for i in range(len(data)): data[list(data.keys())[i]] = butter_lowpass_filter(data=data[list(data.keys())[i]], cutoff_freq=signal_filter["butter"][0], nyq_freq=ema_fs/2, order=signal_filter["butter"][1])
    elif filter_type == "moving_average":
        for i in range(len(data)): data[list(data.keys())[i]] = mean_filter(data=data[list(data.keys())[i]], N=signal_filter["moving_average"])
    return data

def derivation(data,ema_fs,order):
    x = np.linspace(0.0,len(data)/ema_fs,num=len(data))
    tmp = data
    dx = x[1]-x[0]
    for i in range(order):
        tmp = np.gradient(tmp,dx)
    return tmp

   

def extract_parameters_of_interest(data,poi,ema_fs):
    # initialize results dictionary
    ext_param_data = {}
    
    list_of_poi = list(poi.keys())

    for i in range(len(list_of_poi)):
        if len(list_of_poi[i].split("+")) == 1:
            if poi[list_of_poi[i]] == "x" or poi[list_of_poi[i]] == "y":
                channel_name = list_of_poi[i].split("_")[1]
                ext_param_data[list_of_poi[i]+"_"+poi[list_of_poi[i]]] = data[channel_name+"_"+poi[list_of_poi[i]]]
            elif poi[list_of_poi[i]] == "x-vel" or poi[list_of_poi[i]] == "y-vel":
                channel_name = list_of_poi[i].split("_")[1]
                dimension = poi[list_of_poi[i]].split("-")[0]
                ext_param_data[list_of_poi[i]+"_"+poi[list_of_poi[i]]] = derivation(data[channel_name+"_"+dimension],ema_fs=ema_fs,order=1)
            elif poi[list_of_poi[i]] == "x-acc" or poi[list_of_poi[i]] == "y-acc":
                channel_name = list_of_poi[i].split("_")[1]
                dimension = poi[list_of_poi[i]].split("-")[0]
                ext_param_data[list_of_poi[i]+"_"+poi[list_of_poi[i]]] = derivation(data[channel_name+"_"+dimension],ema_fs=ema_fs,order=2)
            elif poi[list_of_poi[i]] == "tvel":
                channel_name = list_of_poi[i].split("_")[1]
                tmp_data_x_vel = derivation(data=data[channel_name+"_x"],ema_fs=ema_fs,order=1)
                tmp_data_y_vel = derivation(data=data[channel_name+"_y"],ema_fs=ema_fs,order=1)
                ext_param_data[list_of_poi[i]+"_"+poi[list_of_poi[i]]] = np.sqrt(tmp_data_x_vel**2 + tmp_data_y_vel**2)
            elif poi[list_of_poi[i]] == "tvel-deriv":
                channel_name = list_of_poi[i].split("_")[1]
                tmp_data_x_vel = derivation(data=data[channel_name+"_x"],ema_fs=ema_fs,order=1)
                tmp_data_y_vel = derivation(data=data[channel_name+"_y"],ema_fs=ema_fs,order=1)
                tvel = np.sqrt(tmp_data_x_vel**2 + tmp_data_y_vel**2)
                ext_param_data[list_of_poi[i]+"_"+poi[list_of_poi[i]]] = derivation(data=tvel,ema_fs=ema_fs,order=1)

        elif len(list_of_poi[i].split("+")) == 2:
            if poi[list_of_poi[i]] == "eucl":
                # get articulators
                articulators = list_of_poi[i].split("_")[1]
                articulator1, articulator2 = articulators.split("+")
                articulator1_x = data[articulator1+"_x"]
                articulator1_y = data[articulator1+"_y"]
                articulator2_x = data[articulator2+"_x"]
                articulator2_y = data[articulator2+"_y"]
                ext_param_data[list_of_poi[i]] = np.array([np.sqrt((articulator1_x[j]-articulator2_x[j])**2+(articulator1_y[j]-articulator2_y[j])**2) for j in range(len(articulator1_x))] )
                
        
    return ext_param_data

def interpolate_data(data,s,wav_fs,ema_fs):
    interpolated_data = {}
    list_of_params = list(data.keys())
    for i in range(len(list_of_params)):
        tmp = data[list_of_params[i]]
        ema_x = np.linspace(0,len(tmp)/ema_fs,num=len(tmp))
        tck = scipy.interpolate.splrep(ema_x,tmp)
        new_x = np.linspace(0,len(tmp)/ema_fs,num=round((len(tmp)/ema_fs)*wav_fs))
        interpolated_tmp_data = scipy.interpolate.splev(new_x,tck)
        sample_diff = len(s) - len(interpolated_tmp_data)
        interpolated_tmp_data = interpolated_tmp_data.tolist() + [interpolated_tmp_data[len(interpolated_tmp_data)-1] for k in range(0,sample_diff)]
        interpolated_tmp_data = np.array(interpolated_tmp_data,dtype=np.float32)
        interpolated_data[list_of_params[i]] = interpolated_tmp_data
    return interpolated_data


'''Method to write information about channels to metadata of wav file as ID3 tag'''
def write_channels_to_metadata(output_file_path, selected_params):
    # Read audio file
    audio_file = WAVE(output_file_path)
    
    # Compile info about channels using selected_params (Ch1: xxx, Ch2: yyy, ...)
    channel_info = ""
    for i in range(len(selected_params)):
        if (i > 0):
            channel_info = channel_info + ", "
        channel_info = channel_info + "Ch" + str(i+1) + ": " + selected_params[i]

    # Add tags to the audio file in comments and save
    audio_file.add_tags()
    audio_file.tags.add(COMM(encoding = 3, lang = "ENG", desc = "Channel info", text = channel_info))
    audio_file.save()



def export_to_wav(output_file_path,data,fs,s,incl_wav,raw_ema):
    if incl_wav == True:
        tmp = [s]
    else:
        tmp = []
    list_of_params = list(data.keys())
    for i in range(len(list_of_params)):
        if raw_ema == False:
                ttmp = data[list_of_params[i]]  
        else:
            ttmp = data[list_of_params[i]]
        tmp.append(ttmp)

    # resample audio to 16kHz
    for i in range(len(tmp)):
        new_sample_number = round(len(tmp[i]) * float(16000) / fs) 
        tmp[i] = signal.resample(tmp[i],new_sample_number)
    output = np.array(tmp)
    output = output.T
    
    #write wav file with 16 kHz samplerate
    wavfile.write(output_file_path,16000,output)
    
    write_channels_to_metadata(output_file_path, list_of_params)

def export_to_csv(path,data,ema_fs):
    output_csv = open(path,encoding="utf8",mode="a")
    data_columns = list(data.keys())
    #create header
    header_columns = ["_".join(data_columns[i].split("_")[1:]) for i in range(len(data_columns))]
    
    header = "Time,"+ ",".join(header_columns) +"\n"
    output_csv.write(header)
    for line_idx in range(len(data[data_columns[0]])):
        line = str(line_idx*(1/ema_fs))
        for column_idx in range(len(data_columns)): line += "," + str(data[data_columns[column_idx]][line_idx])
        line += "\n"
        output_csv.write(line)
    output_csv.close()

def ema2wav_conversion(path_to_config_json):
    # load config file
    json_config_file = open(path_to_config_json)
    json_config_data = json.load(json_config_file)

    """
    extract information for the conversion process
    necessary informations are:
    - EMA input folder
    - WAV input folder
    - Channel allocation
    - Parameters of interest
    - filter information
    - output folder
    export options:
    - export_audio_ema
    - export_to_csv
    - export_raw_ema
    """

    ema_input_directory = json_config_data["ema_input_directory"]
    audio_input_directory = json_config_data["audio_input_directory"]
    ema_channels = json_config_data["channel_allocation"]
    poi = json_config_data["parameters_of_interest"]
    ema_filter = json_config_data["filter"]
    output_directory = json_config_data["output_directory"]

    export_audio_ema = json_config_data["export_audio+ema"]
    is_csv_export = json_config_data["export_to_csv"]
    is_raw_ema = json_config_data["export_raw_ema"]

    # create emawav output folder
    emawav_path = output_directory + "emawav/"
    create_folder(emawav_path)
    #create raw ema folder if necessary
    emawav_raw_path = output_directory + "raw_ema/"
    if is_raw_ema: create_folder(emawav_raw_path)
    emacsv_path = output_directory + "emacsv/"
    if is_csv_export: create_folder(emacsv_path)

    # get list of files
    ema_file_list = get_file_list(ema_input_directory,"ema")
    wav_file_list = get_file_list(audio_input_directory,"audio")
    
    # get device information
    ema_fs, ema_num_of_channels, ema_device = read_header(ema_input_directory+ema_file_list[0])

    # adjust sample order
    if ema_device == "AG50x":
        sample_order = {"x" : 0, "z" : 1, "y" : 2, "phi" : 3, "t" : 4, "rms" : 5, "extra" : 6}

    # convert each ema file
    for file_idx in range(len(ema_file_list)):

        # read wave file
        wav_fs, wav_data = wavfile.read(audio_input_directory+wav_file_list[file_idx])

        # normalize audio
        # the normalized audio will be stored as 32 bit floats (same as ema data))
        wav_data = np.array((wav_data/np.max(np.abs(wav_data))),dtype=np.float32)
        

        
        
        # read ema file
        ema_fs, ema_num_of_channels, ema_data = read_pos_file(ema_input_directory+ema_file_list[file_idx])
        extracted_ema_data = extract_ema_data(data=ema_data, ema_channels=ema_channels, sample_order=sample_order)

        #apply filter (if any)
        if ema_filter != None:
            extracted_ema_data = smoothing(data=extracted_ema_data, signal_filter=ema_filter, ema_fs=ema_fs)
            
        extracted_parameters = extract_parameters_of_interest(data=extracted_ema_data, poi=poi, ema_fs=ema_fs)
        
        if export_audio_ema == True:
            int_data = interpolate_data(data=extracted_parameters,s=wav_data,wav_fs=wav_fs,ema_fs=ema_fs)
            export_to_wav(output_file_path=output_directory+"emawav/emawav_"+wav_file_list[file_idx],data=int_data,fs=wav_fs,s=wav_data,incl_wav=True,raw_ema=False)
        else:
            export_to_wav(output_file_path=output_directory+"raw_ema/emawav_"+wav_file_list[file_idx],data=extracted_parameters,fs=wav_fs,s=wav_data,incl_wav=False,raw_ema=True)
        if is_raw_ema == True:
            export_to_wav(output_file_path=output_directory+"raw_ema/emawav_"+wav_file_list[file_idx],data=extracted_parameters,fs=wav_fs,s=wav_data,incl_wav=False,raw_ema=True)
        if is_csv_export == True:
            export_to_csv(path=output_directory+"emacsv/"+wav_file_list[file_idx].split(".")[0]+".csv", data=extracted_parameters,ema_fs=ema_fs)