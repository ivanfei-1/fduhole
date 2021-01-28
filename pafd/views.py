from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.db import IntegrityError

from .forms import StudentForm
from .models import Student
from .api import run

import logging
logger = logging.getLogger(__name__)

def index(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            logger.warning(form.cleaned_data)
            # start testing
            submit_result = run(form.cleaned_data['school_id'], form.cleaned_data['password'])
            logger.warning(submit_result)
            if submit_result['status'] == True: # valid information
                if not form.cleaned_data['email']:
                    form.cleaned_data['email'] = form.cleaned_data['school_id'] + "@fudan.edu.cn"
                student = Student(school_id=form.cleaned_data['school_id'],password=form.cleaned_data['password'],name=form.cleaned_data['name'],email=form.cleaned_data['email'])
                try:
                    student.save()
                except IntegrityError:
                    return HttpResponse('已登记过信息!')
                    #return HttpResponseRedirect('/pafd/invalid/')
                else:
                    message = submit_result['message']
                    return HttpResponse('提交不成功 ' + message + ' 请返回并重新填写!')
                    #return render(request, 'pafd/validated.html', {'message': message})
            else:
                return HttpResponse('提交不成功，请返回并重新填写!')
                #return HttpResponseRedirect('/pafd/invalid/')
        else:
            return HttpResponse('信息有误，请返回并重新填写!')
            #return HttpResponseRedirect('/pafd/invalid/')
    if request.method == 'GET':
        form = StudentForm(label_suffix='：')
        return render(request, 'pafd/index.html', {'form': form})

def invalid(request):
    return render(request, 'pafd/invalid.html', {'message': "提交不成功或已登记过信息，请确认无误后再次填写！"})

def validated(request):
    return render(request, 'pafd/validated.html')