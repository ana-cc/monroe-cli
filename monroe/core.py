import time
import datetime
import json
import subprocess
from collections import namedtuple

try:
    from haikunator import Haikunator
except ImportError:

    class Haikunator:
        def haikunate():
            return "ididntinstallhaikunator"


class Experiment:
    ''' 
    Class that models monroe experiments.
    '''

    def __init__(self, data):
        self._data = data

    def name(self, value=None):
        '''
        Sets the name of an experiment to ``value``, otherwise returns the name of the experiment when called with no argument.

        :param value: Experiment name
        :type value: string
        :returns: string 
        '''
        if value == None:
            return self._data['name']
        elif self._data['status'] == 'draft':
            self._data['name'] = value
        else:
            raise RuntimeError("Attempted to modify a non-draft experiment")

    def script(self, value=None):
        '''Sets the script (or image to be run) for an experiment to ``value``, otherwise returns the script for the experiment when called with no argument.

        :param value: Docker image or script name
        :type value: string
        :returns: string 
        '''
        if value == None:
            return self._data['script']
        elif self._data['status'] == 'draft':
            self._data['script'] = value
        else:
            raise RuntimeError("Attempted to modify a non-draft experiment")

    def nodetype(self, testing=False):
        '''Sets the nodetype for an experiment to testing if ``value`` is True, and deployed if ``value`` is False. Otherwise returns the nodetype for the experiment.

        :param testing: False for deployed nodes and True for testing nodes
        :type testing: boolean
        :returns: string -- Type of node to deploy on, either type:testing or type:deployed 
        '''
        if testing == None:
            return self._data['nodetype']
        elif self._data['status'] == 'draft':
            if testing == True:
                self._data['nodetype'] = 'type:testing'
            else:
                self._data['nodetype'] = 'type:deployed'

        else:
            raise RuntimeError("Attempted to modify a non-draft experiment")

    def id(self):
        '''Returns the id of an experiment, if it exists. Experiment ids are assigned at experiment submission

        :returns: int 
        '''
        return self._data['id']

    def ownerid(self):
        '''Returns the ID of the owner of an experiment. Owner IDs are assigned at experiment creation using the ``auth`` function.

        :returns: int 
        '''
        return self._data['ownerid']

    def status(self):
        '''Returns the status of an experiment. 

        :returns: string -- This can have the values ``draft``, ``requested``, ``deployed``, ``started``, ``failed`` or ``finished``
        '''
        return self._data['status']

    def summary(self):
        '''Returns the summary of an experiment, if it exists

        :returns: string
        '''
        return self._data['summary']

    def duration(self, value=None):
        '''Sets the duration of an experiment to ``value``, otherwise returns the duration of an experiment when called with no argument.

        :param value: Duration in number of seconds
        :type value: int
        :returns: int -- Duration of the experiment in seconds. 
        '''
        if value == None:
            return self._data['duration']
        elif self._data['status'] == 'draft':
            self._data['duration'] = value
            self._data['stop'] = self._data['start'] + int(self._data[
                'duration'])
        else:
            raise RuntimeError("Attempted to modify a non-draft experiment")

    def start(self, value=None):
        '''Sets the start date/time of an experiment to ``value``, otherwise returns the start date/time of an experiment.

        :param value: Start date and time in format ``%Y-%m-%dT%H:%M:%S``
        :type value: string
        :returns: int -- UNIX timestamp of the experiment start date or 0 if the experiment is scheduled to start as soon as possible
        '''
        if value == None:
            return int(self._data['start'])
        elif self._data['status'] == 'draft':
            try:
                self._data['start'] = time.mktime(
                    datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
                    .timetuple())
            except:
                raise RuntimeError("String format as y-m-dTh:m:s")
            self._data['stop'] = self._data['start'] + int(self._data[
                'duration'])
        else:
            raise RuntimeError("Attempted to modify a non-draft experiment")

    def stop(self):
        '''Returns the stop date/time of an experiment, which is calculated based on start time and duration.

        :returns: int -- UNIX timestamp of the experiment stop date or the duration of the experiment in seconds if scheduled to start as soon as possible
        '''
        return int(self._data['stop'])

    def countries(self, value=None):
        '''Sets the list of countries for an experiment to ``value``, otherwise returns the list of countries for the experiment if existing.

        :param value: List of countries 
        :type value: list
        :returns: list 
        '''
        if value == None:
            return self._data['countries']
        elif self._data['status'] == 'draft':
            self._data['countries'] = value
        else:
            raise RuntimeError("Attempted to modify a non-draft experiment")

    def traffic(self, value=None):
        '''Sets the data traffic usage for an experiment to ``value``, otherwise returns the data traffic usage set for the experimenti when called with no argument.

        :param value: Expected traffic usage per interface in bytes
        :type value: int
        :returns: int -- Expected traffic usage in bytes
        '''
        if value == None:
            return self._data['options']['traffic']
        elif self._data['status'] == 'draft':
            self._data['options']['traffic'] = value
        else:
            raise RuntimeError("Attempted to modify a non-draft experiment")

    def shared(self, value=None):
        '''Sets the log data usage for an experiment to ``value``, otherwise returns the log data usage set for the experiment when called with no argument.

        :param value: Expected log data usage per interface in bytes
        :type value: int
        :returns: int -- Expected log data usage in bytes
        '''
        if value == None:
            return self._data['options']['shared']
        elif self._data['status'] == 'draft':
            self._data['options']['shared'] = value
        else:
            raise RuntimeError("Attempted to modify a non-draft experiment")

    def storage(self, value=None):
        '''Sets the storage data usage for an experiment to ``value``, otherwise returns the storage data usage set for the experiment when called with no argument.

        :param value: Expected storage data usage per interface in bytes
        :type value: int
        :returns: int -- Expected storage data usage in bytes
        '''
        if value == None:
            return self._data['options']['storage']
        elif self._data['status'] == 'draft':
            self._data['options']['storage'] = value
        else:
            raise RuntimeError("Attempted to modify a non-draft experiment")

    def nodecount(self, value=None):
        '''Sets the number of nodes for an experiment to ``value``, otherwise returns the number of nodes set for the experiment when called with no argument.

        :param value: Number of nodes
        :type value: int
        :returns: int 
        '''
        if value == None:
            return self._data['nodecount']
        elif self._data['status'] == 'draft':
            self._data['nodecount'] = value
        else:
            raise RuntimeError("Attempted to modify a non-draft experiment")

    def nodes(self, value=None):
        '''Sets specific nodes for an experiment to ``value`` otherwise returns the nodes set for the experiment when called with no argument.

        :param value: List of nodes
        :type value: list
        :returns: list 
        '''
        if value == None:
            return self._data['options']['nodes']
        elif self._data['status'] == 'draft':
            self._data['options']['nodes'] = value
        else:
            raise RuntimeError("Attempted to modify a non-draft experiment")


    def jsonstr(self, value=None):
        '''Sets the additional option string for an experiment to ``value``, otherwise returns the additional option string set for the experiment when called with no argument.

        :param value: Additional options formatted as a python dict
        :type value: string
        :returns: string
        '''
        if value == None:
            return self._data['options']['jsonstr']
        elif self._data['status'] == 'draft':
            if isinstance(value, dict): 
                self._data['options']['jsonstr'] = value
            else:
                raise RuntimeError("Not a valid dict. JSON strings passed to the scheduler need to be python dictionaries")
        else:
            raise RuntimeError("Attempted to modify a non-draft experiment")

    def sshkey(self, value=None):
        '''Sets the ssh key for an experiment to ``value``, otherwise returns the ssh key set for the experiment when called with no argument.

        :param value: Text body of the public SSH key to be used to connect to the container
        :type value: string
        :returns: string
        '''
        if value == None:
            return self._data['options']['sshkey']
        elif self._data['status'] == 'draft':
            self._data['options']['sshkey'] = value
        else:
            raise RuntimeError("Attempted to modify a non-draft experiment")

    def recurrence(self, period=None, until=None):
        '''Sets recurrence options for an experiment. Called with no arguments, it returns the recurrence options of the experiment.

        :param period: Repeat frequency of the experiment, in seconds
        :type period: int
        :param until: Recurrence end date/time, in UNIX timestamp format
        :type until: int
        :returns: tuple -- Repeat frequency of the experiment and recurrence end date/time in UNIX timestamp format
        '''
        if period is None and until is None:
            return (self._data['options']['period'],
                    self._data['options']['until'])
        elif self._data['status'] == 'draft':
            if period is not None and until is not None:
                self._data['options']['recurrence'] = True
                self._data['options']['period'] = period
                self._data['options']['until'] = until
            else:
                raise RuntimeError("Need to specify a period and finish time")
        else:
            raise RuntimeError("Attempted to modify a non-draft experiment")

    def prepareJson(self):
        '''Returns a formatted JSON string which is suitable for passing to the scheduler backend via an http POST request.

        :returns: JSON string
        '''
        options = {}
        postrequest = {}
        ntype = []
        if len(self._data['countries']) > 0:
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
        if self._data['options']['recurrence'] is True:
            options['recurrence'] = 'simple'
            options['period'] = self._data['options']['period']
            options['until'] = self._data['options']['until']
        if self._data['options']['sshkey'] is not None:
            if self._data['options']['recurrence'] is True:
                raise RuntimeError(
                    "Error. Cannot deploy SSH tunnel with recurrent events!")
            else:
                options['ssh'] = {
                    "server": "tunnel.monroe-system.eu",
                    "server.port": 29999,
                    "server.user": "tunnel",
                    "client.public": self._data['options']['sshkey']
                }
        if len(self._data['options']['nodes']) > 0:
            options['nodes'] = ', '.join([str(i) for i in self._data['options']['nodes']])
        jinp =  self._data['options']['jsonstr']
        if len(jinp.keys()) > 0:        
            for item in jinp.keys():
                    options[item] = jinp[item]
        postrequest['name'] = self._data['name']
        postrequest['nodecount'] = self._data['nodecount']
        postrequest['nodetypes'] = ','.join(ntype)
        postrequest['options'] = json.dumps(options)
        postrequest['script'] = self._data['script']
        postrequest['start'] = self._data['start']
        postrequest['stop'] = self._data['stop']
        print (postrequest)
        return json.dumps(postrequest)

    def __repr__(self):
        return "<Experiment id=%r, script=%r, status=%r, summary=%r>" % (
            self.id(), self.script(), self.status(), self.summary())

    def __str__(self):
        return "Experiment ID: %s Name: %s Script: %s Summary: %s" % (
            str(self.id()), self.name(), self.script(), self.summary())


