import pandas as pd


class ExchangeGetter:
    """
    Exchanger Getter only includes static methods to better management.
    All static methods, that exposed to user, force keyword arguments for abstraction layer clarity.
    """
    CURRENCY_SPREADSHEET_ROW_SKIP = 8

    @staticmethod
    def get_currency_exchange(*, file_path: str, currency_exchange_list: list) -> dict:
        """
        return a dict of currency exchange data from bloomberg spreadsheet.
        """

        skip_rows = ExchangeGetter.CURRENCY_SPREADSHEET_ROW_SKIP
        currency_exchange_dict = {}

        for currency in currency_exchange_list:
            try:
                currency_exchange_dict[currency] = pd.read_excel(file_path, sheet_name=currency, skiprows=skip_rows)
            except ValueError:
                raise ValueError(f"Currency {currency} not found in the spreadsheet. "
                                 f"Possible incorrect tab naming in Bloomberg Spreadsheet.")

        return currency_exchange_dict








