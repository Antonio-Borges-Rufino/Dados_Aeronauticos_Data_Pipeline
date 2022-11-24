#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from flask import Flask, request,jsonify
from flask_restful import Resource, Api
import pandas as pd
import json

app = Flask(__name__)
api = Api(app)

class TodoSimple(Resource):
    def get(self,event_city,aircraft_damage,flight_phase,aircraft_make):
        df = pd.read_csv("/home/hadoop/projetos/Scripts_Data/faa_incidents_data.csv")
        df = df.rename(columns={'AIDS Report Number':'AIDSReportNumber','Local Event Date':'LocalEventDate','Event City':'EventCity','Event State':'EventState','Event Airport':'EventAirport','Aircraft Damage':'AircraftDamage','Flight Phase':'FlightPhase','Aircraft Make':'AircraftMake','Aircraft Model':'AircraftModel'})
        
        if event_city != "*":
            df = df.loc[df["EventCity"]==event_city,['AIDSReportNumber','LocalEventDate','EventCity','EventState','EventAirport','AircraftDamage','FlightPhase','AircraftMake','AircraftModel']]
        else:
            df = df[['AIDSReportNumber','LocalEventDate','EventCity','EventState','EventAirport','AircraftDamage','FlightPhase','AircraftMake','AircraftModel']]
        if len(df)>0:
            if aircraft_damage != '*':
                df = df.loc[df["AircraftDamage"]==aircraft_damage]
            else:
                df = df
            if len(df)> 0:
                if flight_phase != "*":
                    df = df.loc[df["FlightPhase"]==flight_phase]
                else:
                    df = df
                if len(df)>0:
                    if aircraft_make != "*":
                        df = df.loc[df["AircraftMake"]==aircraft_make]
                    else:
                        df = df
                    if len(df)>0:
                        df.fillna("None",inplace=True)
                        df = df.to_dict(orient='records')
                        #df = df.to_dict()
                        return df
                    else:
                        return {"Result":"|||Null"}
                else:
                    return {"Result":"||Null"}
            else:
                return {"Result":"|Null"}  
        else:
            return {"Result":"Null"}

api.add_resource(TodoSimple, '/<string:event_city>/<string:aircraft_damage>/<string:flight_phase>/<string:aircraft_make>')

if __name__ == '__main__':
    app.run(debug=True)

