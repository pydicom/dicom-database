# Application
This application lives in a docker-compose orchestration of images running on your local machine. This application has the following components (each a Docker image):

 - **uwsgi**: is the main python application with Django (python)
 - **nginx**: is a web server to make a status web interface for Research IT
 - **worker**: is the same image as uwsgi, but configured to run a distributed job queue called [celery](http://www.celeryproject.org/). 
 - **redis**: is the database used by the worker, with serialization in json.

## Job Queue
The job queue generally works by processing tasks when the server has available resources. There will be likely 5 workers for a single application deployment. The worker currently serves one purpose, and this is likely to change. Until we have other methods for import, the worker will receive a job from the queue to run the [import dicom](import_dicom.md) task when a finished folder is detected by the [watcher](watcher.md). This would support import of images from a folder, and it should be done atomically so that a folder isn't detected until it is present in entirely.

## Models
The `dicom-database` models primarily robust details about image headers to be optimized for detailed searching of data.

 - Image: An image is a single dicom image with one or more headers
 - Batch: A grouping of images imported together, mainly for tracking status and logging
 - Header: a representation of a header object associated with a field and values
   - Field: A study is one or more images that are logically 
   - Value: A study is one or more images that are logically 


## Status
In order to track status of images, we have status states for images and batches.  Right now we only import, and if other functions are added, we can extend these statuses.


```
IMAGE_STATUS = (('NEW', 'The image was just added to the application.'),
               ('PROCESSING', 'The image is currently being processed, and has not been sent.'),
               ('DONE','The image has been imported.'))

BATCH_STATUS = (('NEW', 'The batch was just added to the application.'),
               ('PROCESSING', 'The batch currently being processed.'),
               ('DONE','The batch is done, and images are ready for cleanup.'))
```

## Errors
The most likely error would be an inability to read a dicom file, which could happen for any number of reasons. This, and generally any errors that are triggered during the lifecycle of a batch, will flag the batch as having an error. The variable `has_error` is a boolean that belongs to a batch, and a matching JSONField `errors` will hold a list of errors for the user. This error flag will be most relevant during cleanup.

For server errors, the application is configured to be set up with Opbeat. @vsoch has an account that can handle Stanford deployed applications, and all others should follow instructions for setup [on the website](opbeat.com/researchapps). It comes down to adding a few lines to the [main settings](dicomdb/settings/main.py). Opbeat (or a similar service) is essential for being notified immediately when any server error is triggered.


Now let's [start the application](start.md)!
