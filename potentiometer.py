from subprocess import call
import urllib
import xml.etree.ElementTree as ET
import time, math

## serial is not no buon
#import serialDecoder.py as sd

TELNET = "telnet 192.168.2.241 10001"
device = '/dev/cu.usbserial'
time_delay = 0.1
time_step = 0.001


class DataGetter():
  """Abstract class used for getting the voltage from a device"""
  def __init__(self):
    pass
  def get(self):
    pass

class PotentiometerMover():
  """Abstract class used for moving the potentiometer"""
  def __init__(self):
    pass

  def move(self, direction, distance):
    pass


class AD_DataGetter(DataGetter):
  """Class using the AD4ETH A2D converter for measuring the voltage"""
  def __init__(self, url):
    self.url = url

  def get(self):
    data = urllib.urlopen(self.url).read()
    root = ET.fromstring(data)
    inputs = root[0]

    return float(inputs.attrib['val'])

class Serial_DataGetter(DataGetter):
  """Class using the VA18B voltmeter over serial connection"""
  def __init__(self, serialDevice):
    self.serialDevice

  def get(self):
    return float(self.serialDevice.getValue())


class Relay_PotentiometerMover(PotentiometerMover):
  """Class using the Quido relay for moving the potentiometer head"""
  def __init__(self):
    pass

  def _sendCommand(self, relayId, high):
    if relayId > 16 or relayId < 1:
      raise ValueError("Value out of bounds")

    stateLetter = ""
    if high:
      stateLetter = "H"
    else:
      stateLetter = "L"

    stringToSend = "echo '*B1OS" + str(relayId) + stateLetter + "' | " + TELNET
    call(stringToSend, shell=True)

  def move(self, val):
    for i in xrange(abs(val)):
      if val > 0:
        self._sendCommand(2, True)
        self._sendCommand(3, True)
      else:
        self._sendCommand(2, False)
        self._sendCommand(3, False)

      print val
      time.sleep(time_delay/(abs(val)/10.0))
      self._sendCommand(1, True)
      time.sleep(time_step)
      self._sendCommand(1, False)
      time.sleep(time_step)



class Potentiometer():
  def __init__(self, voltageGetter, potentiometerMover, rang=0.05):
    self.vG = voltageGetter
    self.pM = potentiometerMover
    self.rang = rang

  def setValue(self, value):
    while True:
      offset = self._offset(value)
      if abs(offset) < self.rang: # we are in range of the value
        time.sleep(1)
        print "done"
        if abs(self._offset(value)) > self.rang:
          print "final:",self._offset(value)
          continue
        print self._offset(value)
        return


      move = self._movement(offset)
      print "moving", move
      self._move(int(move))  # move the head a little

  def _offset(self, value):
    currentVal = self.getValue()
    offset = currentVal - value
    return offset

  def _movement(self, offset):
    if offset < 0:
      sign = True
    else:
      sign = False

    move = math.ceil((offset*10))

    if sign:
      move *= 1

    return move

  def _move(self, val):
    self.pM.move(val)

  def getValue(self):
    return self.vG.get()


po = Relay_PotentiometerMover()

## Using AD
dataGetter = AD_DataGetter('http://192.168.2.242/data.xml')
va = Potentiometer(dataGetter, po)


print va.getValue()

va.setValue(2)
## Using serial device
#with sd.SerialDevice(device, 1) as s:
#  dataGetter = Serial_DataGetter(s)
#  va = Potentiometer(dataGetter)


