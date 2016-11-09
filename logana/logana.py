#!/usr/bin/python
# #encoding=utf8
__author__ = 'Simon Xie'
__email__ = 'thimoon@sina.com'
__version__ = 20160531
from optparse import OptionParser
import  StringIO
import gzip
import datetime
import time
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def locate_log_files(LogFilePath,FileNameKeyWord,query_utc_datetime_scope=None):
    walk = os.walk(LogFilePath)
    # print LogFilePath,FileNameKeyWord
    result_list = []
    tmp_dict = {}
    try:
        while True:
            for eachfile in walk.next()[-1]:
                if FileNameKeyWord in eachfile:
                    fname = os.path.join(LogFilePath,eachfile)
                    if 'gz' in fname:
                        g = gzip.GzipFile(fname,'rb')
                    else:
                        g = open(fname,'rb')
                    firstline = g.readline()
                    try:
                        utcstamp = log_field_extract(firstline)['timestamp_fmt']['utc']
                    except IndexError:
                        utcstamp = query_utc_datetime_scope[1] +datetime.timedelta(0, 28800)
                    g.close()
                    if firstline == '':
                        utcstamp = query_utc_datetime_scope[1] +datetime.timedelta(0, 28800)
                    if utcstamp > query_utc_datetime_scope[1]:
                        # print utcstamp,query_utc_datetime_scope[1]
                        pass
                    else:
                        tmp_dict[utcstamp]=fname
                    # result_list.append(fname)
    except StopIteration:
        # print tmp_dict.keys()
        time_order = tmp_dict.keys()
        time_order.sort(reverse=False)
        # print time_order
        if len(time_order) >=3:
            for x in range(len(time_order)):
                if x < len(time_order)-1:
                    if (time_order[x] <= query_utc_datetime_scope[0] <= time_order[x+1]) or query_utc_datetime_scope[0] < time_order[x] :
                        for y in range(x,len(time_order)):
                            result_list.append(tmp_dict[time_order[y]])
                        return result_list
                elif x == len(time_order) -1 and time_order[x] <= query_utc_datetime_scope[0]:
                    result_list.append(tmp_dict[time_order[x]])
                    # print 'test'
                    return result_list

        else:
            for key in time_order:
                result_list.append(tmp_dict[key])
        return result_list


def server2utc(server_stamp):
    now_stamp = time.time()
    local_time = datetime.datetime.fromtimestamp(now_stamp)
    utc_time = datetime.datetime.utcfromtimestamp(now_stamp)
    offset = local_time - utc_time
    server_datetime = datetime.datetime.fromtimestamp(server_stamp)
    return server_datetime - offset

def bj2utc(beijing_iso_time):
    """
    offset = beijing_time - utc_time
    """
    ISOSTRING = '%Y-%m-%dT%X'
    offset = datetime.timedelta(0, 28800)
    beijing_stamp = time.mktime(time.strptime(beijing_iso_time,ISOSTRING))
    beijing_datetime = datetime.datetime.fromtimestamp(beijing_stamp)
    utc_datetime = beijing_datetime - offset
    return  utc_datetime



def timestamp_handler(timestamp):
    ISOSTRING = '%Y-%m-%d %X'
    year = int(timestamp.split('/')[2].split(':')[0])
    month = timestamp.split('/')[1]
    day = int(timestamp.split('/')[0])
    hour = int(timestamp.split(':')[1])
    minute = int(timestamp.split(':')[2])
    second = int(timestamp.split(':')[3])
    timestamp_fmt = {}
    for x in range(1,13):
        # if  month in datetime.date(year,x,day).ctime():  # change day to 2 in case
        if  month in datetime.date(year,x,2).ctime():
            timestamp_fmt['datetime'] = datetime.datetime(year,x,day,hour,minute,second)
            timestamp_fmt['iso'] = time.strftime(ISOSTRING,timestamp_fmt['datetime'].timetuple())
            timestamp_fmt['stamp'] = time.mktime(time.strptime(timestamp_fmt['iso'],ISOSTRING))
            timestamp_fmt['utc'] = server2utc(timestamp_fmt['stamp'])
            return timestamp_fmt



