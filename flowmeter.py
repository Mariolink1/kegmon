# SPDX-FileCopyrightText: 2019 Anne Barela for Adafruit Industries
#
# SPDX-License-Identifier: MIT
# Modified by Chase Matthews for IST 402

import time
import random
class FlowMeter():
  PINTS_IN_A_LITER = 2.11338
  SECONDS_IN_A_MINUTE = 60
  MS_IN_A_SECOND = 1000.0
  displayFormat = 'metric'
  beverage = 'beer'
  enabled = True
  clicks = 0
  lastClick = 0
  clickDelta = 0
  hertz = 0.0
  flow = 0 # in Liters per second
  thisPour = 0.0 # in Liters
  totalPour = 0.0 # in Liters
  kegSize = 'quarter'
  calibrationFactor = 0.0

  def __init__(self, displayFormat, beverage, size):
    self.displayFormat = displayFormat
    self.beverage = beverage
    self.clicks = 0
    self.lastClick = int(time.time() * FlowMeter.MS_IN_A_SECOND)
    self.clickDelta = 0
    self.hertz = 0.0
    self.flow = 0.0
    self.thisPour = 0.0
    self.totalPour = 0.0
    self.enabled = True
    self.kegSize = size 
    self.calibrationFactor = .22
    

  def update(self, currentTime):
    self.clicks += 1
    # get the time delta
    self.clickDelta = max((currentTime - self.lastClick), 1)
    # calculate the instantaneous speed
    if (self.enabled == True and self.clickDelta < 1000):
      self.hertz = FlowMeter.MS_IN_A_SECOND / self.clickDelta
      self.flow = self.hertz / (FlowMeter.SECONDS_IN_A_MINUTE * 7.5)  # In Liters per second
      instPour = self.flow * (self.clickDelta / FlowMeter.MS_IN_A_SECOND)  
      instPour = self.flow * (self.clickDelta / FlowMeter.MS_IN_A_SECOND) * self.calibrationFactor #Offset added to hopefully correct the calibration on the system 
      self.thisPour += instPour
      self.totalPour += instPour
    # Update the last click
    self.lastClick = currentTime

  def getBeverage(self):
    return self.beverage

  def setBeverage(self, newBev):
    self.beverage = newBev

  def getKeg(self):
    return self.kegSize

  def setKeg(self, newKeg):
      self.kegSize = newKeg.lower()

  def getFormattedClickDelta(self):
     return str(self.clickDelta) + ' ms'
  
  def getFormattedHertz(self):
     return str(round(self.hertz,3)) + ' Hz'
  
  def getFormattedFlow(self):
    if(self.displayFormat == 'metric'):
      return str(round(self.flow,3)) + ' L/s'
    else:
      return str(round(self.flow * FlowMeter.PINTS_IN_A_LITER, 3)) + ' pints/s'

  def setThisPour(self, newPour):
    self.thisPour = float(newPour) 
 
  def getFormattedThisPour(self):
    if(self.displayFormat == 'metric'):
      return str(round(self.thisPour,3)) + ' L'
    else:
      return str(round(self.thisPour * FlowMeter.PINTS_IN_A_LITER, 3)) + ' pints'

  def setTotalPour(self, newTot):
    self.totalPour = float(newTot)

  def getFormattedTotalPour(self):
    if(self.displayFormat == 'metric'):
      return str(round(self.totalPour,3)) + ' L'
    else:
      return str(round(self.totalPour * FlowMeter.PINTS_IN_A_LITER, 3)) + ' pints'

  def getFormattedBeerLeft(self):
    kegVol = 0
    if (self.kegSize == "quarter"):
      kegVol = 29.34
    else:
      kegVol = 19.55
    if(self.displayFormat == 'metric'):
      return str(round((kegVol-self.totalPour),3)) + ' L'
    else:
      return str(round((kegVol-self.totalPour) * FlowMeter.PINTS_IN_A_LITER, 3)) + ' pints'

  def getPercentLeft(self):
    kegVol = 0
    if (self.kegSize == "quarter"):
      kegVol = 29.34
    else:
      kegVol = 19.55
    return(str(round(100*((kegVol-self.totalPour)/kegVol),3)))

  def clear(self):
    self.thisPour = 0
    self.totalPour = 0

  def calibrate(self, gBeer):
    gBeer=float(gBeer)
    if (self.thisPour>0):
    #clean up last pour
      self.totalPour = (self.totalPour-self.thisPour)
    #calculate relative error
      relError = ((self.thisPour-(gBeer/1000.0))/(gBeer/1000.0))
    #undo total pour
      self.thisPour = (self.thisPour/self.calibrationFactor)
    #set new calibration factor
      self.calibrationFactor= (self.calibrationFactor/(1+relError))
    #set new pour data
      self.thisPour = (self.thisPour*self.calibrationFactor)
      self.totalPour = (self.totalPour+self.thisPour)
    else:
      self.calibrationFactor = gBeer
  def getCali(self):
    return str(self.calibrationFactor)      