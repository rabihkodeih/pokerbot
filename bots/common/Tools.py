'''
Created on Aug 31, 2012

@author: Shadi Moodad
'''
from bots.common.Config import SiteConfig
from django.core.context_processors import csrf
import logging
import math
import types

log = logging.getLogger(__name__)

def toAutoCompleteMap(uid, label, value):
    return {'id': uid, 'label': label, 'value': value}

def isNumber(nbStr):
    isNum = False
    
    try:
        float(nbStr)
        isNum = True
    except:
        pass
            
    return isNum

def toFloat(nbr):
    '''
     Check if the nubmer is float then it returns it as is. if not then it checks if number and returns it
     if not then it checks if the input is empty then returns zero otherwise will return the input unchanged
    '''
    if isinstance(nbr, types.FloatType):
        return nbr
    elif isNumber(nbr):
        return float(nbr)
    else:
        return nbr if str(nbr).strip() != '' else float(0);
    
def toInt(nbr):
    '''
     Check if the nubmer is int then it returns it as is. if not then it checks if number and returns it
     if not then it checks if the input is empty then returns zero otherwise will return the input unchanged
    '''
    if isinstance(nbr, types.IntType):
        return nbr
    elif isNumber(nbr):
        return int(float(nbr))
    else:
        return nbr if str(nbr).strip() != '' else int(0);
    
    
def defaultContextData(request, ctx={}):
    """"
     Inject in a context the default attributes used in most pages. 
     ctx['user'] if authenticated
     csrf initialization
     ctx['APP_NAME'] in order to be changed on the file without the need to hard code it 
    """
    
    if request.user is not None and request.user.is_authenticated():
        ctx['user'] = request.user
    
    ctx['config'] = SiteConfig()
    
    ctx.update(csrf(request))
    
    ctx['APP_NAME'] = 'Bots Management'
    
    return ctx;
    
def populateContextForGrid(ctx, rs, rows, page, sidx, sord):
    """
     Fils the necessary data for the grid in order to be used in the XML data of the JQGrid .
     @param rs: the result set returned from the execution of ModelClass.objects.all() or ModelClass.objects.filter()
     @param rows: number of rowas per page
     @param page: page number
     @sidx: sort index
     @sord: sort order "asc" or "desc".
     
     Note: all those parameters: rows, page, sidx, sord are returned from the JQGrid 
    """
    
    rows = int(rows)
    page = int(page)
    
    totalRecords = rs.count()
    
    sortOn = "-" + sidx if sord == "desc" else sidx
    
    rs = rs.order_by(sortOn)[(page - 1) * rows: page * rows]
    
    ctx['grid'] = list(rs)
    ctx['page'] = page
    ctx['totalRecords'] = totalRecords
    ctx['totalPages'] = math.ceil(float(totalRecords) / rows)
    ctx['rows'] = rows

    
    return ctx;


