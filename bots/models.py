from django.db import models
import datetime


class Bot(models.Model):
    class Meta:
        db_table = u't_bot'
        managed = False
        
    id = models.AutoField(primary_key=True, db_column="f_id")
    f_player_id = models.IntegerField(default=0)
    f_nick = models.CharField(max_length=32)
    f_password = models.CharField(max_length=128)
    f_money_type = models.CharField(max_length=3)
    f_enabled = models.IntegerField(null=True, blank=True)
    f_strategy = models.CharField(max_length=32)
    f_status = models.IntegerField(default=0)
    f_status_expires = models.DateTimeField(default=datetime.datetime.now())
    f_min_bb = models.IntegerField()
    f_max_bb = models.IntegerField()
    f_bb_exit = models.FloatField()


class BotTable(models.Model):
    class Meta:
        db_table = u't_bot_table'
        managed = False
        
    id = models.AutoField(primary_key=True, db_column="f_id")
    bot = models.ForeignKey(Bot, db_column="f_bot_id")

    f_table_id = models.IntegerField(default=0)
    f_table_name = models.CharField(max_length=255)
    f_strategy = models.CharField(max_length=32)
    f_enabled = models.IntegerField()
    f_status = models.IntegerField(default=0)
    f_last_enter_time = models.DateTimeField(default=datetime.datetime.now())
    f_last_exit_time = models.DateTimeField(default=datetime.datetime.now())
    f_last_msg = models.CharField(max_length=255)
    f_min_bb = models.IntegerField()
    f_max_bb = models.IntegerField()
    f_bb_exit = models.FloatField()


class BotTableHistory(models.Model):
    class Meta:
        db_table = u't_bot_table_history'
        managed = False
        
    id = models.AutoField(primary_key=True, db_column="f_id")
    f_bot_nick = models.CharField(max_length=32)
    f_table_name = models.CharField(max_length=255)
    f_strategy = models.CharField(max_length=32)
    f_funds_in = models.BigIntegerField()
    f_funds_out = models.BigIntegerField(null=True, blank=True)
    f_enter_time = models.DateTimeField()
    f_exit_time = models.DateTimeField()
    f_exit_type = models.CharField(max_length=32)
    f_message = models.CharField(max_length=255)


class Config(models.Model):
    class Meta:
        db_table = u't_config'
        managed = False
        
    id = models.AutoField(primary_key=True, db_column="f_id")
    f_name = models.CharField(max_length=125, unique=True)
    f_clear_name = models.CharField(max_length=255)
    f_value = models.CharField(max_length=128)
    
class BotMonitor(models.Model):
    class Meta:
        db_table = u't_bot_monitor'
        managed = False
        
    id = models.AutoField(primary_key=True, db_column="f_id")
    f_nick = models.CharField(max_length=32)
    f_table = models.CharField(max_length=255)
    f_strategy = models.CharField(max_length=32)
    f_seat = models.IntegerField()
    f_hole1 = models.CharField(max_length=8)
    f_hole2 = models.CharField(max_length=8)
    f_game_id = models.BigIntegerField()

class BotTableChat(models.Model):
    class Meta:
        db_table = u't_bot_table_chat'
    
    id = models.AutoField(primary_key=True, db_column="f_id")
    f_bot_nick = models.CharField(max_length=32)
    f_table_name = models.CharField(max_length=255)
    f_message = models.CharField(max_length=128, null=False)
    f_time = models.DateTimeField(auto_now_add=True)    

class BotTournament(models.Model):
    class Meta:
        db_table = u't_bot_tournament'
        managed = False
        
    id = models.AutoField(primary_key=True, db_column="f_id")
    bot = models.ForeignKey(Bot, db_column="f_bot_id")

    f_table_name = models.CharField(max_length=255)
    f_strategy = models.CharField(max_length=32)
    f_enabled = models.IntegerField()
    f_rebuy = models.IntegerField(default=1)
    f_addon = models.IntegerField(default=0)

class BotSchedule(models.Model):
    class Meta:
        db_table = u't_bot_schedule'
        
    id = models.AutoField(primary_key=True, db_column="f_id")
    f_name = models.CharField(max_length=128, unique=True)
    f_from_time = models.CharField(max_length=32)
    f_to_time = models.CharField(max_length=32)
    
    f_num_bots = models.IntegerField(default=0)
    f_enabled = models.IntegerField()

    f_tables = models.CharField(max_length=1024)    
    f_nicks = models.CharField(max_length=1024)


class PlayerHand(models.Model):
    class Meta:
        db_table = u't_players_hands'
        
    id = models.AutoField(primary_key=True, db_column="f_id")
    f_game_id = models.IntegerField(default=0)
    f_player_id = models.IntegerField(default=0)
    f_hole1 = models.CharField(max_length=2)
    f_hole2 = models.CharField(max_length=2)    
    f_nick = models.CharField(max_length=128)
    f_ts = models.DateTimeField(auto_now_add=True)    
    