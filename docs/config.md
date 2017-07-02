# Configuration
The configuration for the application consists of the files in the [dicomdb/settings](../dicomdb/settings) folder. The files that need attention are `secrets.py` and [config.py](../dicomdb/settings/config.py).  

## Application Secrets
First make your secrets.py like this:

```
cp dicomdb/settings/bogus_secrets.py dicomdb/settings/secrets.py
vim dicomdb/settings/secrets.py
```

Once you have your `secrets.py`, it needs the following added:

 - `SECRET_KEY`: Django will not run without one! You can generate one [here](http://www.miniwebtool.com/django-secret-key-generator/)
 - `DEBUG`: Make sure to set this to `False` for production.


## Dicom Import
Right now, the only setting to configure is whether you want the dicom files deleted after import from the `/data` (or other mapped) directory:

```
DICOMIMPORT_DELETE=False
```

It is currently set to False.


## Authentication
If you look in [dicomdb/settings/auth.py](../dicomdb/settings/auth.py) you will see something called `lockdown` and that it is turned on:

```
# Django Lockdown
LOCKDOWN_ENABLED=True
```

This basically means that the entire site is locked down, or protected for use (from a web browser) with a password. It's just a little extra layer of security. 

![img/dicom-database.png](img/dicom-database.png)


You can set the password by defining it in your [dicomdb/settings/secrets.py](../dicomdb/settings/secrets.py):

```
LOCKDOWN_PASSWORDS = ('mysecretpassword',)
```

Note that we choose a global lockdown over user accounts because this application is primarily intended for local use. If that changes, then the application needs to have user accounts re-enabled (it's all in place but would need views added, etc) and the server where it is deployed would need to be secured with https. The latter mostly comes down to changing the [nginx.conf](../nginx.conf) and [docker-compose.yml](../docker-compose.yml) to those provided in the folder [https](../https).

Next, you should read a bit to understand the [application](application.md).
