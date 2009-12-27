from django.db import models
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string

from pygments import highlight
from xa.mypygments import EventScriptsLexer
from pygments.formatters import HtmlFormatter

class BaseManager(models.Manager):
    def get_or_404(self, *args, **kwargs):
        return get_object_or_404(self, *args, **kwargs)
    

class PowerManager(BaseManager):
    def get_or_create(self, name, user):
        flgs = self.filter(name=name)
        if flgs:
            flg = flgs[0]
        else:
            flg = self.create(name=name, custom=True)
        if flg.custom:
            flg.users.add(user)
        return flg


class Power(models.Model):
    id          = models.AutoField(primary_key=True)
    name        = models.CharField(max_length=255)
    default     = models.PositiveSmallIntegerField(default=1)
    custom      = models.BooleanField(default=False)
    users       = models.ManyToManyField('auth.User', related_name='custom_powers', blank=True)

    objects = PowerManager()

    class Meta:
        verbose_name = 'Power Flag'
        verbose_name_plural = 'Power Flags'
    
    def __unicode__(self):
        return self.name
    
    
class Config(models.Model):
    id          = models.AutoField(primary_key=True)
    name        = models.CharField(max_length=255)
    owner       = models.ForeignKey('auth.User', related_name='configs')
    
    objects     = BaseManager()
    
    class Meta:
        unique_together = [('name','owner')]
    
    def __unicode__(self):
        return '%s (%s)' % (self.name, self.owner)
    
    def players(self):
        return Player.objects.filter(groups__config=self).distinct()
    
    def render(self):
        return render_to_string('groupauth/config.txt', {'config': self})
        
    def render_plain(self):
        return self.render()
    
    def render_nice(self):
        return highlight(self.render(), EventScriptsLexer(), HtmlFormatter())
    
    
class PlayerRelation(models.Model):
    player      = models.ForeignKey('groupauth.Player')
    user        = models.ForeignKey('auth.User')
    name        = models.CharField(max_length=255)
    
    
class Player(models.Model):
    id          = models.AutoField(primary_key=True)
    steamid     = models.CharField(max_length=25, unique=True)
    known_by    = models.ManyToManyField('auth.User', related_name='known_players',
                                         through=PlayerRelation)
    
    def __unicode__(self):
        return self.steamid
    
    
class Group(models.Model):
    id          = models.AutoField(primary_key=True)
    name        = models.CharField(max_length=255)
    default     = models.PositiveSmallIntegerField(default=1)
    config      = models.ForeignKey(Config, related_name='groups')
    players     = models.ManyToManyField(Player, related_name='groups')
    powers      = models.ManyToManyField(Power, related_name='groups')
    
    def __unicode__(self):
        return '%s (%s)' % (self.name, self.config)
