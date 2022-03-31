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

* Edit configuration in the file `config.json`:

  The configuration of the converter contains the following parameters:
  
  1. `input_path`: this is the directory where the subfolder of your pos and wav data are located, defaults to input folder in project directory
  2. `output_path`: this is the output directory for the processed wav files with audio and position data and csv files
  3. `channels`: the AG channels in your pos data. Format follows the sheme `parameter name : channel number`. For example:
     ```
     "channels" : {
        "rear" : 1,
        "lear" : 2,
        "nose" : 3,
        "chin" : 4,
        "tbo2" : 5,
        "tbo1" : 6,
        "ttip" : 7,
        "ulip" : 8,
        "llip" : 9,
        "ch10" : 10,
        "ch11" : 11,
        "ch12" : 12,
        "ch13" : 13,
        "ch14" : 14,
        "ch15" : 15,
        "ch16" : 16
        }
  4. `selected_params`: the parameters you want to include in the converted wav file. For example:
      ```
      "selected_params" : [
            "tbo2-y",
            "tbo2-x"
      ]       
  5. `include_acoustics`: specify whether you would like to include the acoustic signal in the converted wav file (true or false)
  6. `raw_ema`: specify whether you would produce a converted wav file with raw ema (i.e., not interpolated and not scaled) in the converted wav file (true or false)
  7. `audio_fs`: specify the audio sampling rate, e.g., `48000` for 48000 Hz
  8. `export_csv`: specify wether pos data is also exported in a csv file (true or false)
  9. `signal_filter`: configure the filter to smooth the data:
 
      * `mean_filter` to smooth the data with a rolling mean. Also specify window width, e.g., `"mean_filter" : 10` for a rolling mean with a window of 10 data points
      * `butter_lowpass_filter` to smooth the data using a butterworth filter. Also specify the cutoff frequency, nyquist frequency and the order, e.g., `"signal_filter" = { "butter_lowpass_filter" : [20,250/2,4] }`
      

* Run the module:

`jupyter notebook ema2wav_converter.ipynb`

* Before running the conversion, make sure you place your data in the input folder (or change path in config file). Use a wav subdirectory for audio files and a pos subdirectoy for the EMA data.

* Output will be saved in configured output folder.
