
# PYTHON SCRIPT

Create python virtual environment then install all packages from [this file](requirements.txt)

Put images of people you need for verification in people folder and then run [this script](extract_embeddings.py)
This builds face embeddings based on the dataset given

then edit [this file](recognise_face_cam.py)

- line 10: edit people dict with the uid of your card and people names
- line 103 onwards: change MQTT connection details
- run file and it should work if your mosquitto broker is up

# ESP32

[In this file](esp32\esp32.ino) you need to change wifi and broker settings as well.
Install the following libraries:

- MFRC522v2.h
- MFRC522DriverSPI.h
- MFRC522DriverPinSimple.h
- WiFi.h
- PubSubClient.h

You also need to include the board manager for ESP32 boards
[Follow this tutorial for ArduinoIDE](https://randomnerdtutorials.com/installing-the-esp32-board-in-arduino-ide-windows-instructions/)
