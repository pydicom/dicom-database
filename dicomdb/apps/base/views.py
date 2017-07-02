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

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views import View
from dicomdb.apps.base.tasks import batch_memory_upload 
from dicomdb.apps.main.models import Batch
from dicomdb.apps.main.utils import get_batch
from django.contrib import messages
import pickle

from haikunator import Haikunator
generator = Haikunator()

# Error Pages #########################################

def handler404(request):
    return render(request,'base/404.html')

def handler500(request):
    return render(request,'base/500.html')


# Upload Dataset as Batch #############################


class UploadDatasets(View):
    '''UploadDatasets will take an uploaded file, and parse it as a dataset for correctness and import to 
    docfish. A dataset that is too large for this interface should be upload in a different method (TBD)
    '''
    def get(self, request, bid=None):

        if bid is None:
            bid = generator.haikunate()  
            batch = Batch.objects.create(uid=bid)
            batch.save()
        else:
            batch = get_batch(bid)

        context = {"batch":batch}

        return render(self.request, 'upload/datasets_upload.html', context)


    def post(self, request, bid):

        batch = get_batch(bid)

        # A post without files, not sure how/why this would be done, but should be caught
        if request.FILES == None:
            data = {'is_valid': False, 'name': "No files provided", 'url': "/"}
            return JsonResponse(data)
            
        # Generate a new batch
        data = batch_memory_upload(memory_file=request.FILES['file'],
                                   batch=batch)

        if data['is_valid'] == True:
            messages.info(request,"Your datasets are uploading. Please refresh the page if you do not see them.")

        return JsonResponse(data)

def clear_database(request):
    return redirect(request.POST.get('next'))
