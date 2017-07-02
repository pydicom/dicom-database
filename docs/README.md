# Dicom Database Documentation

## Overview
The Dicom Database application is intended to be a simple manager of dicom images.

## Deployment

 - [Setup](setup.md): Basic setup (download and install) of a new application.
 - [Configuration](config.md): How to configure the application before starting it up.
 - [Application](application.md): Details about the application infrastructure.
 - [Start](start.md): Start it up!
 - [Interface](interface.md): A simple web interface for monitoring batches.

## Module-specific Documentation

 - [Management](manager.md): an overview of controlling the application with [manage.py](../manage.py)
 - [Logging](logging.md): overview of the logger provided in the application
 - [Watcher](watcher.md): configuration and use of the watcher daemon to detect new DICOM datasets


## Steps in Pipeline

 - [Dicom Import](dicom_import.md): The logic for when a session directory is detected as finished by the Watcher.

