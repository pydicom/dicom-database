# Setup

This document will review basic setup of your dicom database. You will need root (sudo) permissions, and ideally the ability to serve a web application (via a Docker image). 

## Download
Before you start, you should make sure that you have Docker and docker-compose installed, and a complete script for setting up the dependencies for any instance [is provided](scripts/prepare_instance.sh). You should walk through this carefully to make sure everything completes, and importantly, to install docker you will need to log in and out. You should then clone the repo, and we recommend a location like `/opt`.

```
cd /opt
git clone https://www.github.com/pydicom/dicom-database
cd dicom-database
```

This will mean your application base is located at `/opt/dicom-database` and we recommend that your data folder (where your system process will add files) be maintained at `/opt/dicom-database/data`. You don't have to do this, but if you don't, you need to change the folder in the [docker-compose.yml](docker-compose.yml) to where you want it to be. For example, right now we map `data` in the application's directory to `/data` in the container, and it looks like this:

```
uwsgi:
  restart: always
  image: vanessa/dicom-database
  volumes:
    - ./data:/data
```

to change that to `/tmp/dcm` you would change that line to:

```
uwsgi:
  restart: always
  image: vanessa/dicom-database
  volumes:
    - /tmp/dcm:/data
```

You should next [configure](config.md) your application.
