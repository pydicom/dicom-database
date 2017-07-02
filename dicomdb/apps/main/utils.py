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

from django.core.files import File
from django.http.response import (
    HttpResponseRedirect, 
    HttpResponseForbidden, 
    Http404
)
from django.shortcuts import (
    get_object_or_404, 
    render_to_response, 
    render, 
    redirect
)
from django.contrib.auth.models import User
from dicomdb.apps.main.models import (
    Batch,
    Header,
    HeaderValue,
    HeaderField
)
from dicomdb.settings import MEDIA_ROOT
from pydicom import read_file
import os


#### GETS #############################################################

def get_batch(sid):
    '''get a single report, or return 404'''
    keyargs = {'id':sid}
    try:
        batch = Batch.objects.get(**keyargs)
    except Batch.DoesNotExist:
        raise Http404
    else:
        return batch


def ls_fullpath(dirname,ext=None):
    '''get full path of all files in a directory'''
    if ext is not None:
        return [os.path.join(dirname, f) for f in os.listdir(dirname) if f.endswith(ext)]
    return [os.path.join(dirname, f) for f in os.listdir(dirname)]


### FILES ##############################################################

def save_image_dicom(dicom,dicom_file,basename=None):
    '''save image dicom will save a dicom file to django's media
    storage, for this application defined under /images.
    :param dicom: the main.Image instance 
    :param dicom_file: the dicom file (usually in /data) to save
    '''
    if basename is None:
        basename = os.path.basename(dicom_file)

    with open(dicom_file,'rb') as filey:
              django_file = File(filey)
              dicom.image.save(basename,
                               django_file,
                               save=True)  
    dicom.save()
    return dicom


## MODELS ##############################################################

def add_header_fields(instance,dicom=None,include_private=False):
    '''add header fields will add header field objects to be associated
    with an instance of a dicom Image in the database'''
    if dicom is None:
        dicom = read_file(instance.image.path)

    skip = ["PixelData"]

    fields = dicom.dir()
    if include_private:
        from deid.dicom.tags import get_private
        bot.debug("Private tags not yet implemented, not sure if good idea.")

    for field in fields:
        values = dicom.get(field)
        if values not in [None,''] and field not in skip:

            header_field,created = HeaderField.objects.get_or_create(field=field)
            if not isinstance(values,list):
                values = [values]
            for value in values:
                value_field,created = HeaderValue.objects.get_or_create(name=value)
                header,created = Header.objects.get_or_create(value=value_field, 
                                                              field=header_field)             
                header.save()   
                instance.headers.add(header)

    instance.save()
    return instance


def add_batch_error(message,batch):
    '''add batch error will log an error, and flag the batch to have it.
    '''
    bot.error(message)
    batch.has_error = True
    batch.errors.append(message)
    batch.save()
    return batch  


def change_status(images,status):
    '''change status will update an instance status
     to the status choice provided. This works for batch
    and images
    '''
    updated = []
    if not isinstance(images,list):
        images = [images]
    for image in images:
        image.status=status
        image.save()
        updated.append(image)
    if len(updated) == 1:
        updated = updated[0]
    return updated
