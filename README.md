# 🎬 Pepper Cinema Assistant
This repository contains the full implementation of an interactive cinema assistant using the **Pepper humanoid robot**, aimed at exploring multimodal human-robot interaction in real-world public environments. The project showcases capabilities such as personalized movie recommendations, demographic-aware dialogue, spatial guidance, and seamless user experience through multimodal communication.

## 🚀 Features

- **Multimodal Interaction**  
  Pepper uses speech, gestures and tablet to communicate naturally with users.

- **Personalized Recommendations**  
  A graph-based recommendation engine suggests films and concessions based on user preferences and past interactions.

- **Navigation Assistance**  
  Pepper offers step-by-step navigation using a graph-based map of the cinema, guiding users to locations like screening rooms, restrooms, and ticket counters.

- **Adaptive Dialogue**  
  The robot adjusts its tone and interaction style depending on the user's age group (e.g., playful for children, formal for adults).

- **Persistent Knowledge Management**  
  Combines relational databases and knowledge graphs to store and reason over user history and cinema metadata.

- **Simulation & Deployment Ready**  
  Compatible with Choregraphe for simulation and can be adapted for real-world execution.LED feedback

## 📁 Project Structure
```plaintext
pepper-project/
├── animations/           # Custom animations and gesture sequences used by Pepper
├── checkpoints/          # Stored model checkpoints for the graph-based recommendations
├── classes/              # Core Python classes (e.g., recommendation logic, dialogue manager)
├── data/                 # Knowledge graphs and dataset for the traning of the graph model
├── tablet/               # Tablet UI layouts and related assets (e.g., images, actions)
├── topicsFiles/          # Choregraphe topics
├── README.md             # Project documentation
└── main.py               # Launch the full Pepper assistant interaction pipeline
```
## ⚙️ Setup Instructions

### 1. Clone the HRI Software Repository
```bash
git clone https://bitbucket.org/iocchi/hri_software.git
```
### 2. Install the docker
Follow all the instructions on the Readme.md of the hri_software repository
### 3. Clone this repository on the playground folder (you get it following point 2)
```bash
git clone https://github.com/your-username/pepper-cinema-assistant.git
 ```
### 4. Set Up the Docker Environment
Navigate to the Docker folder and execute:
```bash
cd hri_software/docker
./run.bash
```
### 5. Attach to the Docker Container
In a new terminal window:
```bash
docker exec -it pepperhri tmux a
```
This gives you access to multiple virtual terminals using tmux (naoqi, choregraphe, modim and playground).
### 6. Launch NAOqi (tmux)
```bash
./naoqi
```
### 7. Launch Choregraphe (tmux)
```bash
./choregraphe
```
You’ll need to activate Pepper using a license key from SoftBank Robotics
### 8. Load the animation for the Pepper Robot
- Go to **File → Import content → Folder** and choose for the animations directory in this repository.
- Go to **Connection** and press **Upload to the robot and Play**.
- Memorize the pepper port in **Edit→ Preferences → Virtual Robot**
### 9. Set Up the Tablet
Navigate to the Docker folder and execute:
```bash
./run_nginx.bash path/to/pepper-project/tablet
```
### 10. Launch MODIM (tmux)
```bash
export PEPPER_PORT=<your_pepper_port>
python ws_server.py -robot pepper
```
### 11. Install Requirements (tmux)
```bash
pip install tensorflow==1.14.0 \
    protobuf==3.6.1 \
    grpcio==1.23.0 \
    keras-applications==1.0.8 \
    keras-preprocessing==1.1.0 \
    mock==3.0.5 \
    enum34==1.1.10 \
    wrapt==1.11.2
```
### 12. Launch the main in playground (tmux)
```bash
python main.py --pport <your_pepper_port>
```
