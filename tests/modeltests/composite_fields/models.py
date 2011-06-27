from django.db import models

class Person(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birthday = models.DateField()

    full_name = models.CompositeField(first_name, last_name, primary_key=True)

    def __unicode__(self):
        return u'%s %s' % (self.first_name, self.last_name)
