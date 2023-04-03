import pandas as pd
import numpy as np

from quantfreedom.enums.enums import OrderType
from quantfreedom._typing import (
    RecordArray,
    Array1d,
)

import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, dash_table
from jupyter_dash import JupyterDash
from plotly.subplots import make_subplots
from dash_bootstrap_templates import load_figure_template


def get_candle_trace_data(
    index_prices,
    open_prices,
    high_prices,
    low_prices,
    close_prices,
    order_records,
    indicator_dict,
):
    array_size = open_prices.shape[0]

    order_price = np.full(array_size, np.nan)
    avg_entry = np.full(array_size, np.nan)
    stop_loss = np.full(array_size, np.nan)
    trailing_sl = np.full(array_size, np.nan)
    take_profit = np.full(array_size, np.nan)

    or_counter = 0
    array_counter = 0

    temp_avg_entry = np.array([0])
    temp_stop_loss = np.array([0])
    temp_trailing_sl = np.array([0])
    temp_take_profit = np.array([0])

    for i in range(array_size):
        if or_counter < order_records.size and order_records["bar"][or_counter] == i:
            fill_candle_trace_trades(
                order_records=order_records[or_counter],

                order_price=order_price[array_counter],
                avg_entry=avg_entry[array_counter],
                stop_loss=stop_loss[array_counter],
                trailing_sl=trailing_sl[array_counter],
                take_profit=take_profit[array_counter],

                temp_avg_entry=temp_avg_entry[0],
                temp_stop_loss=temp_stop_loss[0],
                temp_trailing_sl=temp_trailing_sl[0],
                temp_take_profit=temp_take_profit[0],
            )
            or_counter += 1

            if or_counter < order_records.size and order_records["bar"][or_counter] == i:
                fill_candle_trace_trades(
                    order_records=order_records[or_counter],

                    order_price=order_price[array_counter],
                    avg_entry=avg_entry[array_counter],
                    stop_loss=stop_loss[array_counter],
                    trailing_sl=trailing_sl[array_counter],
                    take_profit=take_profit[array_counter],

                    temp_avg_entry=temp_avg_entry[0],
                    temp_stop_loss=temp_stop_loss[0],
                    temp_trailing_sl=temp_trailing_sl[0],
                    temp_take_profit=temp_take_profit[0],
                )
            or_counter += 1
        array_counter += 1
    trace_data_list = cerate_candle_trace_trades_list(
        index_prices,
        open_prices,
        high_prices,
        low_prices,
        close_prices,
        order_price,
        avg_entry,
        stop_loss,
        trailing_sl,
        take_profit,
    )
    if list(indicator_dict.keys())[0] == "candle_chart":
        temp_ind_vals = np.array([0], dtype=object)
        for candle_ind_key, candle_ind_value in indicator_dict["candle_chart"].items():
            append_to_trace_data_list(
                trace_data_list,
                index_prices=index_prices,
                dict_key=candle_ind_key,
                dict_value=candle_ind_value,
                temp_ind_vals=temp_ind_vals,
            )
    return trace_data_list

