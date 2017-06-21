from django.db import models
from account_mgr_app.models import Profile

# Create your models here.

class Alert(models.Model):
    name_max_length = 100
    name = models.CharField(max_length = name_max_length)
    subscriber = models.ManyToManyField(
        Profile,
        related_name="subscriptions"
    )
    owner = models.ManyToManyField(
        Profile,
        related_name=None
    )

    def __repr__(self):
        return "{}( name={}, subscriber={}, owner={})".format(
            self.__class__.__name__,
            self.name,
            self.subscriber,
            self.owner
        )

    def __str__(self):
        return(str(self.name))

class Pv(models.Model):
    name_max_length = 100
    name = models.CharField(max_length = name_max_length)

    def __repr__(self):
        return "{}(name={},)".format(self.__class__.__name__, self.name)

    def __str__(self):
        return(str(self.name))

class Trigger(models.Model):
    name_max_length = 100
    name = models.CharField(max_length = name_max_length)
    alert = models.ForeignKey(Alert, on_delete=models.CASCADE)
    pv = models.ForeignKey(
        Pv,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    def __repr__(self):
        return "{}(name={},alert={})".format(self.__class__.__name__, self.name, self.alert)

    def __str__(self):
        return(str(self.name))