class Scheduler:
    ''' 
    Class that models the monroe scheduler functionality.
    '''

    def __init__(self, cert, key):
        self.cert = cert
        self.key = key
        self.endp = "https://scheduler.monroe-system.eu"

    # using wget as it's compiled against GNU TLS; anything using OpenSSL won't work due to MD5 hashes
    # to be changed once fed4fire updates the experimenter certificates  

    def get(self, endpoint):
        '''Function which performs an HTTP GET request against the target backend.

        :param endpoint: REST API endpoint
        :type endpoint: string
        :returns: string -- The response of the request
        '''
        url = self.endp + endpoint
        cmd = [
            'wget','--content-on-error', '--certificate', self.cert, '--private-key', self.key, url,
            '-O', '-'
        ]
        response = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        return json.loads(response.communicate()[0].decode())

    def post(self, endpoint, postrequest):
        '''Function which performs an HTTP POST request against the target backend.

        :param endpoint: REST API endpoint
        :type endpoint: string
        :returns: string -- The response of the request.
        '''
        url = self.endp + endpoint
        cmd = [
            'wget', '--content-on-error', '--certificate', self.cert,
            '--private-key', self.key, '--post-data=' + postrequest,
            '--header=Content-Type:application/json', url, '-O', '-'
        ]
        response = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return response.communicate()[0].decode()

    def download(self, endpoint, prefix):
        '''Function which downloads files from a given endpoint.

        :param endpoint: REST API endpoint
        :type endpoint: string
        :returns: string -- The response of the request.
        '''
        url = self.endp + endpoint
        cmd = [
            'wget', '-r', '-nH', '--cut-dirs=1', '--no-parent', '-P',
            str(prefix), '--certificate', self.cert, '--private-key', self.key,
            url
        ]
        response = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return response.communicate()[0].decode()

    def delete(self, endpoint):
        '''Function which performs an HTTP DELETE request against the target backend.

        :param endpoint: REST API endpoint
        :type endpoint: string
        :returns: string -- The response of the request.
        '''
        url = self.endp + endpoint
        cmd = [
            'wget', '--method=DELETE', '--certificate', self.cert,
            '--private-key', self.key, url, '-O', '-'
        ]
        response = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            return json.loads(response.communicate()[0].decode())
        except:
            raise RuntimeError("Could not perform action.")

    def auth(self):
        '''Returns an ``auth`` object associated with a user.'''
        endpoint = "/v1/backend/auth"
        return Auth(self.get(endpoint))

    def journals(self):
        '''Returns all ``JournalEntry`` objects associated with a user.'''
        res = self.auth()
        endpoint = "/v1/users/%s/journals" % res.id()
        return [JournalEntry(e) for e in self.get(endpoint)]

    def nodes(self):
        '''Returns all ``Node`` objects visible by the scheduler.'''
        endpoint = "/v1/resources/"
        return [Node(e) for e in self.get(endpoint)]

    def experiments(self):
        '''Returns last 50 ``Experiment`` objects associated to a user.'''
        res = self.auth()
        endpoint = "/v1/users/%s/experiments" % res.id()
        obj = []
        exp = self.get(endpoint)
        exp = exp[-50:]
        return [Experiment(e) for e in exp]

    def schedules(self, experimentid):
        '''Returns all ``Schedule`` objects associated with an experiment.'''
        endpoint = "/v1/experiments/%s/schedules" % str(experimentid)
        res = self.get(endpoint)
        obj = {}
        for item in res['schedules'].keys():
            obj[item] = {
                "id": item,
                "nodeid": res['schedules'][item]['nodeid'],
                "start": res['schedules'][item]['start'],
                "status": res['schedules'][item]['status'],
                "stop": res['schedules'][item]['stop']
            }
        return [Schedule(e) for e in obj.values()]

    def submit_experiment(self, monroeExperiment):
        '''Submits an experiment to the scheduler. Returns a ``SubmissionReport`` object.'''
        endpoint = "/v1/experiments"
        req = monroeExperiment.prepareJson()
        a = self.post(endpoint, req)
        try:
            return SubmissionReport(json.loads(a.split("--")[0]))
        except:
            return "Something went wrong. Check the experiment availability."

    def new_experiment(self,
                       name=None,
                       script="monroe/base",
                       nodecount=1,
                       duration=300,
                       testing=False):
        '''Returns an ``Experiment`` object with default options and ``draft`` status.'''
        data = {}
        options = {}
        data['status'] = "draft"
        data['ownerid'] = self.auth().id()
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
        data['countries'] = []
        options['nodes'] = []
        options['traffic'] = 1048576
        options['resultsQuota'] = 0
        options['shared'] = 0
        options['storage'] = 134217728
        options['sshkey'] = None
        options['recurrence'] = False
        options['jsonstr'] ={}
        options['period'] = None
        options['until'] = None
        data['options'] = options

        return Experiment(data)

    def delete_experiment(self, experimentid):
        '''Requests a deletion for a given experiment ID.'''
        endpoint = "/v1/experiments/%s/schedules" % str(experimentid)
        res = self.delete(endpoint)
        return res

    def get_availability(self, experiment=None):
        '''Returns an ``AvailabilityReport`` for a given experiment.'''
        if experiment is not None:
            if experiment._data['status'] == 'draft':
                return self.availability(experiment._data['duration'],
                                         experiment._data['nodecount'],
                                         experiment._data['nodetype'],
                                         experiment._data['countries'],
                                         experiment._data['options']['nodes'],
                                         int(experiment._data['start']))
            else:
                raise RuntimeError("Can't check availability in the past")
        else:
            return self.availability()

    def availability(self,
                     duration=300,
                     nodecount=1,
                     nodetype='type:testing',
                     countries=[],
                     nodes=[],
                     start=0):
        '''Produces and submits HTTP query string for given nodecount, duration and nodetype and returns an AvailabilityReport based on the returned response.'''
        if len(countries) > 0:
            l = len(countries)
            c = 1
            ret = ""
            for item in countries:
                ret += "country:" + item
                if c < l:
                    ret += "|"
                c += 1
            nodetype = ret +', '+ nodetype
        if len(nodes) > 0: 
            nodes = ','.join([str(i) for i in nodes])
            endpoint = "/v1/schedules/find?duration=%s&nodecount=%s&nodes=%s&nodetypes=%s&start=%s" % (
                str(duration), str(nodecount),nodes, nodetype, start)
        
        else:         
            endpoint = "/v1/schedules/find?duration=%s&nodecount=%s&nodetypes=%s&start=%s" % (
                str(duration), str(nodecount), nodetype, start)
        try:
            return AvailabilityReport(self.get(endpoint)[0])
        except:
            return self.get(endpoint)['message']

    def result(self, experimentid):
        '''Downloads the results for a given experiment ID in the current folder.'''
        schedules = self.schedules(experimentid)
        for item in schedules:
            endpoint = "/user/" + str(item.id()) + "/"
            self.download(endpoint, experimentid)


