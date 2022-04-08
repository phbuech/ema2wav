# ema2wav-converter

*ema2wav* is a tool for converting data from electromagnetic articulography (EMA) into multi-channel wav files. The EMA data can be converteid either by executing a standalone Pythons script or by using a user-friendly GUI. The wav files can be opened in programs like [Praat](https://www.fon.hum.uva.nl/praat/) for further processing (display, annotation, measurements). Please read 3. before you use the files in Praat as this section presents some useful tips for good user experience with the data in Praat.

Three export options are available:
* wav file containing the audio signal and the EMA data (sampled to 16 kHz)
* wav file containing the EMA data only (samplerate of the EMA data)
* CSV file containing the EMA data (samplerate of the EMA daata)

The converter works with data from the AG500/501 models of [Carstens Medizinelektronik GmbH](https://www.articulograph.de/) at the moment.

We added executable files so you can run the converter in its GUI-version as every application on your computer:
* For macOS, download the dmg `ema2wav_app.dmg` in the `bin` subdirectory of this project. Copy the application to your applications folder or two another location and open it by double-clicking on the icon.

## 1. Installation instructions

This code has been developed and tested using Python 3.9, we recommend using this version of Python.

* Open the console (terminal)
* Navigate to the top level of the project directory.
* Create an environment for the converter. If you use anaconda, create the environment by the following code:

  `conda create --name ema_env python=3.9.7`

  Replace 3.9.7 by the python version you are working with.
  
  If you do not use anaconda, create the environment with the venv module:
  
  `python3 -m venv ema_env`

* Activate the environment. For anaconda, use this command:
  
  `conda activate ema_env` 
  
  If you use the `venv` module, activate the environment by running this line for Windows:
  
  `ema_env\Scripts\activate.bat`
  
  or for MacOS:
  
  `source ema_env/bin/activate`  

* Install packages:

  `pip3 install -r requirements.txt`
  
## 2. Usage
### 2.1 Configuration by GUI

Use this section, if you want to configure and execute the conversion using the GUI.

* Open the console
* Navigate to the `src` subdirectory of the project. That is where the source code is located.
* Run the following line to start the GUI:
  `python3 ema2wav_app.py`

* In order to start the conversion process, enter the following information into the GUI:
  * Directories of the POS and WAVE files:
  
    Press the `open EMA directory` and `open WAVE directory` buttons and selected the directories where the POS/WAVE files are located. Lists of these files and general informations will appear.
  
  * Channel allocation:

    Enter the necessary channels with their names and their number. In order to add a channel, press the `+` button. If a channel has to be deleted, left-click on the channel and remove it by pressing the `-` button.
  
  * Parameters of Interest:

    Enter the parameters you want to extract. The necessary information is 1. the name of the channel as it appears on the "Name" column in the "Channel allocation" table and 2. the parameter. For a list of the possible parameters, see "Manual configuration", `paramters_of_interest`.
  
  * Enter filter type:

    Select a moving average filter with the number of samples corresponding to the window size, or a Butterworth low pass filter with the cutoff frequency and the order, or none if you do not wish to filter / smooth the data.
  
  * Output directory:
 
    Select the output directory by pressing the `open` button.
  
  * Select export options:

    The export options are located above the `convert` button. You can choose between (1) WAVE files including the POS data and the audio signal ("include audio"), (2) WAVE files containing the POS data only ("export raw EMA"), (3) CSV files containing the POS data only. If (1) is selected, the resulting WAVE files have the same samplerate as original audio. If (2) or (3) is selected, the samplerate is the same as in the POS files.
  
* Start the conversion by pressing the `convert` button. 

* Output is produced in the selected output folder. The converted ema2wav files are in the subdirectory called `emawav`. 

* You will also find that a configuration file called `config.json` is created in the output folder. In this file, the configuration produced by the GUI is saved. If you would like to replicate an earlier conversion, you can load this configuration file or a different one from your disk and all necessary information is entered into the GUI fields. Open a configuration file by pressing the `load CONFIG` button and select the configuration file.
  
### Manual configuration

Use this section, if you code the configuration file yourself (for example by modifying the config.json found in the project directory) and do not use the GUI to create the configuration. After manual configuration, you can run the conversion from the command line or import the converter as a module into your own Python script (see below).

* Edit configuration in the file `config.json` or create your own configuration file as json:

  The configuration of the converter contains the following parameters:
  
  `export_audio+ema`: boolean (true or false). Specifies whether the audio shall be included in the resulting wav file. If true, the resulting file includes the audio. If false, the resulting file only contains the EMA data.
  
  `ema_device_info`: string. the model of the Carstens articulograph. So far, only AG50x possible. In future versions, older version will be supported.
  
  `export_to_csv`: boolean (true or false). Specifies whether the EMA data is exported in a separate csv file. The sampling rate of the csv file is the same as the EMA sampling rate.
 
  `export_raw_ema`: boolean (true or false). Specifies whether the EMA data is exported raw, i.e., not interpolated and not scaled.
  
  `output_directory`: string. This is the output directory for the processed wav files with audio and position data and csv files. Separate subfolders will be created for wav and csv files.
  
  `ema_input_directory`: string. Specifies the input directory of the POS-files (EMA data).
  
  `ema_samplerate`: number. Sample rate of the ema data in Hz, e.g., 250.
 
  `ema_channels`: number. Number of channels in the EMA data, e.g., 16.
  
  `audio_input_directory`: string. Input directory containing the audio (wav) files for the conversion.
  
  `audio_samplerate`: number. Sample rate of the audio in Hz, e.g., 48000.
  
  `audio_channels`: number. Number of channels in the audio file, e.g., 1.
  
  `channel_allocation`: JSON object. The AG channels in your pos data. Format follows the sheme `parameter name : channel number`. For  example:
     ```
     "channel_allocation" : {
        "rear" : 1,
        "lear" : 2,
        "nose" : 3,
        "chin" : 4,
        "tbo2" : 5,
        "tbo1" : 6,
        "ttip" : 7,
        "ulip" : 8,
        "llip" : 9
        }
     ```
   `parameters_of_interest`: JSON object. The parameters you would like to include in the converted wav file. Specify pairs the EMA-channel and the motion parameter, e.g. `"0_ttip" : "y"` converts the y-dimension of the tongue tip channel (make sure you use the names from "channel_allocation" above). Important notes:
   * use a unique number and underscore before the channel name (first element of pair), e.g. "0_ttip".
   * "x" or "y" choose the position dimension (horizontal or vertical)
   * "-vel" chooses the velocity (1st derivative), e.g., "y-vel" chooses the velocity of the vertical dimension.
   * "-acc" chooses the acceleration (2st derivative), e.g., "y-acc" chooses the acceleration of the vertical dimension.
   * "tvel" chooses the tangential velocity of the parameter.
   * "tvel-deriv" chooses the first derivative of the tangential velocity of the parameter.
   * "eucl" chooses the euclidean distance of the sensors. In this case, you need to specify two channels, e.g. "5_ulip+llip".
   
   An example:
   
   ```
     "parameters_of_interest": {
        "0_ttip": "y",
        "1_ttip": "y-vel",
        "2_ttip": "tvel",
        "3_ulip": "y",
        "4_llip": "y",
        "5_ulip+llip": "eucl"
      }
    ```
  
  `filter`: JSON object. Configure the filter to smooth the data:
  * `moving_average` to smooth the data with a rolling mean. Also specify window width, e.g., `"filter" = { "moving_average" : 10 }` for a rolling mean with a window of 10 data points.
  * `butter` to smooth the data using a butterworth filter. Also specify the cutoff frequency and order, e.g., `"filter" = { "butter_lowpass_filter" : [ 25.0, 4.0 ] }`
  * You can only apply one filter


### 2.2 Executing the conversion from command line or as Python module

Before running the conversion, make sure you placed your data in the input folders specified in the config (e.g., the demo input folder inside the `demo_data` subdirectory of the project directory). Output will be saved in configured output folder.

#### 2.2.1 From command line

cd to the `src` subdirectory of the project. Run the conversion from the command line by calling the convert.py script. This command takes one argument, namely the path to the configuration file. For example, when your config file is config.json in the `src` project directory, run the following in the command line:

```python3 convert.py config.json```

#### 2.2.2 Import as Python module

You can import the converter as a Python module and then call the conversion with a configuration file:

```
import ema2wav_module as em
config_file = "/path/to/your/config_file.json"
em.ema2wav_conversion(config_file)
```

## 3. Praat tweaks

The audio data and the POS data have different scales ([-1:1] for audio, higher scales for POS data) and this is also present in the WAVE files created by the conversion. As a result, audio or POS tracks can be difficult to identify and playing these files will lead to loud, uncomfortable noise, due to the higher scales of the POS data. In order to ensure a smooth experience when displaying and annotating the data in Praat, be sure to make the following changes in Praat's editor window:

* Mute POS channels.
  In the editor window, click on "View" and "Mute channels". Then select "ranges" for "channels to mute" and enter the channel numbers of the first and the last POS track
  
* Modify scaling
  In the editor window, click on "View" and "Sound scaling". Select "by window and channel" as "Scaling strategy"


## 4. TODO

* add a dropdown menu for the parameters of interest in the GUI
* add a progress bar
* create .exe and .dmg files
* extension to convert also data from the AG100/200 models of Carstens Medizinelektronik GmbH

## 5. Acknowledgements

This work has benefited/partially benefited from a government grant managed by the Agence Nationale de la Recherche under the "Investissements d'Avenir" programme with the reference ANR-10-LABX-0083 (contributing to the IdEx University of Paris - ANR-18-IDEX-0001, LABEX-EFL) and by the German Research Foundation (DFG) as part of the SFB1252 “Prominence in Language” (Project-ID 281511265), project A04 “Dynamic modelling of prosodic prominence” at the University of Cologne. 




