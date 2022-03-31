# ema2wav-converter

### Installation instructions

* Install anaconda.

* Open Terminal, if necessary activate anaconda.

* Change into project directory.

* Create environment:

  `conda create --name ema_env python=3.9.7`

  Replace 3.9.7 by the python version you are working with.

* Activate the environment:

  `conda activate ema_env`

* Install packages:

  `pip3 install -r requirements.txt`
  
  
### Manual configuration

Use this section, if you code the configuration file yourself (for example by modifying the config.json found in the project directory) and do not use the GUI to create the configuration.

* Edit configuration in the file `config.json` or create your own configuration file as json:

  The configuration of the converter contains the following parameters:
  
  `include_audio`: true or false. Specifies whether the audio shall be included in the resulting wav file.
  
  `ema_device_info`: the model of the Carstens articulograph. So far, only AG50x possible. In future versions, older version will be supported.
  
  `export_to_csv`: true or false. Specifies whether the EMA data is exported in a separate csv file.
 
  `export_raw_ema`: true or false. Specifies whether the EMA data is exported raw, i.e., not interpolated and not scaled.
  
  `output_directory`: this is the output directory for the processed wav files with audio and position data and csv files. Separate subfolders will be created for wav and csv files.
  
  `ema_samplerate`: sample rate of the ema data in Hz, e.g., 1250.
 
  `ema_channels`: number of channels in the EMA data, e.g., 16.
  
  `audio_input_directory`: input directory containing the audio (wav) files for the conversion.
  
  `audio_samplerate`: sample rate of the audio in Hz, e.g., 48000.
  
  `audio_channels`: number of channels in the audio file, e.g., 1.
  
  `channel_allocation`: the AG channels in your pos data. Format follows the sheme `parameter name : channel number`. For  example:
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
   `parameters_of_interest`: the parameters you want to include in the converted wav file.
   * specify pairs of a key containing the channel and a parameter, e.g. "0_ttip" : "y" converts the y-dimension of the tongue tip channel (make sure you use the names from "channel_allocation" above).
   * use a unique number and underscore before the channel name, e.g. "0_ttip".
   * "x" or "y" choose the position dimension (horizontal or vertical)
   * "-vel" chooses the velocity (1st derivative), e.g., "y-vel" chooses the velocity of the vertical dimension.
   * "-acc" chooses the acceleration (2st derivative), e.g., "y-acc" chooses the acceleration of the vertical dimension.
   * "tvel" chooses the tangential velocity of the parameter.
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
  
  `filter`: configure the filter to smooth the data:
  * `moving_average` to smooth the data with a rolling mean. Also specify window width, e.g., `"moving_average" : 10` for a rolling mean with a window of 10 data points.
  * `butter` to smooth the data using a butterworth filter. Also specify the cutoff frequency and order, e.g., `"filter" = { "butter_lowpass_filter" : [ 25.0, 4.0 ] }`


### Executing the conversion

Before running the conversion, make sure you place your data in the input folder (or change path in config file). Use a wav subdirectory for audio files and a pos subdirectoy for the EMA data. Output will be saved in configured output folder.

#### From command line

Run the conversion from the command line by calling the convert.py script. This command takes one argument, namely the path to the configuration file. For example when you config file is config.json in the project directory.

```python3 convert.py config.json```

#### Import as python module

You can import the converter as a python module and then call the conversion with a configuration file:

```
import ema2wav_module as em
config_file = "/path/to/your/config_file.json"
em.ema2wav_conversion(config_file)
```






