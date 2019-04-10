# coding: utf-8
from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Phase


@receiver(pre_save, sender=Phase)
def phase_author(sender, **kwargs):
    u"""
    auto-save author
    """
    p = kwargs['instance']

    #p.author = kwargs
    
