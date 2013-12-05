# -*- coding: utf-8 -*-


def run_after(main):
    import urllib2
    opener = urllib2.build_opener(urllib2.HTTPHandler)
    purge_url = 'http://localhost:5100'
    request = urllib2.Request(purge_url)
    request.add_header('X-Cache-Recursive', '1')
    request.get_method = lambda: 'PURGE'
    url = opener.open(request)
    response_code = url.getcode()
    if response_code != 200:
        print "HTTP Error: {0} for {1}".format(response_code, url.geturl())
    else:
        print "Notification to clean cache was successful"

def run_after_CLEAN_BY_GRAPH(main):
    graph_uri = main.config.get('database_graph')

    import urllib2
    opener = urllib2.build_opener(urllib2.HTTPHandler)
    BRAINIAK_ENDPOINT = 'http://localhost:5100/_?graph_uri={0}'
    purge_url = BRAINIAK_ENDPOINT.format(graph_uri)

    request = urllib2.Request(purge_url)
    request.add_header('X-Cache-Recursive', '1')
    request.get_method = lambda: 'PURGE'
    url = opener.open(request)
