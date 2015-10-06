'''
Created on Aug 31, 2012

@author: Shadi Moodad
'''
from bots.common import Tools
from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
# from django.shortcuts import render_to_response
import logging
from bots.models import Bot, BotTable, BotTournament
import json
from django.http import HttpResponse
import datetime
from django.shortcuts import render_to_response 


render_to_response

log = logging.getLogger(__name__)

urls = patterns('',
        url(r'^bots$', "bots.views.home.bots"),
        url(r'^bots_grid$', "bots.views.home.botsGrid"),
        url(r'^bots_grid_data$', "bots.views.home.botsGridData"),
        url(r'^enable_bot$', "bots.views.home.enableBot"),
        url(r'^delete_bot$', "bots.views.home.deleteBots"),
        url(r'^save_bot$', "bots.views.home.saveBot"),
        url(r'^bot_tables$', "bots.views.home.botTables"),
        url(r'^bot_table_grid_data$', "bots.views.home.botTableGridData"),
        url(r'^bot_tournament_grid_data$', "bots.views.home.botTournamentGridData"),
        url(r'^enable_bottable$', "bots.views.home.enableBotTable"),
        url(r'^enable_bottournament$', "bots.views.home.enableBotTournament"),
        url(r'^save_bottable$', "bots.views.home.saveBotTable"),
        url(r'^save_bottournament$', "bots.views.home.saveBotTournament"),
    )

@login_required
def home(request):
    ctx = {}
    
    Tools.defaultContextData(request, ctx)
    return render_to_response('templates/home/home.html', ctx);

@login_required
def bots(request):
    ctx = Tools.defaultContextData(request, {});

    return render_to_response("templates/home/bots_tab.html", ctx);

@login_required
def botsGrid(request):
    ctx = Tools.defaultContextData(request, {'POST':request.POST});
    
    return render_to_response("templates/home/bots_grid.html", ctx);
    
    
@login_required
def botsGridData(request):
    ctx = Tools.defaultContextData(request, {'POST':request.POST});
    
    #TODO implement the filter 

    rs = Bot.objects.filter()
    Tools.populateContextForGrid(ctx, rs, request.GET['rows'], request.GET['page'], request.GET['sidx'], request.GET['sord'])    

    return render_to_response("templates/home/bots_grid_data.xml", ctx);

@login_required
def enableBot(request):
    rs = {}
    botIds = request.POST['id'].split(",")
    enable = 1 if (request.POST['mode'] == 'enable') else 0
    rs['success'] = True
    
    for botId in botIds:
        Bot.objects.filter(id=botId).update(f_enabled=enable)
    
    return HttpResponse(json.dumps(rs), mimetype="application/json")


@login_required
def deleteBots(request):
    rs = {}
    botIds = request.POST['id'].split(",")
    rs['success'] = True
    
    for botId in botIds:
        Bot.objects.filter(id=botId).delete()
    
    return HttpResponse(json.dumps(rs), mimetype="application/json")

@login_required
def saveBot(request):
    rs = {}
    POST = request.POST
    botId = POST['id']
    
    if(botId != ''):    
        Bot.objects.filter(id=botId).update(f_nick = POST['nick'].strip(), f_password = POST['password'], f_money_type = POST['moneyType']
                                            , f_enabled = POST['enabledStatus'], f_strategy = POST['strategy'], f_min_bb = Tools.toInt(POST['minBB'])
                                            , f_max_bb = Tools.toInt(POST['maxBB']), f_bb_exit = Tools.toInt(POST['bbExit']))
    else:
        nicks = POST['nick'].split(",")
        tableNames = POST['tables'].strip().split(",")
        
        for nick in nicks:
            nick = nick.strip()
            bot = Bot.objects.create(f_nick = nick, f_password = POST['password'], f_money_type = POST['moneyType']
                               , f_enabled = POST['enabledStatus'], f_strategy = POST['strategy'], f_min_bb = Tools.toInt(POST['minBB'])
                               , f_max_bb = Tools.toInt(POST['maxBB']), f_bb_exit = Tools.toInt(POST['bbExit']))
            for table in tableNames:
                tableName = table.strip()
                if(tableName != ''):
                    BotTable.objects.create(bot_id=bot.id, f_table_name = tableName.strip(), f_enabled = 1, f_strategy = '', f_min_bb = 0, f_max_bb = 0, f_bb_exit = 0)
                
    rs['success'] = True
    return HttpResponse(json.dumps(rs), mimetype="application/json")


