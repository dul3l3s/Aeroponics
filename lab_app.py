'''
FILE NAME
lab_app.py
Version 1

1. WHAT IT DOES
Implements the first version of the project's Flask application.
This version contains a single page that reports current temperature and humidity.
 
2. REQUIRES
* Any Raspberry Pi

3. ORIGINAL WORK
Raspberry Full Stack 2018, Peter Dalmaris

4. HARDWARE
* Any Raspberry Pi
* DHT11 or 22
* 10KOhm resistor
* Breadboard
* Wires

5. SOFTWARE
Command line terminal
Simple text editor
Libraries:
from flask import Flask, request, render_template

6. WARNING!
None

7. CREATED 

8. TYPICAL OUTPUT
A simple web page served by this flask application in the user's browser.
The page contains the current temperature and humidity.

 // 9. COMMENTS
--
 // 10. END
'''

from flask import Flask, request, render_template
import time
import datetime
import sys
import Adafruit_DHT
import sqlite3
import board, busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

app = Flask(__name__)
app.debug = True # Make this False if you are no longer debugging

@app.route("/ph")
def getPh():
    i2c = busio.I2C(board.SCL, board.SDA)
    ads = ADS.ADS1115(i2c)
    chan = AnalogIn(ads, ADS.P0)
    phAdj = 21.3295
    ph = -5.74 * chan.voltage + phAdj

    if ph is not None:
        return render_template("ph.html", ph=ph)
    else:
        return render_template("no_sensor.html")

@app.route("/lab_temp")
def lab_temp():
	humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, 17)
	if humidity is not None and temperature is not None:
		return render_template("lab_temp.html",temp=temperature,hum=humidity)
	else:
		return render_template("no_sensor.html")

@app.route("/lab_env_db", methods=['GET'])
def lab_env_db():
        temperatures, humidities, ph, from_date_str, to_date_str = get_records()    
        return render_template("lab_env_db.html",   temp        = temperatures,
                                                    hum         = humidities,
                                                    ph          = ph,
                                                    from_date   = from_date_str,
                                                    to_date     = to_date_str,
                                                    temp_items  = len(temperatures),
                                                    hum_items   = len(humidities))

def get_records():
        from_date_str   = request.args.get('from', time.strftime("%Y-%m-%d %H:%M")) 
        to_date_str     = request.args.get('to', time.strftime("%Y-%m-%d %H:%M"))
        range_h_form    = request.args.get('range_h', '');

        range_h_int     = "nan"

        try:
            range_h_int     = int(range_h_form)
        except:
            print("range_h_form not a number")

        if not validate_date(from_date_str):
            from_date_str   = time.strftime("%Y-%m-%d 00:00")
        if not validate_date(to_date_str):
            to_date_str     = time.strftime("%Y-%m-%d %H:%M")

        if isinstance(range_h_int, int):
            time_now        = datetime.datetime.now()
            time_from       = time_now - datetime.timedelta(hours = range_h_int)
            time_to         = time_now
            from_date_str   = time_from.strftime("%Y-%m-%d %H:%M")
            to_date_str     = time_to.strftime("%Y-%m-%d %H:%M")

        conn = sqlite3.connect('/var/www/lab_app/lab_app.db')
        curs = conn.cursor()
        curs.execute("SELECT * FROM temperatures WHERE rDatetime BETWEEN ? AND ?",(from_date_str, to_date_str))
        temperatures = curs.fetchall()
        curs.execute("SELECT * FROM humidities WHERE rDatetime BETWEEN ? AND ?", (from_date_str, to_date_str))
        humidities = curs.fetchall()
        curs.execute("SELECT * FROM ph WHERE rDatetime BETWEEN ? and ?", (from_date_str, to_date_str))
        ph = curs.fetchall()
        conn.close()
        return [temperatures, humidities, ph, from_date_str, to_date_str]

def validate_date(d):
    try:
        datetime.datetime.strptime(d, '%Y-%m-%d %H:%M')
        return True
    except ValueError:
        return False

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
