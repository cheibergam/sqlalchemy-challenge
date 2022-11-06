import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///./Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Query_date to consider 12 months from the last entry in the database
query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)


#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"<b>Available Routes:</b><br>"
        f"<ul>"
        f"<li><a href='/api/v1.0/precipitation'>/api/v1.0/precipitation</a>"
        f"<li><a href='/api/v1.0/stations'>/api/v1.0/stations</a>"
        f"<li><a href='/api/v1.0/tobs'>/api/v1.0/tobs</a>"
        f"<li>/api/v1.0/&LT;start&GT;"
        f"<li>/api/v1.0/&LT;start&GT;/&LT;end&GT;"
        f"</ul>"
    )

#################################################
# /api/v1.0/precipitation Route
#################################################

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list of precipitation data including the date, prcp of each precipitation"""

    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Query all precipitation
    # Perform a query to retrieve the date and precipitation scores
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= query_date).\
        order_by(Measurement.date.desc()).all()

    # Closing the session
    session.close()

    # Create a dictionary from the row data and append to a list of all_precipitation
    all_precipitation = []
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp
        all_precipitation.append(precipitation_dict)
        
    return jsonify(all_precipitation)


#################################################
# /api/v1.0/precipitation Route
#################################################

@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations"""

    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Query all stations
    results = session.query(Station.id, Station.station).all()

    # Closing the session
    session.close()

    # Create a dictionary from the row data and append to a list of all_station
    all_station = []
    for date, prcp in results:
        station_dict = {}
        station_dict["id"] = date
        station_dict["station"] = prcp
        all_station.append(station_dict)
        
    return jsonify(all_station)



#################################################
# /api/v1.0/tobs Route
#################################################

@app.route("/api/v1.0/tobs")
def tobs():
    """Return a list with the dates and temperature observations of the most-active station for the previous year of data."""

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query to find the most active stations (i.e. what stations have the most rows?)
    # List the stations and the counts in descending order.
    station_list = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    
    # Answer the following question: which station id has the greatest number of observations?
    # The most active station
    most_active_station = station_list[0][0]

    # Using the most active station id from the previous query, calculate the lowest temperature.
    results = session.query(Measurement.station, Measurement.date, Measurement.tobs).\
        filter(Measurement.station==most_active_station, Measurement.date >= query_date).all()
        
    # Closing the session
    session.close()

    # Create a dictionary from the row data and append to a list of all_tobs from the most active station in the last 12 months
    all_tobs = []
    for station, date, tobs in results:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["station"] = station
        tobs_dict["tobs"] = tobs
        all_tobs.append(tobs_dict)
        
    return jsonify(all_tobs)

#################################################
# /api/v1.0/<date> Route
#################################################

@app.route("/api/v1.0/<date>")
def specific_date(date):
    """Return the minimum temperature, the average temperature, and the maximum temperature for a specified start date range"""

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query minimum, maverage and maximum temperature for a specific start date range
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= date).all()
    
    # Closing the session
    session.close()
   
    # Create a dictionary from the row data and append to a list of temperatures (minimum, average and maximum)
    all_temperature = []
    for tmin, tavg, tmax in results:
        temperature_dict = {}
        temperature_dict["tmin"] = tmin
        temperature_dict["tavg"] = tavg
        temperature_dict["tmax"] = tmax
        all_temperature.append(temperature_dict)
        
    return jsonify(all_temperature)  
    
#################################################
# /api/v1.0/<start>/<end> Route
#################################################

@app.route("/api/v1.0/<start>/<end>")
def interval_date(start, end):
    """Return the minimum temperature, the average temperature, and the maximum temperature for a specified interval of start-end date range"""

    # Create our session (link) from Python to the DB
    session = Session(engine)
        
    # Query minimum, maverage and maximum temperature for a specified interval of start-end date range
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).\
            filter(Measurement.date <= end).all()
    
    # Closing the session
    session.close()           
   
    
    # Create a dictionary from the row data and append to a list of temperatures (minimum, average and maximum)
    all_temperature = []
    for tmin, tavg, tmax in results:
        temperature_dict = {}
        temperature_dict["tmin"] = tmin
        temperature_dict["tavg"] = tavg
        temperature_dict["tmax"] = tmax
        all_temperature.append(temperature_dict)
        
    return jsonify(all_temperature)  
      
  
if __name__ == '__main__':
    app.run(debug=True)