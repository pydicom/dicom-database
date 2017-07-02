'''

Copyright (c) 2017 Vanessa Sochat, All Rights Reserved

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

from celery import shared_task, Celery
from celery.schedules import crontab

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.utils import timezone
from dicomdb.apps.base.utils import extract_tmp

from pydicom import read_file
from datetime import datetime
from itertools import chain
import os
import tempfile
import shutil


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dicomdb.settings')
app = Celery('dicomdb')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@shared_task
def validate_dicom_upload(file_path,remove_folder=False, force=True):
    '''ensure valid dicom 
    '''
    tmpdir = os.path.dirname(file_path)
    valid = False
    try:
        dicom = read_file(file_path,force=force)
        valid = True
    except:
        pass
    
    result = {'valid':valid,
              'file':file_path}

    if remove_folder == True:
        shutil.rmtree(tmpdir)

    return result


@shared_task
def dataset_upload(file_path,bid):
    '''dataset_upload will take an compressed file object, decompress
    it, (again) validate it for correctness, and then upload the dataset.
    '''
    from dicomdb.apps.main.utils import get_batch, upload_dicom_batch
    batch = get_batch(bid)
    tmpdir = os.path.dirname(file_path)
  
    # Add image and headers to batch
    image = upload_dicom_batch(batch=batch,
                               dicom_file=file_path)

    shutil.rmtree(tmpdir)


@shared_task
def batch_memory_upload(memory_file,batch):
    '''
    :param memory_file: the in memory uploaded file
    :param collection: the collection to add the uploaded dataset to
    '''
    data = {'is_valid': False, 'name': 'Invalid', 'url': ""}

    tmpdir = "%s/tmp" %settings.MEDIA_ROOT
    if not os.path.exists(tmpdir):
        os.mkdir(tmpdir)

    file_path = extract_tmp(memory_file,
                            base_dir=tmpdir)

    result = validate_dicom_upload(file_path)

    if result['valid'] == True:

        dataset_upload.apply_async(kwargs={"file_path": result['file'],
                                           "bid":batch.id })

        name = os.path.basename(result['file'])
        data = {'is_valid': True, 'name': name, 'url': batch.get_absolute_url()}

    else:
        tmpdir = os.path.dirname(result['file'])
        shutil.rmtree(tmpdir)

    return data
