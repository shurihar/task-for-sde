create table if not exists public.exchange_rates (
    base_currency text not null,
    relative_currency text not null,
    exchange_date date not null,
    exchange_rate numeric(20, 10) not null,
    previous_exchange_rate numeric(20, 10) not null,
    percentage_change numeric(20, 10) not null,
    constraint exchange_rates_pk primary key (base_currency, relative_currency, exchange_date)
)