def log_file_loader(log_file_list,query_utc_datetime_scope=None,depth=None):
    content_lines_list = []
    end_time = datetime.datetime.utcfromtimestamp(time.time())
    for eachfile in log_file_list:
        if 'gz' not in eachfile:
            f = open(eachfile,'rb')
            # f_buf = StringIO.StringIO(f.read())
            parm = 1
            size = os.stat(eachfile).st_size * parm - 500
            each_line =0
            pos = position_acc(f,query_utc_datetime_scope[0],start_pos = 0,end_pos=size)
            f.seek(pos)
            each_line = f.readline()
            while each_line != '':

                try:
                    each_line_fields  = log_field_extract(each_line,depth)
                except IndexError: #ignore the 1st call, due to non-integral concern
                    each_line = f.readline()
                    each_line_fields  = log_field_extract(each_line,depth)
                if query_utc_datetime_scope:
                    if   query_utc_datetime_scope[0]  <=  each_line_fields['timestamp_fmt']['utc'] <= query_utc_datetime_scope[1]:
                        # print eachfile
                        content_lines_list.append(each_line_fields)
                    #exit when finishes the last timestamp:
                    elif each_line_fields['timestamp_fmt']['utc'] > query_utc_datetime_scope[1]:
                        # f_buf.close()
                        f.close()
                        return content_lines_list
                else:

                    '''
                    latest 1 minutes data
                    '''
                    offset = datetime.timedelta(0, 1 * 60)
                    star_time = end_time - offset
                    if star_time <= each_line_fields['timestamp_fmt']['utc'] <= end_time:
                        content_lines_list.append(each_line_fields)
                    elif each_line_fields['timestamp_fmt']['utc'] > end_time:
                        # f_buf.close()
                        f.close()
                        return content_lines_list
                each_line = f.readline()
            # f_buf.close()
            f.close()
        else:
            g = gzip.GzipFile(eachfile)
            # g_buf = StringIO.StringIO(g.read())
            parm = 12
            size = os.stat(eachfile).st_size * parm - 500
            each_line =0
            pos = position_acc(g,query_utc_datetime_scope[0],start_pos = 0,end_pos=size)
            g.seek(pos)
            each_line = g.readline()
            while each_line != '':

            # for each_line  in    g.readlines():
                try:
                    each_line_fields  = log_field_extract(each_line,depth)
                except IndexError: #ignore the 1st call, due to non-integral concern
                    each_line = g.readline()
                    each_line_fields  = log_field_extract(each_line,depth)
                if query_utc_datetime_scope:
                    if   query_utc_datetime_scope[0]  <=  each_line_fields['timestamp_fmt']['utc'] <= query_utc_datetime_scope[1]:
                        content_lines_list.append(each_line_fields)
                    #exit when finishes the last timestamp:
                    elif each_line_fields['timestamp_fmt']['utc'] > query_utc_datetime_scope[1]:
                        # g_buf.close()
                        g.close()
                        return content_lines_list
                else:
                    '''
                    When no time_scope specified, shouldn't check into tar balls
                    '''
                    pass
                each_line = g.readline()
            # g_buf.close()
            g.close()
    return content_lines_list

def log_field_extract(log_line,depth=None):
    result_dict = {}
    client_ip = log_line.split()[0]
    timestamp = log_line.split()[3].split('[')[1]
    timestamp_fmt =timestamp_handler(timestamp)

    http_method = log_line.split()[5].split("\"")[1]
    raw_url = log_line.split()[6]
    protocal = raw_url.split(':')[0]
    FQDN = raw_url.split('/')[2]
    if depth:
        url = protocal + '://' + FQDN + '/'
        for x in range(depth):
            try:
                url += raw_url.split('/')[3+x]
                url += '/'
            except IndexError:
                pass
    else:
        url = raw_url
    code = log_line.split()[8]
    size = log_line.split()[9]
    UA = log_line.split("\"")[-2]

    result_dict['client_ip'] = client_ip
    result_dict['timestamp'] = timestamp
    result_dict['timestamp_fmt'] = timestamp_fmt
    result_dict['http_method'] = http_method
    result_dict['raw_url'] = raw_url
    result_dict['protocal'] = protocal
    result_dict['FQDN'] = FQDN
    result_dict['url'] = url
    result_dict['code'] = code
    result_dict['size'] = size
    result_dict['UA'] = UA
    # return client_ip,timestamp,timestamp_fmt,http_method,raw_url,protocal,FQDN, url , code ,size, UA
    return result_dict


