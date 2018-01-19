drop table if exists cards;
drop table if exists atms;
create table cards (account_name text not null unique, card_id text not null unique, balance integer, primary key (account_name, card_id));
create table atms (atm_id text primary key, num_bills integer);
insert into cards (account_name, card_id, balance) values ('test1', '50000000-0000-0000-0000-000000000000', 10);
insert into atms (atm_id, num_bills) values ('40000000-0000-0000-0000-000000000000', 128 );
