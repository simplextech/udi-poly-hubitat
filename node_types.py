""" Node classes used by the Hue Node Server. """

import polyinterface
import requests

LOGGER = polyinterface.LOGGER


class HubitatBase(polyinterface.Node):
    """ Base class for lights and groups """
    def __init__(self, controller, primary, address, name):
        super().__init__(controller, primary, address, name)
        self.name = name
        self.address = address
        # self.st = None
        self.maker_uri = controller.polyConfig['customParams']['maker_uri']

    """ Basic On/Off controls """
    def hubitatCtl(self, command):
        h_cmd = None
        cmd = command.get('cmd')
        device_id = command.get('address')
        _raw_uri = self.maker_uri.split('?')
        _raw_http = _raw_uri[0].replace('all', device_id)

        print('debug------------------')

        print(self.maker_uri)
        print(self.name)
        print(cmd)
        print(device_id)

        if cmd in ['DON', 'DFON']:
            h_cmd = 'on'
            cmd_uri = _raw_http + '/' + h_cmd + '?' + _raw_uri[1]
            # val = command.get('value')
            print(cmd_uri)

        if cmd in ['DOF', 'DFOF']:
            h_cmd = 'off'
            cmd_uri = _raw_http + '/' + h_cmd + '?' + _raw_uri[1]
            # val = command.get('value')
            print(cmd_uri)

        # if cmd == 'DON':
        #
        #     for k in command.keys():
        #         print('Key: ' + k)
        #

        r = requests.get(cmd_uri)
        print(r.status_code)

        if h_cmd == 'on':
            r = requests.get(cmd_uri)
            if r.status_code == 200:
                self.setDriver('ST', 100)
        elif h_cmd == 'off':
            r = requests.get(cmd_uri)
            if r.status_code == 200:
                self.setDriver('ST', 0)

        print('debug------------------')


class VirtualSwitchNode(HubitatBase):

    def __init__(self, controller, primary, address, name):
        super().__init__(controller, primary, address, name)

    # def start(self):
    #     #self.setDriver('ST', 0)
    #     pass

    # def setOn(self, command):
    #     self.setDriver('ST', 100)
    #
    # def setOff(self, command):
    #     self.setDriver('ST', 0)
    #
    # def query(self):
    #     self.reportDrivers()

    drivers = [{'driver': 'ST', 'value': 0, 'uom': 78}]
    id = 'vswitchnode'
    commands = {
        'DON': HubitatBase.hubitatCtl, 'DOF': HubitatBase.hubitatCtl
    }


class ZoozPowerSwitchNode(HubitatBase):

    def __init__(self, controller, primary, address, name):
        super().__init__(controller, primary, address, name)

    # def start(self):
    #     self.setDriver('ST', 0)
    #     pass
    #
    # def setOn(self, command):
    #     self.setDriver('ST', 100)
    #
    # def setOff(self, command):
    #     self.setDriver('ST', 0)
    #
    # def query(self):
    #     self.reportDrivers()

    drivers = [
        {'driver': 'ST', 'value': 0, 'uom': 78},  # Status
        {'driver': 'CC', 'value': 0, 'uom': 1},  # Current - (Amps)
        {'driver': 'CPW', 'value': 0, 'uom': 73},  # Current Power Used (Watts)
        {'driver': 'CV', 'value': 0, 'uom': 72},  # Current Voltage
        {'driver': 'TPW', 'value': 0, 'uom': 33},  # Total Power Used (energy)
        {'driver': 'GV0', 'value': 0, 'uom': 73},  # currentH
        {'driver': 'GV1', 'value': 0, 'uom': 73},  # currentL
        {'driver': 'GV2', 'value': 0, 'uom': 33},  # powerH
        {'driver': 'GV3', 'value': 0, 'uom': 33},  # powerL
        {'driver': 'GV4', 'value': 0, 'uom': 72},  # voltageH
        {'driver': 'GV5', 'value': 0, 'uom': 72},  # voltageL
        {'driver': 'GV6', 'value': 0, 'uom': 45}  # energy duration
    ]
    id = 'zoozpowerswitch'
    commands = {
        'DON': HubitatBase.hubitatCtl, 'DOF': HubitatBase.hubitatCtl
    }


