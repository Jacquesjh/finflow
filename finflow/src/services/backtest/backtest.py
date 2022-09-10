from datetime import datetime

import pandas as pd

from athena.src.services.pipeline.pipeline import Pipeline
from athena.src.services.plotting import plots
from athena.src.utils import utils


class Backtest:

    pipeline: BasePipeline

    def __init__(self, pipeline: BasePipeline) -> None:
        self.pipeline = pipeline

    def _get_weights(self, dates: list) -> pd.DataFrame:
        df_weights = pd.DataFrame()

        for date in dates:
            raw_df = self.data.loc[:date]

            weights = self.pipeline.run(ohlc=data)

            df_weights = pd.concat([df_weights, weights])

        df_weights = df_weights.sort_index()

        return df_weights

    def _get_returns_dataframe(self, weights: pd.DataFrame) -> pd.Series:
        indexes = self.data["Close"].loc[weights.index[0] :].index
        returns = pd.DataFrame(columns=["returns"], index=indexes)

        for index in indexes:
            """
            The backtest buys at Open price, so this if statment is the return of the day the backtest bought.
            So in this case, I compare the Close price of day 0 to the Buy price of day 0. Outside this case,
            I compare the Close price of day 0 and the Close price of day -1.
            """
            if index in weights.index:
                current_weights = weights.loc[index].dropna()

                buy_prices = self.data["Open"][current_weights.index].loc[index]
                ref_prices = buy_prices

            close_prices = self.data["Close"][current_weights.index].loc[index]
            asset_returns = (close_prices - ref_prices) / ref_prices

            day_return = (asset_returns * current_weights).sum()
            returns["returns"].loc[index] = day_return

            ref_prices = close_prices

        return returns["returns"].dropna()

    def run(self, ohlc: pd.DataFrame, rebalance_interval: str) -> None:
        dates = utils.get_dates(
            raw_df=self.data, rebalance_interval=self.rebalance_interval, start_date=self.start_date
        )

        weights = self._get_weights(dates=dates)
        returns = self._get_returns_dataframe(weights=weights)

        results = dict()
        results["returns"] = returns
        results["weights"] = weights

        return results