class Auth:
    ''' 
    Class that models monroe authentication.
    '''

    def __init__(self, data):
        self._data = data

    def fingerprint(self):
        '''
       Returns the SSL fingerprint of the user.

       :returns: string
       '''
        return self._data['fingerprint']

    def verified(self):
        ''' Returns the status of user verification.

       :returns: string
       '''
        return self._data['verified']

    def id(self):
        ''' Returns the unique identifier of the user.

       :returns: int
       '''
        return self._data['user']['id']

    def name(self):
        ''' Returns the name of the user.

       :returns: string
       '''
        return self._data['user']['name']

    def quota_data(self):
        ''' Returns the data quota status for the user.

       :returns: int
       '''
        return self._data['user']['quota_data']

    def ssl_id(self):
        ''' Returns the SSL ID of the user.

       :returns: string
       '''
        return self._data['user']['ssl_id']

    def quota_storage(self):
        ''' Returns the storage quota status for the user.

       :returns: int
       '''
        return self._data['user']['quota_storage']

    def quota_time(self):
        ''' Returns the time quota status for the user.

       :returns: int
       '''
        return self._data['user']['quota_time']

    def role(self):
        ''' Returns the user's assigned role.

       :returns: string
       '''
        return self._data['user']['role']

    def __repr__(self):
        return "<Auth id=%r name=%r >" % (self.id(), self.name())

    def __str__(self):
        return "Authentication ID: %s, Name: %s, Storage Quota remaining: %s bytes" % (
            str(self.id()), str(self.name()), str(self.quota_storage()))


