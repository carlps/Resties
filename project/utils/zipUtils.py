'''
project.utils.zipUtils

Utilities for checking zip code
as well as looking up lat/lng
'''
from os import environ

import requests

from project.models import ZipCode
from project import db


def zipCheck(zipCode):
    '''query db for zip code
       if already in zipCode table, do nothing
       if not, geolocate and insert'''

    # query db for passed zip
    lookup = ZipCode.query.filter_by(zipCode=zipCode).first()
    # if nothing returned
    if lookup is None:
        # geolocateZip returns (zip, lat, lng)
        geo = geolocateZip(zipCode)
        # create new ZipCode object
        new_zip = ZipCode(*geo)
        # add new zip code to db
        db.session.add(new_zip)
        db.session.commit()


def geolocateZip(zipCode):
    '''use google maps API to geocode a zip
       AKA takes a zip and returns tuple of zip,lat,long'''

    # create url for looking up zip
    url = ('https://maps.googleapis.com/maps/api/geocode/'
           'json?address={}&key={}'.
           format(zipCode, environ['GOOGLE_API_RESTIES']))
    # use requests to request data
    request = requests.get(url)
    # ensure valid response
    if request.status_code != 200:
        raise AttributeError('Request returned bad response')
    else:
        # if valid response, return results from json response
        results = request.json()['results']
    # if more than one result, raise error (need to test)
    if len(results) > 1:
        raise AttributeError('Zip search returned more than one result?')

    # if only one respone, pull lat and long out of json
    # response has other info, but this is all we need (for now?)
    lat = results[0]['geometry']['location']['lat']
    lng = results[0]['geometry']['location']['lng']

    return (zipCode, lat, lng)
