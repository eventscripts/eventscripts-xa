﻿import es
from playerlib import getPlayerList
from xa import xa

info = es.AddonInfo()
info.name = "XA:Objectives for CS:S"
info.version = "0.1"
info.author = "Wonder"
info.description = "Slays the team which fails to complete their objectives."

def load():
	global xaobjectives, slay, text

	xaobjectives = xa.register("xaobjectives")
	slay = xa.setting.createVariable(xaobjectives, "css_objectives", "1", "XA: If 1, losing team will be slain.")
	text = xa.language.getLanguage("xaobjectives")

	if es.getgame() != "Counter-Strike: Source":
		return False

def unload():
	xa.unregister("xaobjectives")

def round_end(eventVar):
	if int(slay):
		if eventVar["winner"] == "2" and es.getlivingplayercount(3):
			cts, ts = getPlayerList("#ct"), getPlayerList("#t")
			for i in cts:
				i.kill()
				es.tell(int(i), "#multi", text("lost"))
			for i in ts:
				es.tell(int(i), "#multi", text("won"))
		elif eventVar["winner"] == "3" and es.getlivingplayercount(2):
			ts, cts = getPlayerList("#t"), getPlayerList("#ct")
			for i in ts:
				i.kill()
				es.tell(int(i), "#multi", text("lost"))
			for i in cts:
				es.tell(int(i), "#multi", text("won"))

def round_start(eventVar):
	if int(slay):
		es.msg("#multi", text("round_start"))