def content_filter(content_lines_list,keyword=None,field_value=None,details=None):
    if field_value and keyword:
        result = []
    else:
        result = {}
    time_duration = content_lines_list[-1]['timestamp_fmt']['stamp'] - content_lines_list[0]['timestamp_fmt']['stamp']
    for each in content_lines_list:
        # print result
        if field_value and keyword:
            if keyword in each.keys():
                if field_value in each[keyword]:
                    result.append(each)
                    # result.append((each['client_ip'],each['timestamp'],each['http_method'],each['protocal'],each['code'],each['size'],each['url'],each['UA']))
                    # print each['client_ip'].ljust(15),each['timestamp'].ljust(10),each['http_method'].ljust(5),each['protocal'].ljust(5),each['code'].ljust(5),each['size'].ljust(5),each['url'].ljust(80),each['UA'].ljust(80)
        else:
            if keyword == 'size' and details is None:
                try:
                    result['Traffic/TB'] += int(each[keyword])
                except KeyError:
                    result.setdefault('Traffic/TB')
                    result['Traffic/TB'] = int(each[keyword])
                except ValueError:
                    pass
                result['Ave_BW/Kbps'] = result['Traffic/TB'] / time_duration *8 /1024
            elif keyword in each.keys():
                if each[keyword].strip() in result.keys():
                    result[each[keyword].strip()] += 1
                else:
                  result[each[keyword].strip()] = 1
            else:
                keyword = 'code'
                result.setdefault(each[keyword])
                result[each[keyword].strip()]=0
            # print result.keys()
            # print type(each[keyword].strip())
                if each[keyword].strip() in result.keys():
                    result[each[keyword].strip()] += 1
                else:
                    result[each[keyword].strip()] = 1
    if type(result) is list:
        if len(result) >50 and details is None:
            for x in range(0,10):
                each = result[x]
                # print each
                print each['client_ip'].ljust(15),each['timestamp'].ljust(10),each['http_method'].ljust(5),each['protocal'].ljust(5),each['code'].ljust(5),each['size'].ljust(5),each['url'].ljust(80),each['UA'].ljust(80)
            print "......"
            for x in range(len(result)-10,len(result)):
                each = result[x]
                print each['client_ip'].ljust(15),each['timestamp'].ljust(10),each['http_method'].ljust(5),each['protocal'].ljust(5),each['code'].ljust(5),each['size'].ljust(5),each['url'].ljust(80),each['UA'].ljust(80)
        else:
            for each in result:
                print each['client_ip'].ljust(15),each['timestamp'].ljust(10),each['http_method'].ljust(5),each['protocal'].ljust(5),each['code'].ljust(5),each['size'].ljust(5),each['url'].ljust(80),each['UA'].ljust(80)
    else:
        # print result
        result= sorted(result.iteritems(),key=lambda asd:asd[1], reverse=True)
        if keyword == 'size' and details is None:
            result = [(result[0][0],float('%.2f'%(result[0][1]/1024/1024/1024.0))),(result[1][0],float('%.2f'%result[1][1]))]
        sum =0.0
        for k,v in result:
            sum +=v
        print 'Note: Use --all to show all entries.'.ljust(15)
        print 'Percent'.ljust(15) +'Count'.ljust(15) + 'Field - %s'%keyword.ljust(15)
        print '___________________________________'
        if len(result) >50 and details is None:
            for x in range(0,10):
                k,v = result[x]
                print ('%.2f%%'%(v/sum*100)).ljust(15) + str(v).ljust(15) + str(k).ljust(15)
            print "......"
            for x in range(len(result)-10,len(result)):
                k,v = result[x]
                print ('%.2f%%'%(v/sum*100)).ljust(15) + str(v).ljust(15) + str(k).ljust(15)
        else:
            for k,v in result:
                print ('%.2f%%'%(v/sum*100)).ljust(15) + str(v).ljust(15) + str(k).ljust(15)

    print """
___________________________________
Totally %s lines during the query time period.
Filtered %s statistic entries per field type %s.
Note:Use --all to show all entries."""%(len(content_lines_list),len(result),keyword)
    return  result

