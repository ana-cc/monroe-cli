import time
import datetime
import json
import subprocess
from collections import namedtuple
from haikunator import Haikunator

class Experiment:
    ''' 
    Class that models monroe experiments.
    '''

    def __init__(self, data):
        self._data = data

    def name(self, value=None):
        if value == None:
            return self._data['name'] 
        elif self._data['status'] == 'draft':
            self._data['name'] = value
        else:
            raise RuntimeError("Attempted to modify a non-draft experiment")
         
    def script(self, value=None):
        if value == None:
            return self._data['script'] 
        elif self._data['status'] == 'draft':
            self._data['script'] = value
        else:
            raise RuntimeError("Attempted to modify a non-draft experiment")

    def nodetype(self, value=None):
        if value == None:
            return self._data['nodetype'] 
        elif self._data['status'] == 'draft':
            self._data['nodetype'] = value
        else:
            raise RuntimeError("Attempted to modify a non-draft experiment")
    def id(self):
        return self._data['id'] 
    def ownerid(self):
        return self._data['ownerid'] 
    def status(self):
        return self._data['status'] 
    def summary(self):
        return self._data['summary']
    def status(self):
        return self._data['status']
    def duration(self, value=None):
        if value == None:
            return self._data['duration']
        elif self._data['status'] == 'draft':
            self._data['duration'] = value
            self._data['stop'] = self._data['start'] + int(self._data['duration'])
        else:
            raise RuntimeError("Attempted to modify a non-draft experiment")
    def start(self, value=None):
        if value == None:
            return int(self._data['start'])
        elif self._data['status'] == 'draft':
            try:
            	self._data['start']= time.mktime(datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S").timetuple())
            except:
                raise RuntimeError("String format as y-m-dTh:m:s")
            self._data['stop'] = self._data['start'] + int(self._data['duration'])
        else:
            raise RuntimeError("Attempted to modify a non-draft experiment")
    def stop(self):
        return int(self._data['stop'])
    
    def countries(self, value=None):
        if value == None:
            return self._data['countries'] 
        elif self._data['status'] == 'draft':
            self._data['countries'] = value
        else:
            raise RuntimeError("Attempted to modify a non-draft experiment")

    def traffic(self, value=None):
        if value == None:
            return self._data['options']['traffic'] 
        elif self._data['status'] == 'draft':
            self._data['options']['traffic'] = value
        else:
            raise RuntimeError("Attempted to modify a non-draft experiment")

    def shared(self, value=None):
        if value == None:
            return self._data['options']['shared'] 
        elif self._data['status'] == 'draft':
            self._data['options']['shared'] = value
        else:
            raise RuntimeError("Attempted to modify a non-draft experiment")

    def storage(self, value=None):
        if value == None:
            return self._data['options']['storage'] 
        elif self._data['status'] == 'draft':
            self._data['options']['storage'] = value
        else:
            raise RuntimeError("Attempted to modify a non-draft experiment")

    def nodes(self, value=None):
        if value == None:
            return self._data['options']['nodes'] 
        elif self._data['status'] == 'draft':
            self._data['options']['nodes'] = value
        else:
            raise RuntimeError("Attempted to modify a non-draft experiment")

    def jsonstr(self, value=None):
        if value == None:
            return self._data['jsonstr'] 
        elif self._data['status'] == 'draft':
            self._data['jsonstr'] = value
        else:
            raise RuntimeError("Attempted to modify a non-draft experiment")

    def sshkey(self, value=None):
        if value == None:
            return self._data['options']['sshkey'] 
        elif self._data['status'] == 'draft':
            self._data['options']['sshkey'] = value
        else:
            raise RuntimeError("Attempted to modify a non-draft experiment")

    def recurrence(self, rtype=None, period=None, until=None):
        if rtype == None:
            return self._data['options']['rtype'] 
        elif self._data['status'] == 'draft':
            if  period is not None and until is not None:
                self._data['options']['rtype'] = rtype
                self._data['options']['period'] = period
                self._data['options']['until'] = until
            else:
                raise RuntimeError("Need to specify a period and finish time")
        else:
            raise RuntimeError("Attempted to modify a non-draft experiment")

    def prepareJson(self):
        options = {}
        postrequest = {}
        ntype = []
        if self._data['countries'] is not None:
            l = len(self._data['countries'])
            c = 1
            ret = ""
            for item in self._data['countries']:
                ret += "country:" + item
                if c < l:
                    ret += "|"
                c += 1
            ntype.append(ret)

        ntype.append(self._data['nodetype'])

        options['traffic'] = self._data['options']['traffic']
        options['resultsQuota'] = self._data['options']['resultsQuota']
        options['shared'] = self._data['options']['shared']
        options['storage'] = self._data['options']['storage']
        if self._data['options']['recurrence'] is not None:
            options['recurrence'] = self._data['options']['recurrence']
            options['period'] = self._data['options']['period']
            options['until'] = self._data['options']['until']
        if self._data['options']['sshkey'] is not None:
            if self._data['options']['recurrence'] is not None:
                raise RuntimeError("Error. Cannot deploy SSH tunnel with recurrent events!")
            else:
                options['ssh'] = json.dumps({
                    "server": "tunnel.monroe-system.eu",
                    "server.port": 29999,
                    "server.user": "tunnel",
                    "client.public": self._data['options']['sshkey']
                })
        if self._data['options']['nodes'] is not None:
            options['nodes'] = json.dumps(self._data['options']['nodes'])

        postrequest['name'] = self._data['name']
        postrequest['nodecount'] = self._data['nodecount']
        postrequest['nodetypes'] = ','.join(ntype)
        postrequest['options'] = json.dumps(options)
        postrequest['script'] = self._data['script']
        postrequest['start'] = self._data['start']
        postrequest['stop'] = self._data['stop']
        return json.dumps(postrequest)


class Scheduler:
    def __init__(self, cert, key):
        self.cert = cert
        self.key = key
        self.endp = "https://scheduler.monroe-system.eu"
    # using wget as it's compiled against GNU TLS; anything using OpenSSL won't work due to MD5 hashes
    # to be changed once fed4fire updates the experimenter certificates  

    def get(self, endpoint):
        url = self.endp + endpoint
        cmd = [
            'wget', '--certificate', self.cert, '--private-key',
            self.key, url, '-O', '-'
        ]
        response = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        return json.loads(response.communicate()[0].decode())

    def post(self, endpoint, postrequest):
        url = self.endp + endpoint
        cmd = [
            'wget', '--certificate', self.cert, '--private-key', self.key,
            '--post-data=' + postrequest,
            '--header=Content-Type:application/json', url, '-O', '-'
        ]
        response = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return response.communicate()[0].decode()

    def download(self, endpoint, prefix):
        url = self.endp + endpoint
        cmd = [
            'wget','-r','-nH','--cut-dirs=1','--no-parent','-P',str(prefix),'--certificate', self.cert, '--private-key',
            self.key, url
        ]
        response = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return response.communicate()[0].decode()

    def delete (self, endpoint):
        url = self.endp + endpoint
        cmd = [
            'wget','--method=DELETE','--certificate', self.cert, '--private-key',
            self.key, url, '-O', '-'
        ]
        response = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return response.communicate()[0].decode()
        
    def auth(self):
        endpoint = "/v1/backend/auth"
        return Auth(self.get(endpoint))

    def journals(self):
        res = self.auth()
        endpoint = "/v1/users/%s/journals" % res.id()
        return [JournalEntry(e) for e in self.get(endpoint)]
    def nodes(self):
        endpoint = "/v1/resources/"
        return [ Node(e) for e in self.get(endpoint) ]

    def experiments(self):
        res = self.auth()
        endpoint = "/v1/users/%s/experiments" % res.id()
        obj = []
        exp =  self.get(endpoint) 
        return [Experiment(e) for e in exp]
         
    def schedules(self, experimentid):
        endpoint = "/v1/experiments/%s/schedules" % str(experimentid)
        res = self.get(endpoint)
        obj = {}
        for item in res['schedules'].keys():
            obj[item]= { "id": item, "nodeid" : res['schedules'][item]['nodeid'], "start": res['schedules'][item]['start'], "status" : res['schedules'][item]['status'], "stop" : res['schedules'][item]['stop'] }
        return [Schedule(e) for e in obj.values()]

    def submit_experiment(self, monroeExperiment):
        endpoint = "/v1/experiments"
        req = monroeExperiment.prepareJson()
        a = self.post(endpoint, req)
        try:
            return SubmissionReport(json.loads(a.split("--")[0]))
        except:
            return 'Nodes not available. Check the availability for your experiment using availability!'

    def new_experiment(self, name=None, script="monroe/base",
                 nodecount=1, duration=300, testing=False):
        data = {}
        options = {}
        data['status'] = "draft"
        data['ownerid']= self.auth().id()
        data['id'] = None
        data['summary'] = None
        # Initialise basic options
        data['name'] = name if name is not None else Haikunator().haikunate()
        data['script'] = script
        data['nodecount'] = nodecount
        data['start'] = 0
        data['stop'] = int(duration)
        data['duration'] = int(duration)
        data['nodetype'] = 'type:testing' if testing else 'type:deployed'
        
        # Initialise advanced options
        data['jsonstr'] = None
        data['countries'] = None
        options['nodes'] = None
        options['traffic'] = 1048576
        options['resultsQuota'] = 0
        options['shared'] = 0
        options['storage'] = 128
        options['sshkey'] = None
        options['recurrence'] = None
        options['period'] = None
        options['until'] = None
        data['options'] = options
        
        return Experiment(data)
    
    def delete_experiment(self, experimentid):
        endpoint = "/v1/experiments/%s/schedules" % str(experimentid)
        res = self.delete(endpoint)
        return res

    def get_availability(self, experiment=None):
        if experiment is not None:
            if experiment._data['status'] == 'draft':
                return self.availability(experiment._data['duration'], experiment._data['nodecount'], experiment._data['nodetype'], int(experiment._data['start']))
            else:
                raise RuntimeError("Can't check availability in the past")
        else:
            return self.availability()

    def availability(self, duration=300, nodecount=1, nodetype='type:testing', start=0):
        endpoint = "/v1/schedules/find?duration=%s&nodecount=%s&nodetypes=%s&start=%s" % (
            str(duration), str(nodecount), nodetype, start)
        return AvailabilityReport(self.get(endpoint)[0])

    def result(self, experimentid):
        schedules = self.schedules(experimentid)
        for item in schedules: 
            endpoint = "/user/" + str(item.id()) + "/"
            self.download(endpoint, experimentid)


class Auth:
    def __init__(self, data):
       self._data = data
    def fingerprint(self):
       return self._data['fingerprint']
    def verified(self):
       return self._data['verified']
    def id(self):
       return self._data['user']['id']
    def name(self):
       return self._data['user']['name']
    def quota_data(self):
       return self._data['user']['quota_data']
    def ssl_id(self):
       return self._data['user']['ssl_id']
    def quota_storage(self):
       return self._data['user']['quota_storage']
    def quota_time(self):
       return self._data['user']['quota_time']
    def role(self):
       return self._data['user']['role']
    def __repr__(self):
       return "<Auth id=%r name=%r >" % (self.id(), self.name())
    def __str__(self):
       return "<Authentication ID: %r, Name: %r, Storage Quota remaining: %r >" % (self.id(), self.name(), self.quota_storage())
 
 
class AvailabilityReport:
    def __init__(self, data):
       self._data = data
    def max_nodecount(self):
       return self._data['max_nodecount']
    def max_stop(self):
       return self._data['max_stop']
    def nodecount(self):
       return self._data['nodecount']
    def nodetypes(self):
       return self._data['nodetypes']
    def start(self):
       return self._data['start']
    def stop(self):
       return self._data['stop']
    def testing(self):
       return self._data['nodetypes'] == 'type:testing'
    def __repr__(self):
       return "<AvailabilityReport start=%r testing=%r max_nodecount=%r max_stop=%r >" % (self.start(), self.testing(), self.max_nodecount(), self.max_stop()) 

class SubmissionReport:
    def __init__(self, data):
       self._data = data
    def experiment(self):
       return self._data['experiment']
    def intervals(self):
       return self._data['intervals']
    def nodecount(self):
       return self._data['nodecount']
    def message(self):
       return self._data['message']
    def __repr__(self):
       return "<SubmissionReport message=%r >" % self.message()


class JournalEntry:
    def __init__(self, data):
       self._data = data
    def value(self):
       return self._data['new_value']
    def ownerid(self):
       return self._data['ownerid']
    def quota(self):
       return self._data['quota']
    def reason(self):
       return self._data['reason']
    def timestamp(self):
       return self._data['timestamp']
    def __repr__(self):
       return "<JournalEntry quota=%r reason=%r timestamp=%r>" % (self.value(), self.reason(), self.timestamp())
    def __str__(self):
       t = datetime.datetime.fromtimestamp(self.timestamp())
       return "%r : Remaining %r is %r, after %r." % (t.strftime('%Y-%m-%d'), self.quota(), self.value(), self.reason())



class Node:
    def __init__(self, data):
       self._data = data
    def heartbeat(self):
       return self._data['heartbeat']
    def hostname(self):
       return self._data['hostname']
    def id(self):
       return self._data['id']
    def model(self):
       return self._data['model']
    def project(self):
       return self._data['project']
    def site(self):
       return self._data['site']
    def status(self):
       return self._data['status']
    def nodetype(self):
       if 'type' in self._data.keys():
           return self._data['type']
       else:
           return 'undefined'
    def __repr__(self):
        return "<Node id=%r status=%r type=%r >" % (self.id(), self.status(), self.nodetype())

class Schedule:
    def __init__(self, data):
       self._data = data
    def id(self):
       return self._data['id']
    def nodeid(self):
       return self._data['nodeid']
    def start(self):
       return self._data['start']
    def stop(self):
       return self._data['stop']
    def status(self):
       return self._data['status']
    def __repr__(self):
       return "<Schedule id=%r nodeid=%r >"  % (self.id(), self.nodeid())
