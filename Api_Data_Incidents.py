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
        if event_city != "*":
            df = df.loc[df["Event City"]==event_city,['AIDS Report Number','Local Event Date','Event City','Event State','Event Airport','Aircraft Damage','Flight Phase','Aircraft Make','Aircraft Model']]
        else:
            df = df[['AIDS Report Number','Local Event Date','Event City','Event State','Event Airport','Aircraft Damage','Flight Phase','Aircraft Make','Aircraft Model']]
        if len(df)>0:
            if aircraft_damage != '*':
                df = df.loc[df["Aircraft Damage"]==aircraft_damage]
            else:
                df = df
            if len(df)> 0:
                if flight_phase != "*":
                    df = df.loc[df["Flight Phase"]==flight_phase]
                else:
                    df = df
                if len(df)>0:
                    if aircraft_make != "*":
                        df = df.loc[df["Aircraft Make"]==aircraft_make]
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

