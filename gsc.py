#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This code is changed from
# https://github.com/google/google-api-python-client/blob/0eaa280ba12a28fac16ff72e9ffaafc4016ab901/samples/searchconsole/search_analytics_api_sample.py
#
# outh2client
# https://github.com/google/oauth2client
# quick start
# https://developers.google.com/webmaster-tools/v3/quickstart/quickstart-python#step_3_set_up_the_sample

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import generators
from __future__ import division

import os
import httplib2
import datetime
import pandas as pd
from oauth2client import client
from oauth2client import tools
from oauth2client import file
from googleapiclient import discovery


def execute_request(service, property_uri, request):
    """Executes a searchAnalytics.query request.

    Args:
      service: The webmasters service to use when executing the query.
      property_uri: The site or app URI to request data for.
      request: The request to be executed.

    Returns:
      An array of response rows.
    """
    res = service.searchanalytics().query(
        siteUrl=property_uri, body=request).execute()
    res_df = pd.DataFrame.from_dict(res['rows'])
    print(res_df)
    return res_df


# exec
client_secrets = os.path.join(os.path.dirname(__file__), 'client_secrets.json')

flow = client.flow_from_clientsecrets(client_secrets,
                                      scope='https://www.googleapis.com/auth/webmasters.readonly',
                                      message=tools.message_if_missing(client_secrets))

storage = file.Storage('credentials.dat')
credentials = storage.get()  # type: client.OAuth2Credentials
if credentials is None or credentials.invalid:
    credentials = tools.run_flow(flow, storage)

# Create an httplib2.Http object and authorize it with our credentials
http = credentials.authorize(http=httplib2.Http())
service = discovery.build('webmasters', 'v3', http=http)
site_list = service.sites().list().execute()
verified_sites_urls = [s['siteUrl'] for s in site_list['siteEntry'] if s['permissionLevel'] != 'siteUnverifiedUser']

print(verified_sites_urls)

start_date = (datetime.date.today() - datetime.timedelta(weeks=4)).strftime('%Y-%m-%d')
end_date = datetime.date.today().strftime('%Y-%m-%d')
property_uri = verified_sites_urls[0]

# First run a query to learn which dates we have data for. You should always
# check which days in a date range have data before running your main query.
# This query shows data for the entire range, grouped and sorted by day,
# descending; any days without data will be missing from the results.
request = {
    'startDate': start_date,
    'endDate': end_date,
    'dimensions': ['date']
}
res = execute_request(service, property_uri, request)


# Get totals for the date range.
request = {
    'startDate': start_date,
    'endDate': end_date
}
print('###  date range')
res = execute_request(service, property_uri, request)


# Get top 10 queries for the date range, sorted by click count, descending.
request = {
    'startDate': start_date,
    'endDate': end_date,
    'dimensions': ['query'],
    'rowLimit': 10
}
print('###  top10 queries')
res = execute_request(service, property_uri, request)


# Get top 11-20 mobile queries for the date range, sorted by click count, descending.
request = {
    'startDate': start_date,
    'endDate': end_date,
    'dimensions': ['query'],
    'dimensionFilterGroups': [{
        'filters': [{
            'dimension': 'device',
            'expression': 'mobile'
        }]
    }],
    'rowLimit': 10,
    'startRow': 10
}
print('###  11-20 mobile queries')
res = execute_request(service, property_uri, request)


# Get top 10 pages for the date range, sorted by click count, descending.
request = {
    'startDate': start_date,
    'endDate': end_date,
    'dimensions': ['page'],
    'rowLimit': 10
}
print('###  top10 pages')
res = execute_request(service, property_uri, request)


# Get the top 10 queries in India, sorted by click count, descending.
request = {
    'startDate': start_date,
    'endDate': end_date,
    'dimensions': ['query'],
    'dimensionFilterGroups': [{
        'filters': [{
            'dimension': 'country',
            'expression': 'jpn'
        }]
    }],
    'rowLimit': 10
}
print('###  top10 queries in Japan')
res = execute_request(service, property_uri, request)


from bokeh.charts import Scatter, output_file, show
# from bokeh.io import output_notebook
output_file("scatter.html")
scatter = Scatter(res, x='impressions', y='clicks', title='bokeh test', y_mapper_type='log', x_mapper_type='log')
show(scatter)


# Group by both country and device.
request = {
    'startDate': start_date,
    'endDate': end_date,
    'dimensions': ['country', 'device'],
    'rowLimit': 10
}
print('###  group by country and device')
res = execute_request(service, property_uri, request)



