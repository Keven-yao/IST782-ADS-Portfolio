
if not exists(select * from sys.databases where name='COD')
	create database COD
GO

use COD

GO

-- DOWN

drop table if exists creators


-- UP MetaData


create table creators (
    creator_id int identity not null,
    creator_first_name Varchar (12),
    creator_last_name Varchar (12),
    creator_email Varchar (16),
);


-- UP Data

INSERT INTO creators (creator_first_name, creator_last_name,creator_email)
VALUES

('Sanchit','Tomar', 'satomar@syr.edu'),
('Odbileg', 'Erdenebileg', 'oerdeneb@syr.edu'),
('Yunkai', 'Yao', 'yyao48@syr.edu'),
('Edward', 'Cogan', 'ejcogani@syr.edu');

-- Verify

select * from creators