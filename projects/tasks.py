from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_task_assigned_email(assignee_email, assignee_name, task_title, project_name):
    send_mail(
        subject=f'You have been assigned a task: {task_title}',
        message=f'''
Hi {assignee_name},

You have been assigned a new task in {project_name}:

Task: {task_title}

Please login to Task Manager to view the details.

Thanks,
Task Manager Team
        ''',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[assignee_email],
        fail_silently=False,
    )