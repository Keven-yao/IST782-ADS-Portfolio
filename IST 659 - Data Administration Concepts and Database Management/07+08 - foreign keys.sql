-- this script will add all of the foreign keys to the tables and should be run last

if not exists(select * from sys.databases where name='COD')
	create database M003
GO

use COD

GO

-- DOWN

if exists(select * from INFORMATION_SCHEMA.TABLE_CONSTRAINTS
where CONSTRAINT_NAME='fk_creators_data_date')
    alter table students drop constraint fk_creators_data_date

if exists(select * from INFORMATION_SCHEMA.TABLE_CONSTRAINTS
where CONSTRAINT_NAME='fk_ratings_data_date')
    alter table students drop constraint fk_ratings_data_date

if exists(select * from INFORMATION_SCHEMA.TABLE_CONSTRAINTS
where CONSTRAINT_NAME='fk_precipitation_ratings_rating_date')
    alter table students drop constraint fk_precipitation_ratings_rating_date

if exists(select * from INFORMATION_SCHEMA.TABLE_CONSTRAINTS
where CONSTRAINT_NAME='fk_precipitation_ratings_rating_date')
    alter table students drop constraint fk_precipitation_ratings_rating_date

if exists(select * from INFORMATION_SCHEMA.TABLE_CONSTRAINTS
where CONSTRAINT_NAME='fk_ratings_derived_data_date')
    alter table students drop constraint fk_ratings_derived_data_date

if exists(select * from INFORMATION_SCHEMA.TABLE_CONSTRAINTS
where CONSTRAINT_NAME='fk_humidity_ratings_rating_date')
    alter table students drop constraint fk_humidity_ratings_rating_date

if exists(select * from INFORMATION_SCHEMA.TABLE_CONSTRAINTS
where CONSTRAINT_NAME='fk_humidity_ratings_rating_date')
    alter table students drop constraint fk_humidity_ratings_rating_date

-- UP MetaData

alter table creators 
    add constraint fk_creators_data_date foreign key (data_date) 
	references data(date)

alter table ratings 
    add constraint fk_ratings_data_date foreign key (data_date) 
	references data(date)

alter table precipitation_ratings 
    add constraint fk_precipitation_ratings_rating_date foreign key (ratings_rating_date) 
	references ratings(rating_date)

alter table seasons
    add constraint fk_seasons_ratings_rating_date foreign key (ratings_rating_date) 
	references ratings(rating_date)

alter table ratings
    add constraint fk_ratings_derived_data_date foreign key (derived_data_date) 
	references derived_data(date)

alter table humidity_ratings
    add constraint fk_humidity_ratings_rating_date foreign key (ratings_rating_date) 
	references ratings(rating_date)

alter table temp_ratings
    add constraint fk_temp_ratings_rating_date foreign key (ratings_rating_date) 
	references ratings(rating_date)


-- UP Data



-- Verify






















