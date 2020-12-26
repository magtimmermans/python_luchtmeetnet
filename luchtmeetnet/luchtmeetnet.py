"""Luchtmeetnet library to get parsed Airquality data from luchtmeetnet.nl."""
import json
import logging
from datetime import datetime
from math import cos, asin, sqrt

import requests

from luchtmeetnet.constants import (
    SUCCESS,
    MESSAGE,
    CONTENT
)

from luchtmeetnet.urls import json_stations_url, json_station_data_url, json_station_lki_data

log = logging.getLogger(__name__)


class LuchtmeetNet:
    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude
        self.location = {'latitude': latitude, 'longitude': longitude}

    def get_station_measurement(self, station):
        data = {}
        result = self.__get_station_lki_data(station)
        if result[SUCCESS]:
            try:
                content = result[CONTENT]
                json_content = json.loads(content)
                measurements = json_content['data']
                if len(measurements) > 0:
                    data = {
                        'LKI' : measurements[0]['value'],
                        'timestamp' : measurements[0]['timestamp_measured']
                    }
            except json.JSONDecodeError as err:
                # result[MESSAGE] = "Unable to parse content as json."
                log.error("Unable to parse content as json. %s", err)
        return data

    def __get_station_lki_data(self, number):
        log.info('Getting LKI from station %s' % number)
        result = {SUCCESS: False, MESSAGE: None}
        try:
            url = json_station_lki_data(number)
            r = requests.get(url)
            if (r.status_code == 200):
                result[SUCCESS] = True
                result[CONTENT] = r.text
            else:
                result[MESSAGE] = "Error retrieving stations: %d." % (r.status_code)
            return result
        except requests.RequestException as rre:
            result[MESSAGE] = 'Error retrieving stations data. %s' % rre
            log.error(result[MESSAGE])

        return result    



    def get_nearest_station(self):
        log.info("Finding nearest station")
        stations = self.__get_stations()
        return self.__closest(stations,self.location)



    def __get_stations(self):
        stations = []
        result = self.__get_station_page(1)
        if result[SUCCESS]:
            try:
                content = result[CONTENT]
                json_content = json.loads(content)
                for page in json_content['pagination']['page_list']:
                    res = self.__get_station_page(page)
                    if res[SUCCESS]:
                        json_data = json.loads(res[CONTENT])
                        for station in json_data['data']:
                            station_result = self.__get_station_data(station['number'])
                            if station_result[SUCCESS]:
                                station_data = json.loads(station_result[CONTENT])
                                element = {'number' : station['number'],
                                           'longitude' : station_data['data']['geometry']['coordinates'][0],
                                           'latitude' :  station_data['data']['geometry']['coordinates'][1],
                                           'location' : station_data['data']['location']
                                }                              
                                stations.append(element)
                                
            except json.JSONDecodeError as err:
                # result[MESSAGE] = "Unable to parse content as json."
                log.error("Unable to parse content as json. %s", err)
        return stations

    def __get_station_page(self,page):
        log.info('Getting station Data')
        result = {SUCCESS: False, MESSAGE: None}
        try:
            r = requests.get(json_stations_url(page))
            if (r.status_code == 200):
                result[SUCCESS] = True
                result[CONTENT] = r.text
            else:
                result[MESSAGE] = "Error retrieving stations: %d." % (r.status_code)
            return result
        except requests.RequestException as rre:
            result[MESSAGE] = 'Error retrieving stations data. %s' % rre
            log.error(result[MESSAGE])

        return result    


    def __get_station_data(self,number):
        log.info('Getting station Data')
        result = {SUCCESS: False, MESSAGE: None}
        try:
            r = requests.get(json_station_data_url(number))
            if (r.status_code == 200):
                result[SUCCESS] = True
                result[CONTENT] = r.text
            else:
                result[MESSAGE] = "Error retrieving stations: %d." % (r.status_code)
            return result
        except requests.RequestException as rre:
            result[MESSAGE] = 'Error retrieving stations data. %s' % rre
            log.error(result[MESSAGE])

        return result    

    def __distance(self, lat1, lon1, lat2, lon2):
        p = 0.017453292519943295
        a = 0.5 - cos((lat2-lat1)*p)/2 + cos(lat1*p)*cos(lat2*p) * (1-cos((lon2-lon1)*p)) / 2
        distance = 12742 * asin(sqrt(a))
        return distance

    def __closest(self, data, v):
        return min(data, key=lambda p: self.__distance(v['latitude'],v['longitude'],p['latitude'],p['longitude']))
