import pytest
import pandas as pd
from exchange_engine import ExchangeEngine
from exchange_getter import ExchangeGetter


def test_exchange_engine():
    # read test_data.csv
    true_currency_df = pd.read_csv('tests/test_data/true_exchange_rate.csv')

    # run exchange engine
    currency_exchange_list = ['USDCAD', 'GBPCAD', 'EURCAD']
    file_path = r'tests/test_data/2024_Bloomberg FX Fwd Curve.xlsx'
    start_month = 1
    start_year = 2024

    currency_exchange_dict = ExchangeGetter.get_currency_exchange(file_path=file_path,
                                                                  currency_exchange_list=currency_exchange_list)

    exchange_engine = ExchangeEngine(start_month=start_month, start_year=start_year)

    process_pipeline = [exchange_engine.clean_currency_exchange_dfs,  # select columns, drop empty cells, etc.
                        exchange_engine.add_year_month,  # transform date, add year and month columns
                        exchange_engine.calculate_mean_exchange_rate,
                        # calculate mean exchange based on forward bid and ask
                        exchange_engine.select_starting_point_rate,
                        # select the starting point rate for start year and month
                        exchange_engine.forward_fill_exchange_rate,
                        # forward fill the exchange rate for the next 100 years
                        ]

    for currency_key in currency_exchange_dict:
        for process in process_pipeline:
            currency_exchange_dict[currency_key] = process(currency_exchange_dict[currency_key])

        # update column 'mean_exchange_rate' base on dict key value
        currency_exchange_dict[currency_key] = exchange_engine.rename_df_based_on_key(
            currency_exchange_dict[currency_key], currency_key)

    # combine all exchange rate into 1 dataframe, base on year and month column
    mega_exchange_rate_df = exchange_engine.combine_currency_exchange_dfs(list(currency_exchange_dict.values()))

    # compare the result with the true_currency_df
    check_list = [(2024, 1), (2024, 2), (2024, 3), (2024, 4), (2024, 5), (2024, 6),
                  (2024, 7), (2024, 8), (2024, 9), (2024, 10), (2024, 11), (2024, 12),
                  (2025, 1), (2025, 2), (2025, 3), (2025, 4), (2025, 5), (2025, 6),
                  (2035, 1), (2035, 2), (2035, 3), (2035, 4), (2035, 5), (2035, 6),
                  (2049, 1), (2049, 2), (2049, 3), (2049, 4), (2049, 5), (2049, 6),
                  (2051, 1), (2051, 2), (2051, 3), (2051, 4), (2051, 5), (2051, 6), ]

    currency_exchange_list = ['USDCAD', 'GBPCAD', 'EURCAD']

    for year, month in check_list:
        for currency in currency_exchange_list:
            tested_value = mega_exchange_rate_df[(mega_exchange_rate_df['year'] == year) &
                                                 (mega_exchange_rate_df['month'] == month)][
                f'{currency}_Exchange_Rate'].values[0]

            test_value = round(tested_value, 4)

            true_value = true_currency_df[(true_currency_df['year'] == year) &
                                          (true_currency_df['month'] == month)][f'{currency}_Exchange_Rate'].values[0]

            true_value = round(true_value, 4)

            assert test_value == true_value
