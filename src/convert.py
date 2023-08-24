import sys
import os
import ema2wav_core as em

config_file = sys.argv[1]
dir_name = os.path.dirname(__file__)

abs_pathname = os.path.abspath(config_file)

if os.path.exists(abs_pathname):
    em.ema2wav_conversion_terminal(config_file)
else:
    print("Configuration file not found.")
