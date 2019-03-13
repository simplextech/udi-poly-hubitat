#!/usr/bin/env python3
"""
This is a NodeServer template for Polyglot v2 written in Python2/3
by Einstein.42 (James Milne) milne.james@gmail.com
"""
try:
    import polyinterface
except ImportError:
    import pgc_interface as polyinterface
import sys
import time
import requests
from lomond import WebSocket

# Import all of the supported device node-types.
# Not using a glob '*' import to validate/test node types as introduced for QA/QC
from node_types import VirtualSwitchNode, NYCEMotionSensorNode, Zooz4n1SensorNode, DomeMotionSensorNode, ZoozPowerSwitchNode, FibaroZW5Node

"""
Import the polyglot interface module. This is in pypy so you can just install it
normally. Replace pip with pip3 if you are using python3.

Virtualenv:
pip install polyinterface

Not Virutalenv:
pip install polyinterface --user

*I recommend you ALWAYS develop your NodeServers in virtualenv to maintain
cleanliness, however that isn't required. I do not condone installing pip
modules globally. Use the --user flag, not sudo.
"""

LOGGER = polyinterface.LOGGER
"""
polyinterface has a LOGGER that is created by default and logs to:
logs/debug.log
You can use LOGGER.info, LOGGER.warning, LOGGER.debug, LOGGER.error levels as needed.
"""

