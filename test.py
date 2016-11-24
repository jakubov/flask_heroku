#!/usr/bin/env python

"""Tests for the LS Weather app"""

import unittest
from app import app

import json
import urllib


class TestApp(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_home_page_works(self):
        rv = self.app.get('https://obscure-cove-65098.herokuapp.com/')
        self.assertTrue(rv.data)
        self.assertEqual(rv.status_code, 200)

    def test_temperature_query_by_zip_code(self):
        rv = self.app.get('https://obscure-cove-65098.herokuapp.com/api/temperature/?query=10013')
        _data = json.loads(rv.data)
        self.assertEqual(_data['status'], 'success')
        self.assertEqual(rv.status_code, 200)

    def test_temperature_query_by_address(self):
        query_str = urllib.quote_plus('39 wooster st new york')
        rv = self.app.get('https://obscure-cove-65098.herokuapp.com/api/temperature/?query=' + query_str)
        _data = json.loads(rv.data)
        self.assertEqual(_data['status'], 'success')
        self.assertEqual(rv.status_code, 200)

    def test_temperature_query_by_address_not_found(self):
        query_str = urllib.quote_plus('39 rooster st zoo york')
        rv = self.app.get('https://obscure-cove-65098.herokuapp.com/api/temperature/?query=' + query_str)
        _data = json.loads(rv.data)
        self.assertEqual(_data['status'], 'failure')
        self.assertEqual(_data['reason'], 'no results found')
        self.assertEqual(rv.status_code, 200)

    def test_temperature_query_by_invalid_address(self):
        query_str = ''
        rv = self.app.get('https://obscure-cove-65098.herokuapp.com/api/temperature/?query=' + query_str)
        _data = json.loads(rv.data)
        self.assertEqual(_data['status'], 'failure')
        self.assertEqual(_data['reason'], 'invalid query')
        self.assertEqual(rv.status_code, 200)

    def test_temperature_query_address_found_multiple_results(self):
        query_str = urllib.quote_plus('wooster st')
        rv = self.app.get('https://obscure-cove-65098.herokuapp.com/api/temperature/?query=' + query_str)
        _data = json.loads(rv.data)
        self.assertEqual(_data['status'], 'failure')
        self.assertEqual(_data['reason'], 'found multiple locations')
        self.assertEqual(rv.status_code, 200)

    def test_app_usage_all_ip_addresses(self):
        rv = self.app.get('https://obscure-cove-65098.herokuapp.com/api/usage/')
        _data = json.loads(rv.data)
        self.assertEqual(_data['status'], 'success')
        self.assertEqual(rv.status_code, 200)

    def test_app_usage_ip_address(self):
        rv = self.app.get('https://obscure-cove-65098.herokuapp.com/api/usage/192.0.2.8')
        _data = json.loads(rv.data)
        self.assertEqual(_data['status'], 'success')
        self.assertEqual(rv.status_code, 200)

    def test_404_page(self):
        rv = self.app.get('/i-am-not-found/')
        self.assertEqual(rv.status_code, 404)


if __name__ == '__main__':
    unittest.main()
