from django.db import models


class Card(models.Model):
    name = models.CharField(max_length=145)

    def __str__(self):
        return self.name

    class Meta:
        app_label = "Scryfall2eBay"


# class UserCardSave(models.Model):
#     id = models.CharField()

