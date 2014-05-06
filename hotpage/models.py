# -*- coding: utf-8 -*- 


from django.db import models
from django.contrib.auth.models import User



# Create your models here.

class UserProfile(models.Model):

    user = models.ForeignKey(User) 
    pets = models.BooleanField(default=False)
    create_time = models.DateTimeField(verbose_name=u"创建时间", auto_now_add=True, null=True)
    last_modified_time = models.DateTimeField(verbose_name=u"最后修改时间", auto_now=True, null = True)

    
