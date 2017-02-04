import json
import subprocess

from haikunator import Haikunator

#TODO experiments in the future (timestamped)

class MonroeExperiment:
    def __init__(self, name=None, script="monroe/base",
                 nodecount=1, duration=300, testing=False):
        # Initialise basic options
        self.name = name if name is not None else Haikunator().haikunate()
        self.script = script
        self.start = 0
        self.stop = int(duration)
        self.nodetype = 'type:testing' if testing else 'type:deployed'
        
        # Initialise advanced options
        self.countries = None
        self.nodes = None
        self.traffic = 1048576
        self.resultsQuota = 0
        self.shared = 0
        self.storage = 128
        self.jsonstr = None
        self.sshkey = None
        self.recurrence = None
        self.period = None
        self.until = None

    def set_countries(self, country_list):
        for item in country_list:
            self.countries.append(item)

    def set_nodes(self, nodelist):
        for item in nodelist:
            self.nodes.append(item)

    def set_jsonstr(self, string):
        self.jsonstr = json.loads(string)

    def set_sshkey(self, string):
        self.sshkey = string

    def set_recurrence(self, rtype, period, until):
        self.recurrence = rtype
        self.period = period
        self.until = until
        
    def prepareJson(self):
        options = {}
        postrequest = {}
        ntype = []
        if self.countries is not None:
            l = len(self.countries)
            c = 1
            ret = ""
            for item in self.countries:
                ret += "country:" + item
                if c < l:
                    ret += "|"
                c += 1
            ntype.append(ret)

        ntype.append(self.nodetype)

        options['traffic'] = self.traffic
        options['resultsQuota'] = self.resultsQuota
        options['shared'] = self.shared
        options['storage'] = self.storage
        if self.recurrence is not None:
            options['recurrence'] = self.recurrence
            options['period'] = self.period
            options['until'] = self.until
        if self.sshkey is not None:
            if self.recurrence is not None:
                print("Error. Cannot deploy SSH tunnel with recurrent events!")
            else:
                options['ssh'] = json.dumps({
                    "server": "tunnel.monroe-system.eu",
                    "server.port": 29999,
                    "server.user": "tunnel",
                    "client.public": self.sshkey
                })
        if self.nodes is not None:
            options['nodes'] = json.dumps(self.nodes)

        postrequest['name'] = self.name
        postrequest['nodecount'] = self.nodecount
        postrequest['nodetypes'] = ','.join(ntype)
        postrequest['options'] = json.dumps(options)
        postrequest['script'] = self.script
        postrequest['start'] = self.start
        postrequest['stop'] = self.stop
        return json.dumps(postrequest)


class _MonroeAuth:
    def __init__(self, cert, key):
        self.cert = cert
        self.key = key
        self.endp = "https://www.monroe-system.eu"

    def get_monroe(self, endpoint):
        url = self.endp + endpoint
        cmd = [
            'wget', '-O', '-', '--certificate', self.cert, '--private-key',
            self.key, url
        ]
        response = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        return json.loads(response.communicate()[0].decode())

    def post_monroe(self, endpoint, postrequest):
        url = self.endp + endpoint
        cmd = [
            'wget', '--certificate', self.cert, '--private-key', self.key,
            '--post-data=' + postrequest,
            '--header=Content-Type:application/json', url, '-O', '-'
        ]
        response = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return response.communicate()[0].decode()
    def download_monroe(self, endpoint):
        url = seld.endp + endpoint
        cmd = [
            'wget', '--certificate', self.cert, '--private-key',
            self.key, url
        ]
        response = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        return json.loads(response.communicate()[0].decode())
        
    def get_auth(self):
        endpoint = "/v1/backend/auth"
        return self.get_monroe(endpoint)

    def get_journals(self):
        res = self.get_auth()
        endpoint = "/v1/users/%s/journals" % res['user']['id']
        return self.get_monroe(endpoint)

    def get_resources(self):
        endpoint = "/v1/resources/"
        return self.get_monroe(endpoint)

    def get_experiments(self):
        res = self.get_auth()
        endpoint = "/v1/users/%s/experiments" % res['user']['id']
        return self.get_monroe(endpoint)

    def get_schedule(self, experimentid):
        endpoint = "/v1/experiments/%s/schedules" % experimentid
        return self.get_monroe(endpoint)

    def submit_experiment(self, monroeExperiment):
        endpoint = "/v1/experiments"
        req = monroeExperiment.prepareJson()
        a = self.post_monroe(endpoint, req)
        try:
            return json.loads(a.split("--")[0])
        except:
            return 'Nodes not available. Check the availability for your experiment using get_availability!'

    def get_availability(self, duration, nodecount, nodetype, start):
        endpoint = "/v1/schedules/find?duration=%s&nodecount=%s&nodetypes=%s&start=%s" % (
            str(duration), str(nodecount), nodetypes, start)
        return json.loads(self.get_monroe(endpoint))
#TODO make it download in a sensible directory....
    def get_result(self, experimentid):
        endpoint = "/user/" + str(experimentid) + "/*"
        return download_monroe(endpoint)