class NYCEMotionSensorNode(polyinterface.Node):

    def __init__(self, controller, primary, address, name):
        super(NYCEMotionSensorNode, self).__init__(controller, primary, address, name)

    # def start(self):
    #     self.setDriver('ST', 0)
    #     pass
    #
    # def setOn(self, command):
    #     self.setDriver('ST', 100)
    #
    # def setOff(self, command):
    #     self.setDriver('ST', 0)
    #
    # def query(self):
    #     self.reportDrivers()

    drivers = [
        {'driver': 'ST', 'value': 0, 'uom': 78},
        {'driver': 'BATLVL', 'value': 0, 'uom': 51},
        {'driver': 'CLITEMP', 'value': 0, 'uom': 17},
        {'driver': 'CLIHUM', 'value': 0, 'uom': 22}
    ]
    id = 'nycemsnode'
    commands = {
        # 'DON': setOn, 'DOF': setOff
    }


class Zooz4n1SensorNode(polyinterface.Node):

    def __init__(self, controller, primary, address, name):
        super(Zooz4n1SensorNode, self).__init__(controller, primary, address, name)

    # def start(self):
    #     self.setDriver('ST', 0)
    #     pass
    #
    # def setOn(self, command):
    #     self.setDriver('ST', 100)
    #
    # def setOff(self, command):
    #     self.setDriver('ST', 0)
    #
    # def query(self):
    #     self.reportDrivers()

    drivers = [
        {'driver': 'ST', 'value': 0, 'uom': 78},
        {'driver': 'BATLVL', 'value': 0, 'uom': 51},
        {'driver': 'CLITEMP', 'value': 0, 'uom': 17},
        {'driver': 'CLIHUM', 'value': 0, 'uom': 22},
        {'driver': 'LUMIN', 'value': 0, 'uom': 36},
        {'driver': 'ALARM', 'value': 0, 'uom': 2}
    ]
    id = 'zooz4n1sensor'
    commands = {
        # 'DON': setOn, 'DOF': setOff
    }


class DomeMotionSensorNode(polyinterface.Node):

    def __init__(self, controller, primary, address, name):
        super(DomeMotionSensorNode, self).__init__(controller, primary, address, name)

    # def start(self):
    #     self.setDriver('ST', 0)
    #     pass
    #
    # def setOn(self, command):
    #     self.setDriver('ST', 100)
    #
    # def setOff(self, command):
    #     self.setDriver('ST', 0)
    #
    # def query(self):
    #     self.reportDrivers()

    drivers = [
        {'driver': 'ST', 'value': 0, 'uom': 78},
        {'driver': 'BATLVL', 'value': 0, 'uom': 51},
        {'driver': 'LUMIN', 'value': 0, 'uom': 36},
    ]
    id = 'domemotionsensor'
    commands = {
        # 'DON': setOn, 'DOF': setOff
    }


class FibaroZW5Node(polyinterface.Node):

    def __init__(self, controller, primary, address, name):
        super(FibaroZW5Node, self).__init__(controller, primary, address, name)

    # def start(self):
    #     self.setDriver('ST', 0)
    #     pass
    #
    # def setOn(self, command):
    #     self.setDriver('ST', 100)
    #
    # def setOff(self, command):
    #     self.setDriver('ST', 0)
    #
    # def query(self):
    #     self.reportDrivers()

    drivers = [
        {'driver': 'ST', 'value': 0, 'uom': 78},
        {'driver': 'BATLVL', 'value': 0, 'uom': 51},
        {'driver': 'CLITEMP', 'value': 0, 'uom': 17},
        {'driver': 'LUMIN', 'value': 0, 'uom': 36},
        {'driver': 'ALARM', 'value': 0, 'uom': 2},
        {'driver': 'SPEED', 'value': 0, 'uom': 2}
    ]
    id = 'fibarozw5node'
    commands = {
        # 'DON': setOn, 'DOF': setOff
    }
