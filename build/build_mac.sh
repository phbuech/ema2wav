#!/bin/bash

echo "Starting"

# Go into the directory where this script lies
cd "$(dirname "$0")"

# Go one level up
cd ..

# Create the virtual environment
python3 -m venv ema_env

# Activate the virt environment and install the dependencies
source ema_env/bin/activate
pip install -r src/requirements.txt

# For building the app we will also need pyinstaller
pip install pyinstaller

# Go into src folder and build the app
cd src
pyinstaller --windowed --onedir --add-data="ema2wav_gui.ui:." ema2wav_app.py

# Zip the resulting app and copy it to the build folder on the toplevel of the project
cd dist
zip -r ema2wav_app_macos.zip ema2wav_app.app
cp ema2wav_app_macos.zip ../../bin/ema2wav_app_macos.zip

# Clean up
cd ..
rm -r build
rm -r dist
rm ema2wav_app.spec

echo "Finished"