'''
Created on Nov 6, 2012

@author: Shadi Moodad
'''

from bots.common import Tools
from bots.models import BotSchedule, BotTable
from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render_to_response
import datetime
import json
import logging
import random
import traceback

log = logging.getLogger(__name__)

urls = patterns('',
        url(r'^scheduler_board$', "bots.views.scheduler.schedulerBoard"),
        url(r'^schedule_grid_data$', "bots.views.scheduler.scheduleGridData"),
        url(r'^save_schedule$', "bots.views.scheduler.saveSchedule"),
        url(r'^enable_schedule$', "bots.views.scheduler.enableSchedule"),
        url(r'^run$', "bots.views.scheduler.runScheduler"),
    )

@login_required
def schedulerBoard(request):
    ctx = {}
    
    Tools.defaultContextData(request, ctx)
    return render_to_response('templates/scheduler/schedule_grid.html', ctx);

@login_required
def scheduleGridData(request):
    ctx = Tools.defaultContextData(request, {'POST':request.POST});
    
    #TODO implement the filter 

    rs = BotSchedule.objects.filter()
    Tools.populateContextForGrid(ctx, rs, request.GET['rows'], request.GET['page'], request.GET['sidx'], request.GET['sord'])    

    return render_to_response("templates/scheduler/schedule_grid_data.xml", ctx);

@login_required
def saveSchedule(request):
    rs = {}
    POST = request.POST
    rId = POST['id']
    
    if(rId != ''):    
        BotSchedule.objects.filter(id=rId).update(f_name = POST['name'], f_from_time = POST['from_time'], f_to_time = POST['to_time']
                                            , f_enabled = POST['enabledStatus'], f_num_bots = Tools.toInt(POST['num_bots']), f_tables = POST['tables']
                                            , f_nicks = POST['bots'])
    else:
        BotSchedule.objects.create(f_name = POST['name'], f_from_time = POST['from_time'], f_to_time = POST['to_time']
                                            , f_enabled = POST['enabledStatus'], f_num_bots = Tools.toInt(POST['num_bots']), f_tables = POST['tables']
                                            , f_nicks = POST['bots'])
                
    rs['success'] = True
    return HttpResponse(json.dumps(rs), mimetype="application/json")

@login_required
def enableSchedule(request):
    rs = {}
    rIds = request.POST['id'].split(",")
    enable = 1 if (request.POST['mode'] == 'enable') else 0
    rs['success'] = True
    
    if(request.POST['mode'] == "delete"):
        BotSchedule.objects.filter(id=rIds[0]).delete()
    else:
        for rId in rIds:
            if rId.strip() != '':
                BotSchedule.objects.filter(id=rId).update(f_enabled=enable)
    
    return HttpResponse(json.dumps(rs), mimetype="application/json")

