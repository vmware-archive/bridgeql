from django.db import models

# Create your models here.
class OperatingSystem(models.Model):
    name = models.CharField(max_length=32)
    arch = models.CharField(max_length=16)

    def __unicode__(self):
        return self.name

class Machine(models.Model):
    ip = models.CharField(max_length=15)
    name = models.CharField(max_length=32)
    cpu_count = models.SmallIntegerField()
    memory = models.IntegerField(help_text='Memory in gigabytes (GB)')
    created_at = models.DateTimeField()
    powered_on = models.BooleanField()
    os = models.ForeignKey(OperatingSystem)

    def __unicode__(self):
        return self.ip