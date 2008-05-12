import es
import os
import copy
import langlib

import psyco
psyco.full()

###########################
#Module methods start here#
########################################################
# All methods that should be able to be called through #
# the API need to have "module" as first parameter     #
########################################################
class LanguageDict(dict):
    languages = langlib.getLanguages()
    abbreviations = map(langlib.getLangAbbreviation, languages)
    defaultlang = langlib.getDefaultLang()
    def __init__(self, key, value):
        self.name = key
        if isinstance(value, dict):
            self.text = self.mapdict(str, value)
        else:
            self.text = {self.defaultlang:str(value)}
    def __str__(self):
        return ("LanguageDict(%s)" % self.name)
    def __repr__(self):
        return self.__str__
    def __len__(self):
        return len(self.abbreviations)
    def __getitem__(self, key):
        if key in self.abbreviations:
            if key in self.text:
                return self.text[key]
            elif self.defaultlang in self.text:
                return self.text[self.defaultlang]
            elif "en" in self.text:
                return self.text["en"]
            else:
                raise IndexError("LanguageDict(%s): No language string available" % self.name)
        else:
            raise IndexError("LanguageDict(%s): No valid abbreviation" % self.name)
    def __setitem__(self, key, value):
        if key in self.abbreviations:
            self.text[key] = str(value)
        else:
            raise IndexError("LanguageDict(%s): No valid abbreviation" % self.name)
    def __delitem__(self, key):
        if key in self.abbreviations:
            if key != self.defaultlang and key != "en":
                del self.text[key]
            else:
                raise ValueError("LanguageDict(%s): You can't delete the default keys" % self.name)
        else:
            raise IndexError("LanguageDict(%s): No valid abbreviation" % self.name)
    def __iter__(self):
        return self.abbreviations.__iter__()
    def __contains__(self, key):
        if key in self.abbreviations:
            return True
        else:
            return False
    def clear(self):
        pass
    def copy(self):
        return copy.copy(self)
    def has_key(self, key):
        return self.__contains__(key)
    def items(self):
        return self.text.items()
    def keys(self):
        return self.abbreviations
    def update(self, iterable):
        return self.text.update(iterable)
    def fromkeys(self, seq, value = None):
        return self.text.fromkeys(seq, value)
    def values(self):
        return self.text.values()
    def mapdict(self, function, iterable):
        if callable(function) and iterable:
            for key in iterable:
                iterable[key] = function(iterable[key])
            return iterable
        else:
            raise TypeError

def createLanguageString(module = None, text = None):
    if not text:
        text = module
    if text:
        return LanguageDict(text.lower(), text)
    else:
        return False

def getLanguage(module = None, file = None):
    if module:
        if file:
            filename = "%s/modules/%s/%s.ini" % (es.getAddonPath('xa'), module, file)
        else:
            filename = "%s/modules/%s/strings.ini" % (es.getAddonPath('xa'), module)
    else:
        if file:
            filename = "%s/languages/%s.ini" % (es.getAddonPath('xa'), file)
        else:
            filename = "%s/languages/strings.ini" % (es.getAddonPath('xa'))
    if os.path.exists(filename):
        langobj = langlib.Strings(filename)
        for key in langobj:
            langobj[key] = LanguageDict(key, langobj[key])
        return langobj
    else:
        raise IOError, "Could not find %s!" % filename
