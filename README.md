# Fair warning, I am still learning all the technologies involved in this project. 

# LaikaTek
A "smart" dog feeder that uses a web application to add and store information about your pets, and the devices assigned to your pets. The device itself is controlled by a Raspberry Pi Pico W running MicroPython cfunctions. Instructions such as feeding times are sent from the web app to the device and sensor information is sent back to the web app tobe displayed for the user. The application uses the Flask framework with MariaDB running in a Docker muilti-container environment.

# Technologies used
- Python
- Docker
- Azure Key vault
- MariaDB
- flask
- sqlalchemy
- CSS (with SASS pre-processor)

# Helpful Docker commands

sudo docker-compose up --build # This creates the docker containers based on the docker-compose.yml file and starts the application.\
\
sudo docker-compose down # Shuts down the docker containers. Adding --remove-orphans removes stopped containers and is useful in development.\
\
sudo docker ps # Lists running docker containers. Adding the -a flag shows all containers including those that are not currently running.\


# Key vault 
Keys will be used to secure passwords used within the app for connection strings.

1. create a key vault
2. create a Role Assignment under Access control
    Access Control(IAM) > Role Assignments > Add
3. Update the keymaster.py file with appropriate information for your

More informtion  on Azure Key Vaults: https://learn.microsoft.com/en-us/cli/azure/keyvault?view=azure-cli-latest&WT.mc_id=Portal-Microsoft_Azure_KeyVault

# Completed items
- Built flask framework and templates
- Set up basic CSS
- Set up a multi-container environment to run the application in
- Launched the app successfully in the Docker environment with unsecure database connection
- Tested core app functions such as: new user creation, login, adding/editing a pet, and adding/editing a device

# To Do
### Web App
- Write micropython code for device functions
- Deploy code to micro-processor and test functions on device hardware
- Refine user session (i.e. set session durration)
- Separate functions in the app.py file into separate files
- Establish IoT connection between the web app and device
- Design and 3d print enclosure for device hardware and other parts for the dog food bowl
- Deploy completed application to cloud environment
- Clean of and organize functions using Separate files and directories
- Final testing

### Micropython functions to build
- Rotate motor
- Wifi sign in
- connec to to web app
- read food level sensor
- receive updates from web app

# Currently working on
- Setting up Mosquito MQTT broker
- configuring wifi setup gateway
- Building out functions to communicate istructions to device 
- Getting the Docker app to authenticate to the Azure Key vault
- Establishing a secure database connection using Azure keys


# Installation

Fork the code over to your local machine and run sudo docker-compose up --build