class AvailabilityReport:
    ''' 
    Class that models experiment availability information.
    '''

    def __init__(self, data):
        self._data = data

    def max_nodecount(self):
        '''
       Returns the maximum number of nodes available for an experiment.
       
       :returns: int
       '''
        return self._data['max_nodecount']

    def max_stop(self):
        '''Returns the maximum time the experimental slot can be extended to.
       
       :returns: int -- Max end time is returned in UNIX timestamp format
       '''
        return self._data['max_stop']

    def nodecount(self):
        '''Returns the number of requested experimental nodes.
       
       :returns: int
       '''
        return self._data['nodecount']

    def nodetypes(self):
        '''Returns the type of requested nodes.
       
       :returns: string
       '''
        return self._data['nodetypes']

    def start(self):
        '''Returns the available start date and time of the requested experiment.
  
       :returns: int -- Start time is returned in UNIX timestamp format
       '''
        return self._data['start']

    def stop(self):
        '''Returns the available stop date and time of the requested experiment.
  
       :returns: int -- Stop time is returned in UNIX timestamp format
       '''
        return self._data['stop']

    def testing(self):
        '''Returns True if the experiment was requested on testing nodes.

       :returns: boolean
       '''
        return self._data['nodetypes'] == 'type:testing'

    def __repr__(self):
        return "<AvailabilityReport start=%r testing=%r max_nodecount=%r max_stop=%r >" % (
            self.start(), self.testing(), self.max_nodecount(),
            self.max_stop())

    def __str__(self):
        av = "Available slot starting at %s" % str(
            datetime.datetime.fromtimestamp(self.start()))
        fi = "Finishing at %s" % str(
            datetime.datetime.fromtimestamp(self.stop()))
        m = "The experiment could use up to %s nodes" % str(self.max_nodecount(
        ))
        de = "The experiment may be delayed or the slot extended until %s" % str(
            datetime.datetime.fromtimestamp(self.max_stop()))
        return "%s\n%s\n%s\n%s" % (av, fi, m, de)


