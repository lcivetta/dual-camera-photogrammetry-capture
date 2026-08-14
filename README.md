# Dual-Camera Photogrammetry Capture

A Python/OpenCV desktop application for standardized dual-camera image acquisition used in photogrammetry-based 3D kidney stone reconstruction research.

![Application interface](assets/app-screenshot.png)

## Overview

This application was developed to simplify and standardize image collection from two cameras during a research workflow. It provides a desktop GUI for camera selection, live preview, automated image capture, and structured file output.

The tool was handed off with installation and usage documentation so researchers could run the image-acquisition workflow independently.

## Key Features

- Detects available camera inputs
- Lets the user select two different cameras
- Prevents duplicate camera selection
- Displays live previews from both cameras
- Captures images from both cameras in an automated sequence
- Collects 20 images per camera (40 total) at 5-second intervals
- Adds timestamps and camera-position labels to filenames
- Saves captures into a user-named folder in Downloads
- Includes refresh and restart controls for camera setup

## Tech Stack

- Python
- OpenCV (`cv2`) for camera access, frame capture, image conversion, and image saving
- Tkinter for the desktop user interface
- Pillow for displaying camera frames in the GUI
- Python threading for running the capture sequence without directly blocking the UI callback

## How It Works

1. The app scans for available cameras.
2. The user selects a camera for Position 1 and Position 2.
3. **Refresh Cam View** opens the selected cameras and starts the live preview.
4. The user enters a folder name.
5. **Start Taking Pictures** begins an automated capture sequence.
6. The program saves 20 images from each camera, one set every 5 seconds.
7. Files are saved with camera-position labels and timestamps in the selected folder under `~/Downloads`.

Example filenames:

```text
pos1_photo_1_YYYYMMDD_HHMMSS.png
pos2_photo_1_YYYYMMDD_HHMMSS.png
```

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/lcivetta/dual-camera-photogrammetry-capture.git
cd dual-camera-photogrammetry-capture
```

### 2. Create a virtual environment (recommended)

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

> Tkinter is included with many Python installations, but some environments may require it to be installed separately.

### 4. Run the application

```bash
python3 dual_camera_capture.py
```

## Platform Note

The current version opens cameras using OpenCV's `CAP_AVFOUNDATION` backend, so it was built for and tested in a macOS camera environment. Supporting Windows or Linux would require selecting an appropriate OpenCV video-capture backend.

## Research Context

The application supported image acquisition for a photogrammetry-based research pipeline associated with the peer-reviewed publication:

**A validated custom pipeline for three-dimensional kidney stone renderings to create an open access repository**

PubMed: https://pubmed.ncbi.nlm.nih.gov/42313154/

The broader research pipeline creates 3D kidney stone renderings and an open-access repository intended to support simulation and future computer-vision and machine-learning applications.

## Repository Structure

```text
dual-camera-photogrammetry-capture/
├── dual_camera_capture.py
├── requirements.txt
├── README.md
├── .gitignore
├── assets/
│   └── app-screenshot.png
└── docs/
    └── Camera_APP.pdf
```

## Notes

- The app currently saves output to the user's Downloads folder.
- The capture sequence is fixed at 20 images per camera with a 5-second interval.
- Camera enumeration currently checks indices 0-4.

## Author

Luca Civetta  
Biomedical Engineering, University of Michigan
