from django.db import models
from django.template.loader import render_to_string

from pygments import highlight
from xa.mypygments import EventScriptsLexer
from xa.utils import BaseManager
from pygments.formatters.html import HtmlFormatter


class PowerManager(BaseManager):
    """
    Custom manager for Powers (subclassing custom BaseManager), to allow a
    custom get_or_create
    """
    def get_or_create(self, name, user):
        """
        Get or create a flag for a user
        """
        flgs = self.filter(name=name)
        if flgs:
            flg = flgs[0]
        else:
            flg = self.create(name=name, custom=True)
        if flg.custom:
            flg.users.add(user)
        return flg


class Power(models.Model):
    """
    A Power flag
    """
    id          = models.AutoField(primary_key=True)
    name        = models.CharField(max_length=255)
    default     = models.PositiveSmallIntegerField(default=1)
    custom      = models.BooleanField(default=False)
    users       = models.ManyToManyField('auth.User',
                                         related_name='custom_powers',
                                         blank=True)

    objects = PowerManager()

    class Meta:
        verbose_name = 'Power Flag'
        verbose_name_plural = 'Power Flags'
    
    def __unicode__(self):
        return self.name
    
    
class Config(models.Model):
    """
    A GroupAuth config file
    """
    id          = models.AutoField(primary_key=True)
    name        = models.CharField(max_length=255)
    owner       = models.ForeignKey('auth.User', related_name='configs')
    
    objects     = BaseManager()
    
    class Meta:
        unique_together = [('name','owner')]
    
    def __unicode__(self):
        return '%s (%s)' % (self.name, self.owner)
    
    def players(self):
        """
        Return a list of players in this config
        """
        return Player.objects.filter(groups__config=self).distinct()
    
    def render(self):
        """
        Render this config plain
        """
        return render_to_string('groupauth/config.txt', {'config': self})
        
    def render_plain(self):
        """
        Same as self.render
        """
        return self.render()
    
    def render_nice(self):
        """
        Render this config nice.
        """
        return highlight(self.render(), EventScriptsLexer(), HtmlFormatter())
    
    
class PlayerRelation(models.Model):
    """
    Through-Model for the Player<->User relation
    """
    player      = models.ForeignKey('groupauth.Player')
    user        = models.ForeignKey('auth.User')
    name        = models.CharField(max_length=255)
    
    objects = BaseManager()
    
    
class Player(models.Model):
    """
    A player (with steamid).
    Names are saved in the Through-Model PlayerRelation
    """
    id          = models.AutoField(primary_key=True)
    steamid     = models.CharField(max_length=25, unique=True)
    known_by    = models.ManyToManyField('auth.User',
                                         related_name='known_players',
                                         through=PlayerRelation)
    
    objects = BaseManager()
    
    def __unicode__(self):
        return self.steamid
    
    
class Group(models.Model):
    """
    A group in a config
    """
    id          = models.AutoField(primary_key=True)
    name        = models.CharField(max_length=255)
    default     = models.PositiveSmallIntegerField(default=1)
    config      = models.ForeignKey(Config, related_name='groups')
    players     = models.ManyToManyField(Player, related_name='groups')
    powers      = models.ManyToManyField(Power, related_name='groups')
    
    objects = BaseManager()
    
    def __unicode__(self):
        return '%s (%s)' % (self.name, self.config)
