'''

Copyright (c) 2017 Vanessa Sochat

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

'''

from celery.decorators import periodic_task
from celery import (
    shared_task, 
    Celery
)

from celery.schedules import crontab
from dicomdb.logger import bot
from dicomdb.apps.main.models import (
    Batch,
    Header,
    HeaderField,
    HeaderValue,
    Image
)

from dicomdb.settings import DICOMIMPORT_DELETE

from dicomdb.apps.main.utils import (
    add_batch_error,
    add_header_fields,
    change_status,
    save_image_dicom,
)


from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime
from dicomdb.apps.main.utils import (
    ls_fullpath
)
import os

from pydicom import read_file
from pydicom.errors import InvalidDicomError

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dicomdb.settings')
app = Celery('dicomdb')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@shared_task
def import_dicomdir(dicom_dir):
    '''import dicom directory manages importing a valid dicom set into the application,
    and is a celery job triggered by the watcher. Here we also flag (and disclude)
    images that have a header value that indicates pixel identifiers.
    '''
    if os.path.exists(dicom_dir):
        dicom_files = ls_fullpath(dicom_dir)
        bot.debug("Importing %s, found %s .dcm files" %(dicom_dir,len(dicom_files)))        
        
        # The batch --> the folder with a set of dicoms tied to one request
        dcm_folder = os.path.basename(dicom_dir)   
        batch,created = Batch.objects.get_or_create(uid=dcm_folder)
        batch.save()

        # Add in each dicom file to the series
        for dcm_file in dicom_files:
            try:
                # The dicom folder will be named based on the accession#
                dcm = read_file(dcm_file,force=True)
                dicom_uid = os.path.basename(dcm_file)

                # Create the Image object in the database
                # A dicom instance number must be unique for its batch
                dicom = Image.objects.create(batch=batch,
                                             uid=dicom_uid)

                # Save the dicom file to storage
                dicom = save_image_dicom(dicom=dicom,
                                         dicom_file=dcm_file) # Also saves

                # Add all header fields (for now not private)
                dicom = add_header_fields(instance=dicom,
                                          dicom=dcm)

                # Only remove files successfully imported
                if DICOMIMPORT_DELETE:
                    os.remove(dcm_file)

            # Note that on error we don't remove files
            except InvalidDicomError:
                message = "InvalidDicomError: %s skipping." %(dcm_file)
                batch = add_batch_error(message,batch)

            except KeyError:
                message = "KeyError: %s is possibly invalid, skipping." %(dcm_file)
                batch = add_batch_error(message,batch)


        # If there were no errors on import, we should remove the directory
        if not batch.has_error:

            if DICOMIMPORT_DELETE:
                os.rmdir(dicom_dir)

    else:
        bot.warning('Cannot find %s' %dicom_dir)