class SubmissionReport:
    ''' 
    Class that models experiment submission information.
    '''

    def __init__(self, data):
        self._data = data

    def experiment(self):
        '''Returns an experiment ID for the submitted experiment.'''
        return self._data['experiment']

    def intervals(self):
        '''Returns the submitted experiment intervals.'''
        return self._data['intervals']

    def nodecount(self):
        '''Returns the nodecount for the submitted experiment.'''
        return self._data['nodecount']

    def message(self):
        '''Returns the message following the submission.'''
        return self._data['message']

    def __repr__(self):
        return "<SubmissionReport message=%r >" % self.message()

    def __str__(self):
        return "SubmissionReport: %s >" % self.message()


class JournalEntry:
    ''' 
    Class that models jounral quota information.
    '''

    def __init__(self, data):
        self._data = data

    def value(self):
        '''
       Returns the quota value in bytes or seconds.

       :returns: int
       '''
        return self._data['new_value']

    def ownerid(self):
        '''Returns the ID of the owner

       :returns: int
       '''
        return self._data['ownerid']

    def quota(self):
        '''Returns the category of quota.

       :returns: string -- Values can be ``quota_time``, ``quota_data`` or ``quota_storage``
       '''
        return self._data['quota']

    def reason(self):
        '''Returns the reason for the quota's latest value 

       :returns: string
       '''
        return self._data['reason']

    def timestamp(self):
        '''Returns the timestamp at which the quota data was available

       :returns: int
       '''
        return self._data['timestamp']

    def __repr__(self):
        return "<JournalEntry quota=%r reason=%r timestamp=%r>" % (
            self.value(), self.reason(), self.timestamp())

    def __str__(self):
        t = datetime.datetime.fromtimestamp(self.timestamp())
        if 'time' in self.quota():
            return "%s : Remaining time is %s hours." % (
                t.strftime('%Y-%m-%d'), str("%.2f" % (self.value() / 3600)))
        if 'storage' in self.quota():
            return "%s : Remaining storage quota is %s GB." % (
                t.strftime('%Y-%m-%d'), str("%.2f" % (self.value() /
                                                      (1024 * 1024 * 1024))))
        if 'data' in self.quota():
            return "%s : Remaining data quota is %s GB." % (
                t.strftime('%Y-%m-%d'), str("%.2f" % (self.value() /
                                                      (1024 * 1024 * 1024))))


