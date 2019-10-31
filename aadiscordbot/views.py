import logging
import datetime

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required

from django.core.exceptions import PermissionDenied

from django.http import Http404, HttpResponse

from celery.task.control import inspect

@staff_member_required
def show_tasks(request):
    try:
        i = inspect()
        active = i.active()
        queue = i.reserved()

        context = {
            'active': active,
            'queue': queue
        }

        return render(request, 'celeryanalytics/tasks.html', context=context)
    except:
        messages.error(request, ('Error loading tasks!'))
        return redirect('index')