class Controller(polyinterface.Controller):
    """
    The Controller Class is the primary node from an ISY perspective. It is a Superclass
    of polyinterface.Node so all methods from polyinterface.Node are available to this
    class as well.

    Class Variables:
    self.nodes: Dictionary of nodes. Includes the Controller node. Keys are the node addresses
    self.name: String name of the node
    self.address: String Address of Node, must be less than 14 characters (ISY limitation)
    self.polyConfig: Full JSON config dictionary received from Polyglot for the controller Node
    self.added: Boolean Confirmed added to ISY as primary node
    self.config: Dictionary, this node's Config

    Class Methods (not including the Node methods):
    start(): Once the NodeServer config is received from Polyglot this method is automatically called.
    addNode(polyinterface.Node, update = False): Adds Node to self.nodes and polyglot/ISY. This is called
        for you on the controller itself. Update = True overwrites the existing Node data.
    updateNode(polyinterface.Node): Overwrites the existing node data here and on Polyglot.
    delNode(address): Deletes a Node from the self.nodes/polyglot and ISY. Address is the Node's Address
    longPoll(): Runs every longPoll seconds (set initially in the server.json or default 10 seconds)
    shortPoll(): Runs every shortPoll seconds (set initially in the server.json or default 30 seconds)
    query(): Queries and reports ALL drivers for ALL nodes to the ISY.
    getDriver('ST'): gets the current value from Polyglot for driver 'ST' returns a STRING, cast as needed
    runForever(): Easy way to run forever without maxing your CPU or doing some silly 'time.sleep' nonsense
                  this joins the underlying queue query thread and just waits for it to terminate
                  which never happens.
    """
    def __init__(self, polyglot):
        """
        Optional.
        Super runs all the parent class necessities. You do NOT have
        to override the __init__ method, but if you do, you MUST call super.
        """
        super(Controller, self).__init__(polyglot)
        self.name = 'Hubitat'
        self.node_list = []

    def start(self):
        """
        Optional.
        Polyglot v2 Interface startup done. Here is where you start your integration.
        This will run, once the NodeServer connects to Polyglot and gets it's config.
        In this example I am calling a discovery method. While this is optional,
        this is where you should start. No need to Super this method, the parent
        version does nothing.
        """
        LOGGER.info('Started Hubitat')
        # Remove all existing notices
        self.removeNoticesAll()
        if self.check_params():
            self.discover()
            self.hubitat_events()

    def shortPoll(self):
        """
        Optional.
        This runs every 10 seconds. You would probably update your nodes either here
        or longPoll. No need to Super this method the parent version does nothing.
        The timer can be overriden in the server.json.
        """
        pass

    def longPoll(self):
        """
        Optional.
        This runs every 30 seconds. You would probably update your nodes either here
        or shortPoll. No need to Super this method the parent version does nothing.
        The timer can be overriden in the server.json.
        """
        pass

    def query(self):
        """
        Optional.
        By default a query to the control node reports the FULL driver set for ALL
        nodes back to ISY. If you override this method you will need to Super or
        issue a reportDrivers() to each node manually.
        """
        for node in self.nodes:
            self.nodes[node].reportDrivers()

    def check_params(self):
        # default_hubitat_uri = 'http://localhost'
        # hubitat_uri = default_hubitat_uri

        default_maker_uri = 'http://<IP_ADDRESS>/apps/api/<APP_ID>/devices/all?access_token=<TOKEN>'
        maker_uri = default_maker_uri

        # if 'hubitat_uri' in self.polyConfig['customParams']:
        #     hubitat_uri = self.polyConfig['customParams']['hubitat_uri']
        #     if hubitat_uri != default_hubitat_uri:
        #         hubitat_st = True
        #     else:
        #         hubitat_st = False
        # else:
        #     LOGGER.error('Hubitat URI is not defined in configuration')
        #     hubitat_st = False

        if 'maker_uri' in self.polyConfig['customParams']:
            maker_uri = self.polyConfig['customParams']['maker_uri']
            if maker_uri != default_maker_uri:
                maker_st = True
            else:
                maker_st = False
        else:
            LOGGER.error('Hubitat Maker API URL is not defined in configuration')
            maker_st = False

        # Make sure they are in the params
        # self.addCustomParam({'hubitat_uri': hubitat_uri})
        self.addCustomParam({'maker_uri': maker_uri})

        if maker_uri == default_maker_uri:
            self.addNotice('Please set proper Hubitat and Maker API URI, and restart this NodeServer', 'HubitatNotice')

        if maker_st:
            return True

    def discover(self, *args, **kwargs):
        """
        Example
        Do discovery here. Does not have to be called discovery. Called from example
        controller start method and from DISCOVER command recieved from ISY as an exmaple.
        """

        r = requests.get(self.polyConfig['customParams']['maker_uri'])
        data = r.json()

        for dev in data:
            LOGGER.info(dev)
            _name = dev['name']
            _label = dev['label']
            _type = dev['type']
            _id = dev['id']

            if dev['type'] == 'Virtual Switch':
                self.addNode(VirtualSwitchNode(self, self.address, _id, _label))
            if dev['type'] == 'NYCE Motion Sensor Series':
                self.addNode(NYCEMotionSensorNode(self, self.address, _id, _label))
            if dev['type'] == 'Zooz 4-in-1 Sensor':
                self.addNode(Zooz4n1SensorNode(self, self.address, _id, _label))
            if dev['type'] == 'Dome Motion Sensor':
                self.addNode(DomeMotionSensorNode(self, self.address, _id, _label))
            if dev['type'] == 'Zooz Power Switch':
                self.addNode(ZoozPowerSwitchNode(self, self.address, _id, _label))
            if dev['type'] == 'Fibaro Motion Sensor ZW5':
                self.addNode(FibaroZW5Node(self, self.address, _id, _label))

        # Build node list
        # self.node_list = []
        for node in self.nodes:
            self.node_list.append(self.nodes[node].address)

    def delete(self):
        """
        Example
        This is sent by Polyglot upon deletion of the NodeServer. If the process is
        co-resident and controlled by Polyglot, it will be terminiated within 5 seconds
        of receiving this message.
        """
        LOGGER.info('Oh God I\'m being deleted. Nooooooooooooooooooooooooooooooooooooooooo.')

    def stop(self):
        LOGGER.debug('NodeServer stopped.')

    def remove_notices_all(self,command):
        LOGGER.info('remove_notices_all:')
        # Remove all existing notices
        self.removeNoticesAll()

    def update_profile(self,command):
        LOGGER.info('update_profile:')
        st = self.poly.installprofile()
        return st

    def hubitat_events(self):
        # hubitat_uri = self.polyConfig['customParams']['hubitat_uri']
        maker_uri = self.polyConfig['customParams']['maker_uri']
        ws_uri = 'ws://' + maker_uri.split('/')[2] + '/eventsocket'

        LOGGER.info(ws_uri)
        LOGGER.info(maker_uri)

        websocket = WebSocket(ws_uri)
        for event in websocket:
            if event.name == "text":
                if event.json['source'] == 'DEVICE':
                    _deviceId = str(event.json['deviceId'])
                    h_value = event.json['value']
                    h_name = event.json['name']

                    print('----Device Info----')
                    print(event.json)
                    print('----Device Info----')

                    if _deviceId in self.node_list:
                        m_node = self.nodes[_deviceId]
                        #print("Hey I own that device!!!")

                        if h_name == 'switch':
                            if h_value == 'on':
                                m_node.setDriver('ST', 100)
                            elif h_value == 'off':
                                m_node.setDriver('ST', 0)
                        elif h_name == 'motion':
                            if h_value == 'active':
                                m_node.setDriver('ST', 100)
                            elif h_value == 'inactive':
                                m_node.setDriver('ST', 0)
                        elif h_name == 'tamper':
                            if h_value == 'detected':
                                m_node.setDriver('ALARM', 1)
                            elif h_value == 'clear':
                                m_node.setDriver('ALARM', 0)
                        elif h_name == 'acceleration':
                            if h_value == 'active':
                                m_node.setDriver('SPEED', 1)
                            elif h_value == 'inactive':
                                m_node.setDriver('SPEED', 0)
                        elif h_name == 'battery':
                            m_node.setDriver('BATLVL', h_value)
                        elif h_name == 'temperature':
                            m_node.setDriver('CLITEMP', h_value)
                        elif h_name == 'humidity':
                            m_node.setDriver('CLIHUM', h_value)
                        elif h_name == 'illuminance':
                            m_node.setDriver('LUMIN', h_value)
                        elif h_name == 'current':
                            m_node.setDriver('CC', h_value)
                        elif h_name == 'currentH':
                            m_node.setDriver('GV0', h_value)
                        elif h_name == 'currentL':
                            m_node.setDriver('GV1', h_value)
                        elif h_name == 'energy':
                            m_node.setDriver('TPW', h_value)
                        elif h_name == 'power':
                            m_node.setDriver('CPW', h_value)
                        elif h_name == 'powerH':
                            m_node.setDriver('GV2', h_value)
                        elif h_name == 'powerL':
                            m_node.setDriver('GV3', h_value)
                        elif h_name == 'voltage':
                            m_node.setDriver('CV', h_value)
                        elif h_name == 'voltageH':
                            m_node.setDriver('GV4', h_value)
                        elif h_name == 'voltageL':
                            m_node.setDriver('GV5', h_value)
                        elif h_name == 'energyDuration':
                            m_node.setDriver('GV6', h_value)
                        else:
                            print('Driver not implemented')

    """
    Optional.
    Since the controller is the parent node in ISY, it will actual show up as a node.
    So it needs to know the drivers and what id it will use. The drivers are
    the defaults in the parent Class, so you don't need them unless you want to add to
    them. The ST and GV1 variables are for reporting status through Polyglot to ISY,
    DO NOT remove them. UOM 2 is boolean.
    """
    id = 'controller'
    commands = {
        'DISCOVER': discover,
        'UPDATE_PROFILE': update_profile,
        'REMOVE_NOTICES_ALL': remove_notices_all
    }
    drivers = [{'driver': 'ST', 'value': 1, 'uom': 2}]


if __name__ == "__main__":
    try:
        polyglot = polyinterface.Interface('Hubitat')
        """
        Instantiates the Interface to Polyglot.
        """
        polyglot.start()
        """
        Starts MQTT and connects to Polyglot.
        """
        control = Controller(polyglot)
        """
        Creates the Controller Node and passes in the Interface
        """
        control.runForever()
        """
        Sits around and does nothing forever, keeping your program running.
        """
    except (KeyboardInterrupt, SystemExit):
        polyglot.stop()
        sys.exit(0)
        """
        Catch SIGTERM or Control-C and exit cleanly.
        """
