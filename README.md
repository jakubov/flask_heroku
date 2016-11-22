Loadsmart coding challenge
==========================

api endpoint:



Database:
postgreSQL hosted on Heroku

CREATE TABLE weather_requests (
  id serial not null,
  zip_code varchar(10),
  location varchar(100),
  temperature smallint,
  created_at timestamp default current_timestamp
);