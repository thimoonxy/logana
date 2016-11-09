# logana
![image](https://github.com/thimoonxy/logana/blob/master/docs/logo.jpg)

Logana.py is a CLI help neteng and sysadmin speed up analyse varnish logs.

It's able go through either plain or rotated gzip files under default /opt/varnish/ folder, depending on the time period that being queried.

Here's also a golang version, without using method of bisection, but it should be good enough to check live logs on platform where has no python installed.
Please check the repo [go-logana](https://github.com/thimoonxy/practiceGo/tree/master/logana).

## Install

```
$easy_install logana
```
or

```
$ pip install logana
```
## Usage
```
$ python logana.py --help
Usage: logana [options]
 
Options:
  -s START_TIME, --query_start_time=START_TIME
                        Specify the isoformat BeiJing query_start_time. If not
                        use this, checks last 8h.
  -e END_TIME, --query_end_time=END_TIME
                        Specify the isoformat BeiJing query_end_time.If not
                        use this, checks last 8h.
  -l LAST, --last=LAST  Specify last time number to filter .e.g. -l 5H, -l 3s,
                        -l 10min etc. If not use this, checks last 8h.
  -k KEYWORD, --keyword=KEYWORD
                        Specify only showing the statistic of a log field. eg.
                        UA, url, size, code, client_ip, http_method, protocal
                        etc. Specially, when use size without --detail, it
                        shows Traffice and BW info.
  -v FIELD_VALUE, --field_value=FIELD_VALUE
                        Specify only showing lines matched with filtered field
                        value.
  -d DEPTH, --depth=DEPTH
                        Specify the depth of folders for url. e.g. -d 3
                        indicates: www.foo.com/1/2/3/
  -?, --help            varnish log analysis tool.
  -a, --all
```

## Regarding efficiency of querying big log data 
When analysing G level plain and compressed log data, locating timestamp hinders query efficiency. 
Here we use method of bisection, with 20 times slicing.

```
def position_acc(file_object,query_utc_start_datetime,start_pos = 0,end_pos=0,count=20):
```

> When it's M level, let's say maybe 500M log file, count=8 should be fine enough.

### Here are some experiment samples:

#### Experiment 1

Compression ratio| File size | File type
---|---|---
1:10 | 430M | Gzip

Slice count | Elapsed | Best
---|---|---
2 | 128s|
3 | 145s|
4 | 159s|
5 | 137s|
6 | 110s|
7 | 105s|
8 | 100s| √
9 | 120s|

#### Experiment 2

Compression ratio| File size | File type
---|---|---
- | 3.2G | Plain

Slice count | Elapsed | Best
---|---|---
6  | 15s  |
8  | 8s   |
12 | 6.8s | √
20 | 7s   |

#### Experiment 3

Compression ratio| File size | File type
---|---|---
- | 18G | Plain

Slice count | Elapsed | Best
---|---|---
8   | 20.76s  | 
20  |   9.45s |  √


## CLI Examples

#### Example 1

- Running directly without orgs/flags specified, it shows http code count ranking by default :

```
root@foo:~# logana
Note: Use --all to show all entries.
Percent        Count          Field - code          
___________________________________
98.24%         22802          200           
1.14%          265            304           
0.62%          144            404           
___________________________________
Totally 23211 lines during the query time period.
Filtered 3 statistic entries per field type code.
Note:Use --all to show all entries.
___________________________________
Queried Files:
    ['/opt/varnish/varnishncsa.log']
Query took 5.67 seconds for logs during server time:
From server timestamp: 21/Jan/2016:01:58:01
Till server timestamp: 21/Jan/2016:01:59:00
```

#### Example 2

- Log field specified as keyword FQDN, UA,  url,  size,  code,  client_ip,  http_method,  protocal etc.:
```
root@foo:~# logana --key FQDN
Note: Use --all to show all entries.
Percent        Count          Field - FQDN          
___________________________________
92.35%         20878          store.foo.com.cn
7.65%          1729           cdn.foo.com.cn:80
 
___________________________________
Totally 22607 lines during the query time period.
Filtered 2 statistic entries per field type FQDN.
Note:Use --all to show all entries.
 
___________________________________
Queried Files:
    ['/opt/varnish/varnishncsa.log']
 
Query took 6.29 seconds for logs during server time:
 
From server timestamp: 21/Jan/2016:02:01:28
Till server timestamp: 21/Jan/2016:02:02:27
```

#### Example 3
- Filter specific field value you want, print 1st and last 10 lines for short. Use --all to show all matching log lines:
```
root@foo:~# logana --k code -v 40
115.231.65.7    21/Jan/2016:02:07:44 HEAD  http  404   0     http://cdn.foo2.com.cn:80/favicon.ico                                           -                                                                              
115.231.65.7    21/Jan/2016:02:07:44 HEAD  http  404   0     http://cdn.foo2.com.cn:80/favicon.ico                                           -                                                                              
115.231.65.7    21/Jan/2016:02:07:44 HEAD  http  404   0     http://cdn.foo2.com.cn:80/favicon.ico                                           -                                                                              
115.231.65.7    21/Jan/2016:02:07:44 GET   http  404   0     http://cdn.foo2.com.cn:80/favicon.ico                                           -                                                                              
115.231.65.7    21/Jan/2016:02:07:47 HEAD  http  404   0     http://cdn.foo2.com.cn:80/favicon.ico                                           -                                                                              
115.231.65.7    21/Jan/2016:02:07:50 HEAD  http  404   0     http://cdn.foo2.com.cn:80/favicon.ico                                           -                                                                              
115.231.65.7    21/Jan/2016:02:07:51 HEAD  http  404   0     http://cdn.foo2.com.cn:80/favicon.ico                                           -                                                                              
115.231.65.7    21/Jan/2016:02:07:52 HEAD  http  404   0     http://cdn.foo2.com.cn:80/favicon.ico                                           -                                                                              
115.231.65.7    21/Jan/2016:02:07:52 HEAD  http  404   0     http://cdn.foo2.com.cn:80/favicon.ico                                           -                                                                              
115.231.65.7    21/Jan/2016:02:07:53 HEAD  http  404   0     http://cdn.foo2.com.cn:80/favicon.ico                                           -                                                                              
......
115.231.65.7    21/Jan/2016:02:08:38 GET   http  404   131   http://cdn.foo2.com.cn:80/apps/foo2/images/leagues/3671/0/0_datafile.txt       Valve/Steam HTTP Client 1.0 (570)                                              
115.231.65.7    21/Jan/2016:02:08:38 HEAD  http  404   0     http://cdn.foo2.com.cn:80/favicon.ico                                           -                                                                              
115.231.65.7    21/Jan/2016:02:08:38 GET   http  404   0     http://cdn.foo2.com.cn:80/favicon.ico                                           -                                                                              
115.231.65.7    21/Jan/2016:02:08:38 HEAD  http  404   0     http://cdn.foo2.com.cn:80/favicon.ico                                           -                                                                              
115.231.65.7    21/Jan/2016:02:08:39 GET   http  404   0     http://cdn.foo2.com.cn:80/favicon.ico                                           -                                                                              
115.231.65.7    21/Jan/2016:02:08:39 GET   http  404   0     http://cdn.foo2.com.cn:80/favicon.ico                                           -                                                                              
115.231.65.7    21/Jan/2016:02:08:40 HEAD  http  404   0     http://cdn.foo2.com.cn:80/favicon.ico                                           -                                                                              
115.231.65.7    21/Jan/2016:02:08:40 HEAD  http  404   0     http://cdn.foo2.com.cn:80/favicon.ico                                           -                                                                              
115.231.65.7    21/Jan/2016:02:08:41 GET   http  404   0     http://cdn.foo2.com.cn:80/favicon.ico                                           -                                                                              
115.231.65.7    21/Jan/2016:02:08:41 HEAD  http  404   0     http://cdn.foo2.com.cn:80/favicon.ico                                           -                                                                              
 
___________________________________
Totally 20831 lines during the query time period.
Filtered 74 statistic entries per field type code.
Note:Use --all to show all entries.
 
___________________________________
Queried Files:
    ['/opt/varnish/varnishncsa.log']
 
Query took 4.83 seconds for logs during server time:
 
From server timestamp: 21/Jan/2016:02:07:42
Till server timestamp: 21/Jan/2016:02:08:41
```

#### Example 4
Use --depth to indicate how depth of the url path you want to analyse. e.g. -d 2 means http://foo.com/path1/path2/ : 
```
root@foo2:~# logana --k url  --depth 2
Note: Use --all to show all entries.
Percent        Count          Field - url           
___________________________________
62.20%         13043          http://store.foo2.com.cn//webapi/
12.13%         2543           http://store.foo2.com.cn/webapi/IChat/
6.02%          1262           http://cdn.foo2.com.cn:80/steamcommunity/public/
4.40%          923            http://store.foo2.com.cn/feed/?language=schinese&l=schinese/
4.37%          916            http://store.foo2.com.cn/webapi/IEconomy/
2.75%          577            http://store.foo2.com.cn/frontpage?lv=1&c=RMB&l=schinese/
1.44%          301            http://store.foo2.com.cn/public/css/
1.22%          256            http://store.foo2.com.cn/watch/76561197960265728?streamonly=1/
0.92%          192            http://cdn.foo2.com.cn:80/apps/570/
0.62%          129            http://store.foo2.com.cn//jsfeed/
......
0.00%          1              http://store.foo2.com.cn/feed/?account_id=243002388&language=schinese&self_only=true&l=schinese/
0.00%          1              http://store.foo2.com.cn/feed/?account_id=164643312&language=schinese&self_only=true&l=schinese/
0.00%          1              http://store.foo2.com.cn/feed/?account_id=138679560&language=schinese&self_only=true&l=schinese/
0.00%          1              http://store.foo2.com.cn/feed/?account_id=317059948&language=schinese&self_only=true&l=schinese/
0.00%          1              http://store.foo2.com.cn/feed/?account_id=146531488&language=schinese&self_only=true&l=schinese/
0.00%          1              http://store.foo2.com.cn/feed/?account_id=317591913&language=schinese&self_only=true&l=schinese/
0.00%          1              http://store.foo2.com.cn/feed/?account_id=139998997&language=schinese&self_only=true&l=schinese/
0.00%          1              http://store.foo2.com.cn/feed/?account_id=152201006&language=schinese&self_only=true&l=schinese/
0.00%          1              http://store.foo2.com.cn/feed/?account_id=136397615&language=schinese&self_only=true&l=schinese/
0.00%          1              http://store.foo2.com.cn/feed/?account_id=145705559&language=schinese&self_only=true&l=schinese/
 
___________________________________
Totally 20969 lines during the query time period.
Filtered 518 statistic entries per field type url.
Note:Use --all to show all entries.
 
___________________________________
Queried Files:
    ['/opt/varnish/varnishncsa.log']
 
Query took 5.27 seconds for logs during server time:
 
From server timestamp: 21/Jan/2016:02:06:38
Till server timestamp: 21/Jan/2016:02:07:37

```

#### Example  5
- Use --size (without --all), it shows the bandwitdh of traffic info:
```
root@foo2:~# logana -k size
Note: Use --all to show all entries.
Percent        Count          Field - size          
___________________________________
0.00%          0.16           Traffic/TB    
100.00%        23198.0        Ave_BW/Kbps   
___________________________________
Totally 20046 lines during the query time period.
Filtered 2 statistic entries per field type size.
Note:Use --all to show all entries.
___________________________________
Queried Files:
    ['/opt/varnish/varnishncsa.log']
Query took 5.03 seconds for logs during server time:
From server timestamp: 21/Jan/2016:02:12:59
Till server timestamp: 21/Jan/2016:02:13:58

```


#### Example 6

- Use --last to show last foo time log report, code count ranking by default:

```
root@foo2:~# logana --last 15s
Note: Use --all to show all entries.
Percent        Count          Field - code          
___________________________________
98.24%         5125           200           
1.28%          67             304           
0.48%          25             404           
___________________________________
Totally 5217 lines during the query time period.
Filtered 3 statistic entries per field type code.
Note:Use --all to show all entries.
___________________________________
Queried Files:
    ['/opt/varnish/varnishncsa.log']
Query took 4.44 seconds for logs during server time:
From server timestamp: 21/Jan/2016:02:11:57
Till server timestamp: 21/Jan/2016:02:12:11
```

#### Example 7

- Use --start and --end to specific a time period:

```
root@foo2:~# logana -s 2016-01-21T06:00:00 -e 2016-01-21T07:00:00
Note: Use --all to show all entries.
Percent        Count          Field - code          
___________________________________
98.06%         195348         200           
1.11%          2217           304           
0.82%          1631           404           
0.01%          26             503           
___________________________________
Totally 199222 lines during the query time period.
Filtered 4 statistic entries per field type code.
Note:Use --all to show all entries.
___________________________________
Queried Files:
    ['/opt/varnish/varnishncsa.log']
Query took 15.98 seconds for logs during server time:
From server timestamp: 20/Jan/2016:17:00:00
Till server timestamp: 20/Jan/2016:18:00:00

```


## Todo list
 - [x] ** Basic function **
 - []  ** Log file path customization, instead of firmly read from /opt/varnish/ **


## Reference
Here's also a golang version, without using method of bisection, but it should be good enough to check live logs on platform where has no python installed.
Please check the repo [go-logana](https://github.com/thimoonxy/practiceGo/tree/master/logana).

For more ops tools, check [opsPykit](https://github.com/thimoonxy/opsPyKit).
