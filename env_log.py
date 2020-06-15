#!/usr/bin/env python

'''

FILE NAME
env_log.py

1. WHAT IT DOES
Takes a reading from a DHT sensor and records the values in an SQLite3 database using a Raspberry Pi.
 
2. REQUIRES
* Any Raspberry Pi
* A DHT sensor
* A 10kOhm resistor
* Jumper wires

3. ORIGINAL WORK
Raspberry Full stack 2018, Peter Dalmaris

4. HARDWARE
D17: Data pin for sensor

5. SOFTWARE
Command line terminal
Simple text editor
Libraries:
import sqlite3
import sys
import Adafruit_DHT

6. WARNING!
None

7. CREATED 

8. TYPICAL OUTPUT
No text output. Two new records are inserted in the database when the script is executed

 // 9. COMMENTS
--

 // 10. END

'''



import sqlite3
import sys
import Adafruit_DHT
import board, busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

def log_values(sensor_id, temp, hum, ph):
        conn=sqlite3.connect('/var/www/lab_app/lab_app.db')  #It is important to provide an
                                                             #absolute path to the database
                                                             #file, otherwise Cron won't be
                                                             #able to find it!
        # For the time-related code (record timestamps and time-date calculations) to work 
        # correctly, it is important to ensure that your Raspberry Pi is set to UTC.
        # This is done by default!
        # In general, servers are assumed to be in UTC.
        curs=conn.cursor()
        curs.execute("""INSERT INTO temperatures values(datetime(CURRENT_TIMESTAMP, 'localtime'), (?), (?))""", (sensor_id,temp))
        curs.execute("""INSERT INTO humidities values(datetime(CURRENT_TIMESTAMP, 'localtime'), (?), (?))""", (sensor_id,hum))
        curs.execute("""INSERT INTO ph values(datetime(CURRENT_TIMESTAMP, 'localtime'), (?), (?))""", (sensor_id,ph))
        conn.commit()
        conn.close()

i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
chan = AnalogIn(ads, ADS.P0)
phAdj = 21.3295
ph = -5.74 * chan.voltage + phAdj

humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, 17)
# If you don't have a sensor but still wish to run this program, comment out all the 
# sensor related lines, and uncomment the following lines (these will produce random
# numbers for the temperature and humidity variables):
# import random
# humidity = random.randint(1,100)
# temperature = random.randint(10,30)
if humidity is not None and temperature is not None and ph is not None:
        log_values("1", temperature, humidity, ph)      
else:
        log_values("1", -999, -999, -999)