def position_acc(file_object,query_utc_start_datetime,start_pos = 0,end_pos=0,count=8):
    '''
    Dichotomie method
    :param file_object:
    :param query_utc_start_datetime:
    :param start_pos:
    :param end_pos:
    :param count: define how many times to slice the scope
     Experimentally got the best count=8 to query 5min log contents in 430M gzip file (100s) and 3.2G plant text file (8s).
    :return:
    '''
    # if 'gz' in fname:
    #     parm = 12
    #     f = gzip.GzipFile(fname,'rb')
    #     size = os.stat(f).st_size * parm - 500
    # else:
    #     parm = 1
    #     f = open(fname,'rb')
    #     size = os.stat(f).st_size * parm - 500
    # end_post = size
    f = file_object
    mid_pos = ( start_pos + end_pos ) /2
    tell = f.seek(mid_pos)
    # ignore the 1st call after seek, since this line might not be integral
    mid_line_ignored = f.readline()
    mid_line = f.readline()

    #to prevent size defined so big
    roll = 6
    while mid_line == '' and roll !=0:
        end_pos = mid_pos
        mid_pos = ( start_pos + end_pos ) /2
        tell = f.seek(mid_pos)
        mid_line_ignored = f.readline()
        mid_line = f.readline()
        roll-=1

    # print mid_line
    mid_line_utc =  log_field_extract(mid_line)['timestamp_fmt']['utc']
    if  query_utc_start_datetime <= mid_line_utc:
        start_pos = start_pos
        end_pos = mid_pos
    else:
        start_pos = mid_pos
        end_pos = end_pos
    count -=1
    while count !=0:
        return position_acc(f,query_utc_start_datetime,start_pos,end_pos,count)
    return start_pos

