Loadsmart coding challenge
==========================

api endpoint:

  GET https://obscure-cove-65098.herokuapp.com/api/temperature/?query=<address>

e.g:

  curl -H "Content-type: application/json" -X GET https://obscure-cove-65098.herokuapp.com/api/temperature/?query=10013
  or
  curl -H "Content-type: application/json" -G -v "https://obscure-cove-65098.herokuapp.com/api/temperature" --data-urlencode "query=39 wooster st new york"

response:

  {"status": "success", "data": {"state": "NY", "city": "New York", "temp":39}}



Database:
postgreSQL hosted on Heroku

CREATE TABLE weather_requests (
  id serial not null,
  zip_code varchar(10),
  location varchar(100),
  temperature smallint,
  created_at timestamp default current_timestamp
);