@login_required
def botTables(request):
    ctx = Tools.defaultContextData(request, {'POST':request.POST});
    
    return render_to_response("templates/home/bot_tables.html", ctx);
    
@login_required
def botTableGridData(request):
    POST = request.POST
    ctx = Tools.defaultContextData(request, {'POST':POST});
    
    #TODO implement the filter 

    rs = BotTable.objects.filter(bot_id=request.GET['id'])
    Tools.populateContextForGrid(ctx, rs, request.GET['rows'], request.GET['page'], request.GET['sidx'], request.GET['sord'])    

    return render_to_response("templates/home/bot_table_grid_data.xml", ctx)

@login_required
def botTournamentGridData(request):
    POST = request.POST
    ctx = Tools.defaultContextData(request, {'POST':POST});
    
    #TODO implement the filter 

    rs = BotTournament.objects.filter(bot_id=request.GET['id'])
    Tools.populateContextForGrid(ctx, rs, request.GET['rows'], request.GET['page'], request.GET['sidx'], request.GET['sord'])    

    return render_to_response("templates/home/bot_tournament_grid_data.xml", ctx)


@login_required
def enableBotTable(request):
    rs = {}
    botTblId = request.POST['id']
    enable = 1 if (request.POST['mode'] == 'enable') else 0
    rs['success'] = True
    
    if(request.POST['mode'] == "delete"):
        BotTable.objects.filter(id=botTblId).delete()
    else:
        BotTable.objects.filter(id=botTblId).update(f_enabled=enable)
    
    return HttpResponse(json.dumps(rs), mimetype="application/json")

@login_required
def enableBotTournament(request):
    rs = {}
    botTblId = request.POST['id']
    enable = 1 if (request.POST['mode'] == 'enable') else 0
    rs['success'] = True
    
    if(request.POST['mode'] == "delete"):
        BotTournament.objects.filter(id=botTblId).delete()
    else:
        BotTournament.objects.filter(id=botTblId).update(f_enabled=enable)
    
    return HttpResponse(json.dumps(rs), mimetype="application/json")

@login_required
def saveBotTable(request):
    rs = {}
    POST = request.POST
    botTableId = POST['id']
    
    if(botTableId != ''):    
        BotTable.objects.filter(id=botTableId).update(f_table_name = POST['tableName'], f_enabled = POST['enabledStatus'], f_strategy = POST['strategy'], f_min_bb = Tools.toInt(POST['minBB'])
                                            , f_max_bb = Tools.toInt(POST['maxBB']), f_bb_exit = Tools.toInt(POST['bbExit']))
    else:
        tableNames = POST['tableName'].split(",")
        nTime = datetime.datetime.now() - datetime.timedelta(minutes = 30)
        for tableName in tableNames:
            BotTable.objects.create(bot_id=POST['botId'], f_table_name = tableName.strip(), f_enabled = POST['enabledStatus'], f_strategy = POST['strategy'], f_min_bb = Tools.toInt(POST['minBB'])
                                                , f_max_bb = Tools.toInt(POST['maxBB']), f_bb_exit = Tools.toInt(POST['bbExit']), f_last_exit_time = nTime, f_last_enter_time = nTime)
    rs['success'] = True
    return HttpResponse(json.dumps(rs), mimetype="application/json")

@login_required
def saveBotTournament(request):
    rs = {}
    POST = request.POST
    botTableId = POST['id']
    
    if(botTableId != ''):    
        BotTournament.objects.filter(id=botTableId).update(f_table_name = POST['tableName'], f_enabled = POST['enabledStatus'], f_strategy = POST['strategy'], f_rebuy = POST['rebuy'], f_addon = POST['addOn'])
    else:
        tableNames = POST['tableName'].split(",")
        for tableName in tableNames:
            BotTournament.objects.create(bot_id=POST['botId'], f_table_name = tableName.strip(), f_enabled = POST['enabledStatus'], f_strategy = POST['strategy'], f_rebuy = POST['rebuy'], f_addon = POST['addOn'])
            
    rs['success'] = True
    return HttpResponse(json.dumps(rs), mimetype="application/json")

