url = "https://stat.ripe.net/data/network-info/data.json?resource=" + ip + "&sourceapp=uninett"
response = urllib.request.urlopen(url)
data = json.loads(response.read().decode('utf-8'))

url = "https://stat.ripe.net/data/bgp-updates/data.json?resource=" \
      + all_prefixes + "&endtime=" + stoptime + "&starttime=" + starttime + "&unix_timestamps=true&sourceapp=uninett"
response = urllib.request.urlopen(url)
data = json.loads(response.read().decode('utf-8'))