def main():
    '''
    parser blocks:
    '''

    parser = OptionParser(add_help_option=False)
    parser.add_option('-s', '--query_start_time',
                                dest='start_time',
                                help='Specify the isoformat BeiJing query_start_time. If not use this, checks last 8h.')
    parser.add_option('-e', '--query_end_time',
                                dest='end_time',
                                help='Specify the isoformat BeiJing query_end_time.If not use this, checks last 8h.')
    parser.add_option('-l', '--last',
                                dest='last',
                                help='Specify last time number to filter .e.g. -l 5H, -l 3s, -l 10min etc. If not use this, checks last 8h.')
    parser.add_option('-k', '--keyword',
                                dest='keyword',
                                help='Specify only showing the statistic of a log field. eg. UA, url, size, code, client_ip, http_method, protocal etc. Specially, when use size without --detail, it shows Traffice and BW info.')
    parser.add_option('-v', '--field_value',
                                dest='field_value',
                                help='Specify only showing lines matched with filtered field value.')
    parser.add_option('-d', '--depth',
                                dest='depth',
                                help='Specify the depth of folders for url. e.g. -d 3 indicates: www.foo.com/1/2/3/')

    parser.add_option('-?', '--help',
                                action='store_true',
                                help='varnish log analysis tool.')
    def option_without_param(option, opt_str, value, parser):
        parser.values.details = True

    details = None
    parser.add_option("-a","--all", action="callback", callback=option_without_param)

    (options, args) = parser.parse_args()

    start_time = options.start_time
    end_time = options.end_time
    last = options.last
    keyword = options.keyword
    depth = options.depth
    field_value = options.field_value
    if depth !=None:
        depth=int(depth)
    try:
        if  options.details:
            details = options.details
    except AttributeError:
        details = None
    # print options
    # print details


    # if options.help or (start_time or end_time or keyword or field_value or depth) is None:
    if options.help :
        parser.print_help()
        parser.exit()

    try:
        if start_time and end_time:
            start_time = bj2utc(start_time)
            end_time = bj2utc(end_time)
            delta = end_time - start_time
            if delta.seconds/3600.0 >8 or delta.days > 0:
                print('Warning, Query time scope should not be longer than 8 hours, in case eats up Mem to affect server perf.')
                parser.exit()
            elif end_time < start_time:
                print('Warning, end timestamp is smaller than start timestamp.')
                parser.exit()
        elif start_time is not None and end_time is None:
            start_time = bj2utc(start_time)
            end_time = start_time + datetime.timedelta(0, 60)
        elif start_time is None and end_time is not None:
            end_time = bj2utc(end_time)
            start_time = end_time - datetime.timedelta(0, 60)
        elif last:
            end_time = datetime.datetime.utcfromtimestamp(time.time())
            # print last,end_time
            import re
            p =re.compile('([0-9]+\.?[0-9]*)(.*)')
            m = re.search(p,last)
            # print type(m.groups())
            last_value = float(m.groups()[0])

            last_unit = m.groups()[1]
            if last_unit.upper() in ['H','HOUR','HOURS']:
                start_time = end_time - datetime.timedelta(0, last_value * 60 * 60)
            elif last_unit.upper() in ['M','MIN','MINUTE','MINUTES']:
                start_time = end_time - datetime.timedelta(0, last_value * 60 )
            elif last_unit.upper() in ['S','SEC','SECOND','SECONDS']:
                start_time = end_time - datetime.timedelta(0, last_value)
            else:
                start_time = end_time - datetime.timedelta(0, 60)

        else:
            end_time = datetime.datetime.utcfromtimestamp(time.time())
            start_time = end_time - datetime.timedelta(0, 60)
        query_utc_datetime_scope = (start_time,end_time)
        # print(query_utc_datetime_scope)
    except:
        print('Note: time parm should be in isoformat like: 1970-01-01T01:00:00')
        parser.exit()

    '''
    variable blocks:
    '''
    if os.name !='posix':
        LogFilePath = 'C:\\Users\\simon\\Downloads'
    else:
        LogFilePath = '/opt/varnish/'
    FileNameKeyWord = 'varnishncsa'
    runtime_start = time.time()
    # print query_utc_datetime_scope
    log_file_list = locate_log_files(LogFilePath,FileNameKeyWord,query_utc_datetime_scope=query_utc_datetime_scope)

    if len(log_file_list) == 0:
        print("Wrong time scope, no log file located.")
        sys.exit()
    # for each in log_file_list:
    #     print datetime.datetime.fromtimestamp(os.path.getctime(each)).isoformat()
    content_lines_list = log_file_loader(log_file_list,query_utc_datetime_scope=query_utc_datetime_scope,depth=depth)
    if len(content_lines_list) ==0:
        print "Warning, got no content in result."
        sys.exit()
    result = content_filter(content_lines_list,keyword=keyword,field_value=field_value,details=details)
    runtime = time.time() - runtime_start
    print'''
___________________________________
Queried Files:
    %s'''%log_file_list
    print '''
Query took %.2f seconds for logs during server time:

From server timestamp: %s
Till server timestamp: %s
    '''%(runtime,content_lines_list[0]['timestamp'],content_lines_list[-1]['timestamp'])




if __name__ == '__main__':
    """
    parser block
    """
    #main block
    main()
    """
    117.14.57.115 - - [12/Jan/2016:06:54:12 -0500] "GET http://store.foo2.com.cn//path2/Ifoo2MatchStats/GetRealtimeStats/v001?server_game_id=123& HTTP/1.1" 304 0 "-" "Foo/game HTTP Client 1.0 (570)"

    ('117.14.57.115', '12/Jan/2016:06:54:12', datetime.datetime(2016, 1, 12, 6, 54, 12), 'GET', 'http://store.foo2.com.cn//path2/Ifoo2MatchStats/GetRealtimeStats/v001?server_game_id=123&', 'http', 'store.foo2.com.cn', 'http://store.foo2.com.cn//path2/Ifoo2MatchStats/GetRealtimeStats/v001?server_game_id=123&/', '304', '0', 'Foo/game HTTP Client 1.0 (570)')
    """

