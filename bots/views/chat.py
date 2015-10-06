'''
Created on Nov 6, 2012

@author: Shadi Moodad
'''

from bots.common import Tools
from bots.models import Bot, BotTable, BotTableChat, BotTournament
from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render_to_response
import json
import logging

log = logging.getLogger(__name__)

urls = patterns('',
        url(r'^bots_chat$', "bots.views.chat.botsChat"),
        url(r'^send_chat$', "bots.views.chat.sendChat"),
    )

@login_required
def botsChat(request):
    ctx = {}
    
    tmpTables = BotTable.objects.values('f_table_name').distinct()
    lstTables = [x['f_table_name'] for x in tmpTables]
    
    
    tmpTables = BotTournament.objects.values("f_table_name").distinct()
    if len(tmpTables):
        lstTables.append("------Tournaments-------")
        lstTables = lstTables + [x['f_table_name'] for x in tmpTables]
    
    ctx['tables'] = lstTables
    
    ctx['bots'] = Bot.objects.values("f_nick").distinct();
    
    Tools.defaultContextData(request, ctx)
    return render_to_response('templates/chat/chat_board.html', ctx);

@login_required
def sendChat(request):
    ctx = {}
    bot = request.GET['bot']
    table = request.GET['table']
    msg = request.GET['msg']

    if(bot.strip() != "" and table.strip()!="" and msg.strip() != "" and table != "------Tournaments-------"):
        BotTableChat.objects.create(f_bot_nick=bot, f_table_name = table, f_message = msg)
        
    ctx['success'] = True
    ctx['chats'] = BotTableChat.objects.all() 
    
    Tools.defaultContextData(request, ctx)    
    return render_to_response('templates/chat/pending_msgs.html', ctx);