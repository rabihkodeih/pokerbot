'''
Created on Sep 22, 2012

@author: Shadi Moodad
'''

from bots.common import Tools
from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, redirect
import logging
from bots.models import Bot, BotTable, Config, BotMonitor, BotTournament
import json
from django.http import HttpResponse

log = logging.getLogger(__name__)

urls = patterns('',
        url(r'^bot_cards$', "bots.views.monitoring.botCards"),
        url(r'^monitored_tables$', "bots.views.monitoring.monitoredTables"),
        url(r'^monitor_table$', "bots.views.monitoring.monitorTable"),
        url(r'^stop_table$', "bots.views.monitoring.stopTable"),
    )


@login_required
def botCards(request):
    ctx = {}
    
    tmpTables = BotTable.objects.values('f_table_name').distinct()
    lstTables = [x['f_table_name'] for x in tmpTables]
    
    
    tmpTables = BotTournament.objects.values("f_table_name").distinct()
    if len(tmpTables):
        lstTables.append("------Tournaments-------")
        lstTables = lstTables + [x['f_table_name'] for x in tmpTables]
    
    ctx['tables'] = lstTables
    
    Tools.defaultContextData(request, ctx)
    return render_to_response('templates/monitoring/bot_cards.html', ctx);

def monitoredTables(request):
    """
     Get the list of all monitored data, group them by table and add them to a map.
     Each map entry contains the name of table as key and an array of size 9 where the index in the array is the position on the table
     Each slot in the array contains the 
    """
    
    ctx = {}

    #Get list of monitored tables from the config in order not to include the ones that aren't configured. Since the bots takes some time to stop    
    lstMonitoredTables = []
    lstConf = Config.objects.filter(f_name='MONITOR_TABLE').order_by('f_value')
    for c in lstConf:
        lstMonitoredTables.append(c.f_value)
    
    mTables = {}
    mTablesGames = {} #hold reference to the last game ID on this table. used to filter the games that aren't related to this table.
    
    lstMtbl = BotMonitor.objects.all().order_by('f_table', '-f_game_id')
    
    lstToClean= []
    
    for mTbl in lstMtbl:
        if mTbl.f_table in lstMonitoredTables:
            if mTbl.f_table not in mTables:
                mTables[mTbl.f_table] = [None] * 9
                mTablesGames[mTbl.f_table] = mTbl.f_game_id
                
            if mTablesGames[mTbl.f_table] == mTbl.f_game_id:
                tables = mTables[mTbl.f_table]
                tables[mTbl.f_seat] = mTbl
        else:
            lstToClean.append(mTbl)
            
    #clean the left overs. this happen because bots takes time to stop logging their hands
    for mTbl in lstToClean:
        mTbl.delete()
            
    #concat the name with the gameId
    for k in mTables.keys():
        mTables[k+"-"+str(mTablesGames[k])] = mTables[k]
        del mTables[k]
        
    ctx['monitoredTables'] = mTables
    
    Tools.defaultContextData(request, ctx)
    return render_to_response('templates/monitoring/bot_tables.html', ctx);
    
def monitorTable(request):
    ctx = {}
    
    tblName = request.GET['tblToMonitor']
    if tblName != "------Tournaments-------":
        lstConfig = Config.objects.filter(f_name='MONITOR_TABLE', f_value = tblName)
        if len(lstConfig) == 0:
            Config.objects.create(f_name='MONITOR_TABLE', f_value = tblName, f_clear_name = 'Monitoring bots cards for table')
    
    Tools.defaultContextData(request, ctx)
    return redirect('/bots/monitoring/monitored_tables');
    
    
def stopTable(request):
    ctx = {}
    
    tblName = request.GET['tbl']
    
    if tblName.rfind("-") > 0:
        tblName = tblName[0:tblName.rfind("-")]
    
    #stop the configuration
    Config.objects.filter(f_name='MONITOR_TABLE', f_value = tblName).delete()
    
    #delete all old records
    BotMonitor.objects.all().filter(f_table=tblName).delete()
    
    
    Tools.defaultContextData(request, ctx)
    return redirect('/bots/monitoring/monitored_tables');