class Node:
    ''' 
    Class that models nodes.
    '''

    def __init__(self, data):
        self._data = data

    def heartbeat(self):
        '''Returns timestamp of when the node was last seen.

       :returns: int
       '''
        return self._data['heartbeat']

    def hostname(self):
        '''Returns the node hostame.

       :returns: string
       '''
        return self._data['hostname']

    def id(self):
        '''Returns the node id.

       :returns: int
       '''
        return self._data['id']

    def model(self):
        '''Returns the APU board model of the node.

       :returns: string
       '''
        return self._data['model']

    def project(self):
        '''Returns the designated node project.

       :returns: string
       '''
        return self._data['project']

    def site(self):
        '''Returns the designated node site.

       :returns: string
       '''
        return self._data['site']

    def status(self):
        '''Returns the node status.

       :returns: string
       '''
        return self._data['status']

    def nodetype(self):
        '''Returns the node type.

       :returns: string
       '''
        if 'type' in self._data.keys():
            return self._data['type']
        else:
            return 'undefined'

    def __repr__(self):
        return "<Node id=%r status=%r type=%r >" % (self.id(), self.status(),
                                                    self.nodetype())

    def __str__(self):
        return "Node ID=%s Status=%s Type=%s >" % (
            str(self.id()), self.status(), self.nodetype())


class Schedule:
    ''' 
    Class that models schedules.
    '''

    def __init__(self, data):
        self._data = data

    def id(self):
        '''Returns the schedule id.

       :returns: int
       '''
        return self._data['id']

    def nodeid(self):
        '''Returns the node id.

       :returns: int
       '''
        return self._data['nodeid']

    def start(self):
        '''Returns the schedule start.

       :returns: int -- The schedule start in UNIX timestamp format
       '''
        return self._data['start']

    def stop(self):
        '''Returns the schedule stiop.

       :returns: int -- The schedule stop in UNIX timestamp format
       '''
        return self._data['stop']

    def status(self):
        '''Returns the schedule status.

       :returns: string
       '''
        return self._data['status']

    def __repr__(self):
        return "<Schedule id=%r nodeid=%r >" % (self.id(), self.nodeid())

    def __str__(self):
        return "Schedule ID=%s Node ID=%s >" % (str(self.id()),
                                                str(self.nodeid()))
