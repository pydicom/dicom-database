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
 1. [Dicom Import](dicom_import.md): The logic for when a session directory is detected as finished by the Watcher.
 2. [Deidentify](deidentify.md): the defaults (and configuration) for the de-identification step of the pipeline. This currently includes just header fields, and we expect to add pixel anonymization.
 3. [Storage](storage.md): Is the final step to move the de-identified dicom files to OrthanCP and/or Google Cloud Storage.