def runScheduler(request):
    """
     Gets all configured/enabled scheduling intervals that falls within the current time.
     1- For each table configured in each interval, check if the number of bots who can play is below the configured number and if yes
         pick up a bot that is not enabled from the list of allowed bots to play and enable it
     
     2- if number of configured bots is bigger then disable a bot that is playing
     
     3- Checks if there is a bot enabled that is not in the current interval and turn it off
     
     4- disable the bots that finished within 30 min 
    """
    
    lstMsgs = []
    
    def printMsg(msg):
        print msg
        lstMsgs.append(msg)
        
    print("Scheduler started at :%s" % (datetime.datetime.now()))
    lstSchedules = BotSchedule.objects.filter(f_enabled=1)
    now = datetime.datetime.now().time()
    
    expTime = datetime.datetime.now() - datetime.timedelta(minutes = 30)
    processedTable = {}
    lstTablesToStop = set()  #list of tables that are in an enabled schedule but not in any interval
    lstTablesInSchedule = set() #list of tables that are in an enabled schedule and within interval
    
    for schedule in lstSchedules:
        printMsg("Checking schedule: %s from: %s to: %s" % (schedule.f_name, schedule.f_from_time, schedule.f_to_time) ) 
        
        try:
            tFrom = datetime.time(int(schedule.f_from_time.split(":")[0]), int(schedule.f_from_time.split(":")[1]))
            tTo = datetime.time(int(schedule.f_to_time.split(":")[0]), int(schedule.f_to_time.split(":")[1]))
            tMidnight = tTo
            if tFrom > tTo:
                tMidnight = datetime.time(23, 59, 59)
                
            if (now >= tFrom and now <= tMidnight) or (now >= tMidnight and now <= tTo) :
                printMsg("\tProcessing matching schedule: %s from: %s  to: %s" %(schedule.f_name, tFrom, tTo) )
                lstTables = schedule.f_tables.split(",")
                for table in lstTables:
                    table = table.strip().lower()
                    
                    if table in processedTable:
                        printMsg("\t\tWARNING! table %s is configured in more than one schedule. Already Processed with %s, skipped schedule: %s " % (table, processedTable[table], schedule.f_name))
                        continue
                    
                    lstTablesInSchedule.add(table)
                    
                    #disable BotTable where the entry is enabled and bot is disabled in order not to interfere with the results
                    BotTable.objects.filter(bot__f_enabled = 0, f_enabled = 1).update(f_enabled=0)
                    
                    lstActive = BotTable.objects.filter(f_table_name=table, f_enabled = 1, f_last_exit_time__lt = expTime)
                    
                    lstCanPlay = BotTable.objects.filter(f_table_name=table, f_enabled = 0, f_last_exit_time__lt = expTime)
                    
                    printMsg("\tNum of bots who are active on table: %s is %s vs. %s configured" % (table, len(lstActive), schedule.f_num_bots))
                    
                    scheduledBots = [b.strip().lower() for b in schedule.f_nicks.split(",")]
                    lstCanPlayNicks = [t.bot.f_nick.strip().lower() for t in lstCanPlay]
                    lstBots = [b for b in scheduledBots if b.strip() in lstCanPlayNicks]
                        
                    #Enable a bot
                    if len(lstActive) < schedule.f_num_bots:
                        printMsg("\t\tNumber of bots who can plan on table: %s is less then configured: %s" % (table, schedule.f_num_bots))
                        
                        if len(lstBots):
                            #Retry few times in order to account for errors when someone enters a bot that is not assigned to the given table
                            nbRetries = 5
                            choosenBot = None
                            while choosenBot is None and nbRetries != 0 :
                                choosenBot = lstBots[random.randint(0, len(lstBots) - 1)]
                                tmp =  BotTable.objects.filter(f_table_name=table, bot__f_nick = choosenBot)
                                nbRetries -= 1
                                if len(tmp):
                                    choosenBot = tmp[0]
                                    choosenBot.f_enabled = 1
                                    choosenBot.bot.f_enabled = 1
                                    choosenBot.bot.save()
                                    choosenBot.save()
                                    printMsg("\t\tEnabled bot: %s to play on table: %s" % (choosenBot.bot.f_nick, table))
                                else:
                                    printMsg("\t\tWARNING! bot: %s is scheduled to play on %s but not configured in the bot tab" % (choosenBot, table) )
                                    choosenBot = None             
                        else:
                            printMsg("\t\tWARNING! not enough configured bots to play on table: %s" % (table))
                    elif len(lstActive) > schedule.f_num_bots:
                        printMsg("\t\tNumber of bots who can plan on table: %s is more then configured: %s. Going to stop one" % (table, schedule.f_num_bots))
                        botToStop = lstActive[random.randint(0, len(lstActive)-1 )]
                        botToStop.f_enabled = 0
                        botToStop.save()
                        printMsg("\t\tStopped bot: %s " % (botToStop.bot.f_nick))
                            
                    #Disable the bots that stopped playing within the last 30 min
                    BotTable.objects.filter(f_table_name=table, f_enabled = 1, f_last_exit_time__gt = expTime).update(f_enabled=0)
                    
                    #Disable the fishes that aren't in this rule
                    lstNotInThisRule = [b for b in lstActive if b.bot.f_nick.strip().lower() not in scheduledBots]
                    if len(lstNotInThisRule):
                        bot = lstNotInThisRule[random.randint(0, len(lstNotInThisRule)-1)]
                        bot.f_enabled= 0
                        bot.save()
                        printMsg("\t\tDisabled bot: %s from table: %s because not in current schedule: %s" % (bot.bot.f_nick, table, schedule.f_name))
                    
                    processedTable[table] = "%s--> %s-%s" % (schedule.f_name, schedule.f_from_time, schedule.f_to_time)
            else:
                lstTablesToStop.update([t.strip() for t in schedule.f_tables.split(",") if t.strip() != ''] )
                print "tbls: %s" % (schedule.f_tables,)
                    
        except:
            printMsg("ERROR in rule: %s, wrong time [from:%s, to:%s]" % (schedule.f_name, schedule.f_from_time, schedule.f_to_time))
            traceback.print_exc()
            
    lstTablesToStop = lstTablesToStop - lstTablesInSchedule
    
    printMsg("\nOut of schedule tables: %s" % (lstTablesToStop))
    for table in lstTablesToStop:
        lstActive = BotTable.objects.filter(f_table_name=table, f_enabled = 1, bot__f_enabled = 1)
        if len(lstActive):
            tbl = lstActive[random.randint(0, len(lstActive)-1 )]
            tbl.f_enabled = 0
            tbl.save()
            
            printMsg("\tStopping bot: %s from table: %s" % (tbl.bot.f_nick, tbl.f_table_name))
                    
            
    printMsg("\nSuccessfuly completed")
    
    ctx = Tools.defaultContextData(request, {'content': "\n".join(lstMsgs)})
        
    return render_to_response("templates/scheduler/run.html", ctx);