def fill_candle_trace_trades(
    order_records: RecordArray,
    order_price: Array1d,
    avg_entry: Array1d,
    stop_loss: Array1d,
    trailing_sl: Array1d,
    take_profit: Array1d,
    temp_avg_entry: Array1d,
    temp_stop_loss: Array1d,
    temp_trailing_sl: Array1d,
    temp_take_profit: Array1d,
):
    if temp_avg_entry != order_records["avg_entry"]:
        temp_avg_entry = order_records["avg_entry"]
    else:
        temp_avg_entry = np.nan

    if temp_stop_loss != order_records["sl_prices"]:
        temp_stop_loss = order_records["sl_prices"]
    else:
        temp_stop_loss = np.nan

    if temp_trailing_sl != order_records["tsl_prices"]:
        temp_trailing_sl = order_records["tsl_prices"]
    else:
        temp_trailing_sl = np.nan

    if temp_take_profit != order_records["tp_prices"]:
        temp_take_profit = order_records["tp_prices"]
    else:
        temp_take_profit = np.nan

    if np.isnan(order_records["real_pnl"]):
        order_price = order_records["price"]
        avg_entry = temp_avg_entry
        stop_loss = temp_stop_loss
        trailing_sl = temp_trailing_sl
        take_profit = temp_take_profit

    elif order_records["real_pnl"] > 0 and (
        order_records["order_type"] == OrderType.LongTP
        or order_records["order_type"] == OrderType.ShortTP
    ):
        order_price = np.nan
        avg_entry = np.nan
        stop_loss = np.nan
        trailing_sl = np.nan
        take_profit = order_records["tp_prices"]

    elif order_records["real_pnl"] > 0 and (
        order_records["order_type"] == OrderType.LongTSL
        or order_records["order_type"] == OrderType.ShortTSL
    ):
        order_price = np.nan
        avg_entry = np.nan
        stop_loss = np.nan
        trailing_sl = order_records["tsl_prices"]
        take_profit = np.nan

    elif order_records["real_pnl"] <= 0:
        order_price = np.nan
        avg_entry = np.nan
        stop_loss = order_records["sl_prices"]
        trailing_sl = order_records["tsl_prices"]
        take_profit = np.nan

    temp_avg_entry = order_records["avg_entry"]
    temp_stop_loss = order_records["sl_prices"]
    temp_trailing_sl = order_records["tsl_prices"]
    temp_take_profit = order_records["tp_prices"]


def cerate_candle_trace_trades_list(
    index_prices,
    open_prices,
    high_prices,
    low_prices,
    close_prices,
    order_price,
    avg_entry,
    stop_loss,
    trailing_sl,
    take_profit,
):
    return [
        go.Candlestick(
            x=index_prices,
            open=open_prices,
            high=high_prices,
            low=low_prices,
            close=close_prices,
            name="Candles",
            legendgroup="1",
        ),
        # go.Scatter(
        #     name="Entries",
        #     x=index_prices,
        #     y=order_price,
        #     mode="markers",
        #     marker=dict(
        #         color="yellow",
        #         size=10,
        #         symbol="square",
        #         line=dict(color="black", width=1),
        #     ),
        #     legendgroup="1",
        # ),
        go.Scatter(
            name="Avg Entries",
            x=index_prices,
            y=avg_entry,
            mode="markers",
            marker=dict(
                color="lightblue",
                size=10,
                symbol="circle",
                line=dict(color="black", width=1),
            ),
        ),
        go.Scatter(
            name="Stop Loss",
            x=index_prices,
            y=stop_loss,
            mode="markers",
            marker=dict(
                color="orange",
                size=10,
                symbol="x",
                line=dict(color="black", width=1),
            ),
        ),
        go.Scatter(
            name="Trailing SL",
            x=index_prices,
            y=trailing_sl,
            mode="markers",
            marker=dict(
                color="orange",
                size=10,
                symbol="triangle-up",
                line=dict(color="black", width=1),
            ),
        ),
        go.Scatter(
            name="Take Profits",
            x=index_prices,
            y=take_profit,
            mode="markers",
            marker=dict(
                color="#57FF30",
                size=10,
                symbol="star",
                line=dict(color="black", width=1),
            ),
        ),
    ]


def append_to_trace_data_list(
    trace_data_list: list,
    dict_key,
    dict_value,
    index_prices,
    temp_ind_vals,
):
    if "values" in dict_key:
        temp_ind_vals[0] = dict_value.values.flatten()
        trace_data_list.append(
            go.Scatter(
                x=index_prices,
                y=temp_ind_vals[0],
                mode="lines",
            )
        )
    elif "entries" in dict_key:
        temp_ind_entries = np.where(
            dict_value.values.flatten(), temp_ind_vals[0], np.nan
        ).flatten()
        trace_data_list.append(
            go.Scatter(
                x=index_prices,
                y=temp_ind_entries,
                mode="markers",
            )
        )