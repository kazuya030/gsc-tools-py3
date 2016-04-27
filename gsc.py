#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This code is changed from
# https://github.com/google/google-api-python-client/blob/0eaa280ba12a28fac16ff72e9ffaafc4016ab901/samples/searchconsole/search_analytics_api_sample.py

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import generators
from __future__ import division


import sys
import os
import httplib2
import datetime
from oauth2client import client
from oauth2client import tools
from oauth2client import file
from googleapiclient import discovery

def main():
  name = 'webmasters'

  client_secrets = os.path.join(os.path.dirname(__file__), 'client_secrets.json')

  flow = client.flow_from_clientsecrets(client_secrets,
      scope='https://www.googleapis.com/auth/webmasters.readonly',
      message=tools.message_if_missing(client_secrets))

  storage = file.Storage(name + '.dat')
  credentials = storage.get()
  if credentials is None or credentials.invalid:
    credentials = tools.run_flow(flow, storage)

  # Create an httplib2.Http object and authorize it with our credentials
  http = credentials.authorize(http = httplib2.Http())
  service = discovery.build(name, 'v3', http=http)
  site_list = service.sites().list().execute()
  verified_sites_urls = [s['siteUrl'] for s in site_list['siteEntry'] if s['permissionLevel'] != 'siteUnverifiedUser']

  print(verified_sites_urls)

  start_date = (datetime.date.today()-datetime.timedelta(weeks=4)).strftime('%Y-%m-%d')
  end_date =  datetime.date.today().strftime('%Y-%m-%d')
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
  response = execute_request(service, property_uri, request)
  print_table(response, 'Available dates')

  # Get totals for the date range.
  request = {
      'startDate': start_date,
      'endDate': end_date
  }
  response = execute_request(service, property_uri, request)
  print_table(response, 'Totals')

  # Get top 10 queries for the date range, sorted by click count, descending.
  request = {
      'startDate': start_date,
      'endDate': end_date,
      'dimensions': ['query'],
      'rowLimit': 10
  }
  response = execute_request(service, property_uri, request)
  print_table(response, 'Top Queries')

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
  response = execute_request(service, property_uri, request)
  print_table(response, 'Top 11-20 Mobile Queries')

  # Get top 10 pages for the date range, sorted by click count, descending.
  request = {
      'startDate': start_date,
      'endDate': end_date,
      'dimensions': ['page'],
      'rowLimit': 10
  }
  response = execute_request(service, property_uri, request)
  print_table(response, 'Top Pages')

  # Get the top 10 queries in India, sorted by click count, descending.
  request = {
      'startDate': start_date,
      'endDate': end_date,
      'dimensions': ['query'],
      'dimensionFilterGroups': [{
          'filters': [{
              'dimension': 'country',
              'expression': 'ind'
          }]
      }],
      'rowLimit': 10
  }
  response = execute_request(service, property_uri, request)
  print_table(response, 'Top queries in India')

  # Group by both country and device.
  request = {
      'startDate': start_date,
      'endDate': end_date,
      'dimensions': ['country', 'device'],
      'rowLimit': 10
  }
  response = execute_request(service, property_uri, request)
  print_table(response, 'Group by country and device')


def execute_request(service, property_uri, request):
  """Executes a searchAnalytics.query request.

  Args:
    service: The webmasters service to use when executing the query.
    property_uri: The site or app URI to request data for.
    request: The request to be executed.

  Returns:
    An array of response rows.
  """
  return service.searchanalytics().query(
      siteUrl=property_uri, body=request).execute()


def print_table(response, title):
  """Prints out a response table.

  Each row contains key(s), clicks, impressions, CTR, and average position.

  Args:
    response: The server response to be printed as a table.
    title: The title of the table.
  """
  print(title + ':')

  if 'rows' not in response:
    print('Empty response')
    return

  rows = response['rows']
  row_format = '{:<20}' + '{:>20}' * 4
  print(row_format.format('Keys', 'Clicks', 'Impressions', 'CTR', 'Position'))
  for row in rows:
    keys = ''
    # Keys are returned only if one or more dimensions are requested.
    if 'keys' in row:
      keys = ','.join(row['keys'])
    #print(row_format.format(
    #    keys, row['clicks'], row['impressions'], row['ctr'], row['position']))
    #  print(row['keys'])
    print(row_format.format(keys, row['clicks'], row['impressions'], row['ctr'], row['position']))


if __name__ == '__main__':
  print(sys.version)
  main()
