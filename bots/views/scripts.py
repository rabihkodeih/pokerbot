'''
Created on May 6, 2013

@author: Shadi Moodad
'''
from bots import settings
from bots.models import PlayerHand
from django.conf.urls import patterns, url
from django.shortcuts import render_to_response
import datetime
import logging
import os

log = logging.getLogger(__name__)

urls = patterns('',
        url(r'^sync_hands$', "bots.views.scripts.syncHands"),
    )

def syncHands(request):
    ctx = {}
    lstFiles = []
    
    try:
        logPath = settings.HAND_LOG_PATH
        lstFiles = os.listdir(logPath)
        
        nbHandsRead = 0
        
        for fPath in lstFiles:
            if fPath.find('hand-') != 0:
                continue
            
            nbHandsRead += 1
            f = None
            
            try:
                f = open(logPath +"/" + fPath)
                log.debug('Reading hands for game: %s', f.name)
                
                for line in f.readlines():
                    data = line.split(",")
                    gameId = data[0]
                    playerId = data[1]
                    holeCards = data[2].replace("{", "").replace("}", "").replace("10", "T").split(" ")
                    hole1 = holeCards[0][0].upper()+holeCards[0][1].lower()
                    hole2 = holeCards[1][0].upper()+holeCards[1][1].lower()
    #                 log.debug('--->hole cards: %s', (holeCards,))
                    nick = data[3]
                    PlayerHand.objects.create(f_game_id = gameId, f_player_id = playerId, f_hole1 = hole1, f_hole2=hole2, f_nick=nick)
                
    #             f.close()
    #             log.debug('removed file: %s', f.name)
            except:
                log.error("Error reading player hands", exc_info=1)
                
            if f:
                f.close()
                os.remove(f.name)
                
        #Clean up old hands 
        PlayerHand.objects.filter(f_ts__lte = datetime.datetime.now() - datetime.timedelta(minutes=30)).delete()
        
        ctx['content'] = "Collected %s hands" % (nbHandsRead)
    except:
        log.error("Error reading hands", exc_info=1)
        ctx['content'] = "Error reading hands, please check the logs"
    
    return render_to_response("templates/scripts/sync_hands.html", ctx);