import pandas as pd
from functools import reduce


class ExchangeEngine:
    """
    Exchange Engine is responsible for cleaning, processing, and storing the currency exchange data
    """

    def __init__(self, *, start_month: int, start_year: int) -> None:
        self.start_month = start_month
        self.start_year = start_year
        self.year_range = 100
        self.exchange_df = None

    def load_mega_exchange_rate(self, exchange_rate_df) -> None:
        self.exchange_df = exchange_rate_df

    def get_mega_exchange_rate(self) -> pd.DataFrame:
        return self.exchange_df

    def export_exchange_df(self, file_name: str) -> None:
        self.exchange_df.to_csv(file_name, index=False)

    @staticmethod
    def clean_currency_exchange_dfs(currency_df: pd.DataFrame) -> pd.DataFrame:
        """
        Select the relevant columns, drop any rows with missing values, and rename the columns.
        for loop approach for better readability and clarity.
        """

        try:
            currency_df = currency_df.iloc[:, :6]
            currency_df = currency_df.dropna(axis=0, how='any')

            standard_columns = ['time_range', 'date', 'point_bid',
                                'point_ask', 'forwards_bid', 'forwards_ask']

            currency_df.columns = standard_columns

            # point_bid and point_ask not needed anymore, release memory
            currency_df.drop(columns=['point_bid', 'point_ask'], inplace=True)
            currency_df.dropna()
            return currency_df

        except ValueError:
            raise ValueError(f"Currency exchange data not in the expected format. "
                             f"Possible incorrect data format in Bloomberg Spreadsheet.")

    @staticmethod
    def add_year_month(currency_df: pd.DataFrame) -> pd.DataFrame:
        """
        Transform the currency exchange data: convert data types, index, etc.
        for loop approach for better readability and clarity.
        """
        # convert date object into datatime, add month, year column
        try:
            currency_df.date = pd.to_datetime(currency_df.date)
            currency_df['month'] = currency_df.date.dt.month
            currency_df['year'] = currency_df.date.dt.year

            return currency_df

        except SyntaxError:
            raise SyntaxError(f"Incorrect format for currency exchange dates. "
                              f"Check Bloomberg Spreadsheet.")

    @staticmethod
    def calculate_mean_exchange_rate(currency_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate the mean exchange rate for each currency pair.
        for loop approach for better readability and clarity.
        """
        try:
            currency_df['mean_exchange_rate'] = (currency_df['forwards_bid'] +
                                                 currency_df['forwards_ask']) / 2
            currency_df.drop(columns=['forwards_bid', 'forwards_ask'], inplace=True)
            return currency_df

        except ValueError:
            raise ValueError(f"Error in calculating mean exchange rate. "
                             f"Check Bloomberg Spreadsheet.")

    def select_starting_point_rate(self, currency_df: pd.DataFrame) -> pd.DataFrame:
        """
        Select the starting point rate for each currency pair.
        for loop approach for better readability and clarity.
        """

        df_starting_point = currency_df[(currency_df['month'] == self.start_month) &
                                        (currency_df['year'] == self.start_year) &
                                        (currency_df['time_range'] == 'SP')]

        if df_starting_point.empty:
            raise ValueError(f'Starting point not found. '
                             f'Check Bloomberg Spreadsheet')

        # remove all rows with starting month and year, add df_starting_point to current currency df
        df_to_removed = currency_df[(currency_df['year'] == self.start_year) &
                                    (currency_df['month'] == self.start_month)]

        currency_df = currency_df[~currency_df.isin(df_to_removed)]
        currency_df = pd.concat([currency_df, df_starting_point])
        currency_df.sort_values(by=['date'], inplace=True)

        # time_range and date not needed anymore, release memory
        currency_df.drop(columns=['time_range', 'date'], inplace=True)

        return currency_df

    def forward_fill_exchange_rate(self, currency_df: pd.DataFrame) -> pd.DataFrame:
        """
        Forward fill missing data.
        for loop approach for better readability and clarity.
        """

        # create an empty dataframe  with a year range of 100 years, each year with 12 month
        year_min = int(currency_df.year.min())
        year_max = int(currency_df.year.min() + self.year_range)

        years = [year for year in range(year_min, year_max + 1)] * 12
        months = [month for month in range(1, 13)] * (year_max - year_min + 1)

        df_all_years = pd.DataFrame({'year': years, 'month': months})
        df_all_years.sort_values(by=['year', 'month'], inplace=True)
        df_all_years.reset_index(drop=True, inplace=True)

        # merge input currency dataframe with newly constructed df, then forward fill
        df_merged = df_all_years.merge(currency_df, on=['year', 'month'], how='left')
        df_merged.ffill(inplace=True)

        return df_merged

    @staticmethod
    def rename_df_based_on_key(currency_df: pd.DataFrame, key: str) -> pd.DataFrame:
        currency_df.rename(columns={'mean_exchange_rate': f'{key}_Exchange_Rate'}, inplace=True)
        return currency_df

    @staticmethod
    def combine_currency_exchange_dfs(df_list: list[pd.DataFrame]):
        mega_df = reduce(lambda left, right: pd.merge(left, right, on=['year', 'month']), df_list)
        return mega_df


