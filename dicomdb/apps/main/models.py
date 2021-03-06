'''
Images models. 

  Batch: a folder with a set of images associated with a C-MOVE query
  Image: one dicom image associated with a batch
  Header: field and value pairs associated with an image

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



from taggit.managers import TaggableManager
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.core.urlresolvers import reverse
from django.db.models.signals import m2m_changed
from django.db.models import Q, DO_NOTHING
from django.db import models
from django.conf import settings

import collections
import operator
import os


#######################################################################################################
# Supporting Functions and Variables ##################################################################
#######################################################################################################


def get_upload_folder(instance,filename):
    '''get_upload_folder will return the folder for an image associated with the ImageSet id.
    instance: the Image instance to upload to the ImageCollection
    filename: the filename of the image
    '''
    batch_id = instance.batch.id

    # This is relative to MEDIA_ROOT
    # /[ MEDIAROOT ] / [ BATCH ] / [ FILENAME ]

    return os.path.join(str(batch_id),filename)



IMAGE_STATUS = (('NEW', 'The image was just added to the application.'),
               ('PROCESSING', 'The image is currently being processed, and has not been sent.'),
               ('DONE','The image has been received, and is ready for cleanup.'))

BATCH_STATUS = (('NEW', 'The batch was just added to the application.'),
               ('PROCESSING', 'The batch currently being processed.'),
               ('DONE','The batch is done, and images are ready for cleanup.'))


ERROR_STATUS = ((True,'The batch had an error at some point, and errors should be checked'),
                (False, 'No error occurred during processing.'))


#################################################################################################
# Headers #######################################################################################
#################################################################################################


class HeaderValue(models.Model):
    '''A header value is one or more values associated with a field.
    '''
    name = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return "%s" %self.name

    def __unicode__(self):
        return "%s" %self.name
 
    def get_label(self):
        return "header-value"

    class Meta:
        app_label = 'main'


class HeaderField(models.Model):
    '''A header value is one or more values associated with a field.
    '''
    field = models.CharField(max_length=128)
    value = models.ManyToManyField(HeaderValue, through='Header')

    def __str__(self):
        return "%s" %self.field

    def __unicode__(self):
        return "%s" %self.field
 
    def get_label(self):
        return "header-field"

    class Meta:
        app_label = 'main'


class Header(models.Model):
    '''A header is a field and value associated with one or more images.
    '''
    field = models.ForeignKey(HeaderField)
    value = models.ForeignKey(HeaderValue)
    add_date = models.DateTimeField('date added', auto_now_add=True)

    def __str__(self):
        return "%s:%s" %(self.field,self.value)

    def __unicode__(self):
        return "%s:%s" %(self.field,self.value)
 
    def get_label(self):
        return "header"

    class Meta:
        app_label = 'main'
        unique_together = ('field','value',)




#################################################################################################
# Batch #########################################################################################
#################################################################################################


class Batch(models.Model):
    '''A batch has one or more images for some number of patients, each of which
    is associated with a Study or Session. A batch maps cleanly to a folder that is
    dropped into data for processing, and the application moves through tasks based
    on batches.
    '''
    uid = models.CharField(max_length=200, null=False, unique=True)

    status = models.CharField(choices=BATCH_STATUS,
                              default="NEW",
                              max_length=250)

    add_date = models.DateTimeField('date added', auto_now_add=True)
    has_error = models.BooleanField(choices=ERROR_STATUS, 
                                    default=False,
                                    verbose_name="HasError")

    errors = JSONField(default=dict())
    modify_date = models.DateTimeField('date modified', auto_now=True)
    tags = TaggableManager()

    def change_images_status(self,status):
        '''change all images to have the same status'''
        for dcm in self.image_set.all():
            dcm.status = status
            dcm.save()
    

    def get_image_paths(self):
        '''return file paths for all images associated
        with a batch'''
        image_files = []
        for dcm in self.image_set.all():
            image_files.append(dcm.image.path)
        return image_files


    def get_absolute_url(self):
        return reverse('batch_details', args=[str(self.id)])


    def __str__(self):
        return "%s-%s" %(self.id,self.uid)

    def __unicode__(self):
        return "%s-%s" %(self.id,self.uid)

    def get_label(self):
        return "batch"

    class Meta:
        app_label = 'main'


class Image(models.Model):
    '''An image maps to one dicom file, usually in a series
    '''
    uid = models.CharField(max_length=250, null=False, blank=False)

    status = models.CharField(choices=IMAGE_STATUS,
                              default="NEW",
                              max_length=250)

    image = models.FileField(upload_to=get_upload_folder,null=True,blank=False)
    add_date = models.DateTimeField('date added', auto_now_add=True)
    modify_date = models.DateTimeField('date modified', auto_now=True)
    batch = models.ForeignKey(Batch,null=False,blank=False)
    headers = models.ManyToManyField(Header)

    def __str__(self):
        return "%s-%s" %(self.id,self.uid)

    def __unicode__(self):
        return "%s-%s" %(self.id,self.uid)

    def load_dicom(self):
        '''easily load an Image if dicom file'''
        from pydicom import read_file
        return(read_file(self.image.path,
                         force=True))

    def rename(self,new_basename):
        ''' rename will name the image path of an already uploaded
        file to some new_basename.'''
        initial_path = self.image.path
        self.image.name = new_basename
        new_path = settings.MEDIA_ROOT + self.image.name
        os.rename(initial_path, new_path)
        self.save()
        return self


    def get_label(self):
        return "image"

    class Meta:
        app_label = 'main'
        unique_together = ('uid','batch',)
 
    # Get the url for a report collection
    def get_absolute_url(self):
        return reverse('image_details', args=[str(self.id)])

