JSON_STATIONS_URL_TEMPLATE = (
   'https://api.luchtmeetnet.nl/open_api/stations?page={page}&order_by=number&organisation_id=' 
)

JSON_STATION_DATA_URL_TEMPLATE = (
    'https://api.luchtmeetnet.nl/open_api/stations/{number}/'
)

JSON_STATION_LKI_DATA_TEMPLATE = (
    'https://api.luchtmeetnet.nl/open_api/lki?station_number={station}&order_by=timestamp_measured&order_direction=desc'
)


def json_stations_url(pagenumber) -> str:
    return JSON_STATIONS_URL_TEMPLATE.format(page=pagenumber)


def json_station_data_url(stationnumber) -> str:
    return JSON_STATION_DATA_URL_TEMPLATE.format(number=stationnumber)

def json_station_lki_data(stationnumber) -> str:
    return JSON_STATION_LKI_DATA_TEMPLATE.format(station=stationnumber)

