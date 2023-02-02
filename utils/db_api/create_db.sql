CREATE EXTENSION if not exists pgcrypto;

create table if not exists users
(
    id int GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    user_id bigint UNIQUE,
    username text,
    full_name text,
    referral text,
    referral_id text unique not null default gen_random_uuid(),
    card_fio text,
    card_phone text,
    card_number bigint UNIQUE default floor(random()*(999999-10+1))+1,
    card_status boolean default FALSE,
    birthday date,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    prize int default 0,
    balance int default 0
);

create table if not exists prize_codes
(
    id int GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    code bigint UNIQUE default floor(random()*(999999-10+1))+1,
    code_description text,
    user_id int,
    code_status boolean default TRUE,
    foreign key (user_id) references users(user_id)
);

create table if not exists orders_hall
(
    id int GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    admin_id bigint,
    admin_name text,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    order_status boolean default FALSE,
    table_number smallint,
    admin_answer varchar(12),
    chat_id bigint,
    user_id bigint,
    username text,
    full_name text,
    data_reservation DATE NOT NULL,
    time_reservation varchar(5),
    number_person smallint,
    phone text,
    comment text
);

create table if not exists category_menu
(
    id int GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    title text
);

create table if not exists items_menu
(
    id int GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    title varchar(30),
    description  text,
    photo text,
    price numeric(6, 2),
    category_id int,
    foreign key (category_id) references category_menu(id) ON DELETE CASCADE
);

