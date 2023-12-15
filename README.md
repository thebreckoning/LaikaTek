# Fair warning, I am still learning all the technologies involved in this project. 

# LaikaTek
A "smart" dog feeder that uses a web application to add and store information about your pets, and the devices assigned to your pets. The device itself is controlled by a Raspberry Pi Pico W running MicroPython cfunctions. Instructions such as feeding times are sent from the web app to the device and sensor information is sent back to the web app tobe displayed for the user. The application uses the Flask framework with MariaDB running in a Docker muilti-container environment. 

# Technologies used
### Languages
- Python
- MicroPython
- HTML
- CSS (with SASS pre-processor)
- Json
- Javascript
  
### Platforms
- Docker
- MariaDB
- Nginx
- Alpine Linux
- flask
- MQTT (Mosquitto)
- OctoPi 3d Print server

### Tools and gadgets
- Raspberry PI Pico W
- Raspberry Pi 3
- Ender 3 3D printer
- RGB1602 LCD screen
- 5V 4-Phase Stepper Step Motor + Driver Board ULN2003 with Drive Test Module
- HC-SR04 Ultrasonic Module Distance Measuring Transducer Sensor

### Software
- VSCode
- Thonny
- Fusion 360
- Ultimaker Cura
- ChatGPT
- OpenArt AI
    

# Helpful Docker commands

sudo docker-compose up --build # This creates the docker containers based on the docker-compose.yml file and starts the application.\
\
sudo docker-compose down # Shuts down the docker containers. Adding --remove-orphans removes stopped containers and is useful in development.\
\
sudo docker ps # Lists running docker containers. Adding the -a flag shows all containers including those that are not currently running.\


# Completed items
- Built flask web app framework and templates
- Set up basic CSS styling
- Set up a multi-container environment to run the application in
- Launched the app successfully in the Docker environment with unsecure database connection
- Tested core app functions such as: new user creation, login, adding/editing a pet, and adding/editing a device
- Establish IoT connection between the web app and device
- Instructions from the app on when to dispense are recieved on the device via MQTT message
- Sensor information successfully delivered from the device to the web application.
- Set up LCD screen to display time on device

# To Do
### Web App
- Refine and secure user sessions (i.e. set session durration)
- Separate functions in the app.py file into separate files
- Clean up unused functions and libraries
- Re-design dispenser mechanism to use an auger
- Add 3D print files to repository
  


# Installation

1. Fork the code over to a server running docker and run sudo docker-compose up --build

