import time
import os
import pandas as pd
from data_handling_realtime import (get_dataframe_from_file,
                                    leave_only_last_line,
                                    get_last_order_time_from_file)
from signals_with_ob_short_long_realtime import hourly_engulf_signals
from orders_sender import last_candle_ohlc, send_buy_sell_orders
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# pd.set_option('display.max_rows', 100)  # Increase the number of rows shown
pd.set_option('display.max_columns', 9)  # Increase the number of columns shown
pd.set_option('display.width', 700)  # Increase the terminal width for better visibility

# ******************************************* ORDER PARAMETERS *******************************************************
volume_value = 1                    # 1000 MAX for stocks. Used only in AU3 (MT5 assigns volume itself)
risk_reward = 1                     # Risk/Reward ratio (Not used with multiple TP-s)
stop_loss_offset = 1                # Is added to SL for Shorts and subtracted for Longs (can be equal to spread)

# hardcoded_sr_levels = [('2024-11-02 16:19:00', 69245.00), ('2024-11-02 16:19:00', 69167.00)]  # Example support levels
current_candle_max_size = 200
current_candle_min_size = 20
ob_candle_max_size = 200
ob_candle_min_size = 200
max_time_waiting_for_entry = 40     # Minutes

level_lifetime_minutes = 60   # Minutes after interaction

clear_csv_before_start = True
# **************************************************************************************************************

# LIIKURI PATHS
path_ohlc_check_for_change = 'C:\\Users\\Liikurserv\\PycharmProjects\\RT_Ninja\\'
file = 'OHLCVData_1.csv'

# SILLAMAE PATHS
# path =
# 'C:\\Users\\Vova deduskin lap\\AppData\\Roaming\\MetaQuotes\\Terminal\\D0E8209F77C8CF37AD8BF550E51FF075\\MQL5\\Files'
# file = 'OHLCVData_475.csv'
# SILLAMAE PATHS

buy_signal_flag = True                    # MUST BE TRUE BEFORE ENTERING MAIN LOOP
sell_signal_flag = True                   # MUST BE TRUE BEFORE ENTERING MAIN LOOP
last_signal = None                              # Initiate last signal

# LEAVE ONLY FIRST OHLC IN CSV BEFORE CREATING DATAFRAME
if clear_csv_before_start:
    leave_only_last_line()
    print('Csv first lines cleared before starting script'.upper())

"""
Watchdog module monitors csv changes for adding new OHLC row and trigger main.py function calls 
only when new data is added to the CSV
"""


class CsvChangeHandler(FileSystemEventHandler):
    print("\nScript successfully started. Waiting for first candle to close...".upper())

    def on_modified(self, event):
        global buy_signal_flag, sell_signal_flag, last_signal
        # print(f"File modified: {event.src_path}")  # This should print on any modification
        if not event.src_path == os.path.join(path_ohlc_check_for_change, file):  # CSV file path
            return
        print("CSV file updated; triggering function calls...")
        # Call a function that contains all main calls
        buy_signal_flag, sell_signal_flag, last_signal = run_main_functions(
            buy_signal_flag, sell_signal_flag, last_signal
        )


def run_main_functions(b_s_flag, s_s_flag, l_signal):
    print('\n********************************************************************************************************')
    print('\n********************************************************************************************************')

    nt8_levels_path = 'nt8_levels.csv'
    valid_levels_path = 'python_valid_levels.csv'
    expired_levels_path = 'expired_levels.csv'

    # GET DATAFRAME FROM LOG
    dataframe_from_log, last_datetime_of_df = get_dataframe_from_file(max_time_waiting_for_entry)
    # print('\nget_dataframe_from_file: \n', dataframe_from_log[-10:])
    # print('last_date!!!!!', last_datetime_of_df)

    # SIGNALS
    (
        s_signal,               # signal 100 or -100
        n_index,                # index
        stop_market_price,      # stop-market order price
        candle_counter,
        s_time,
        signals_counter
    ) = hourly_engulf_signals(
        dataframe_from_log,
        # max_time_waiting_for_entry,
        current_candle_max_size,
        current_candle_min_size,
        ob_candle_max_size,
        ob_candle_min_size
    )

    print(f'\nCandles processed since start: {candle_counter}')

    last_order_timestamp = get_last_order_time_from_file()

    # SEND ORDERS
    (
        b_s_flag,
        s_s_flag,
    ) = send_buy_sell_orders(
        stop_market_price,
        l_signal,
        s_signal,
        n_index,
        b_s_flag,
        s_s_flag,
        last_candle_high,
        last_candle_low,
        stop_loss_offset,
        s_time,
        last_order_timestamp
    )

    l_signal = s_signal
    return b_s_flag, s_s_flag, l_signal


if __name__ == "__main__":
    try:
        event_handler = CsvChangeHandler()
        observer = Observer()
        observer.schedule(event_handler, path_ohlc_check_for_change, recursive=False)  # CSV folder path
        observer.start()
    except FileNotFoundError as e:
        print(f'Error: {e}. \nPlease check that the path: {path_ohlc_check_for_change} exists and is accessible.')

    else:
        # Run the observer only if no exceptions were raised
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print()
            print('Program stopped manually'.upper())
            observer.stop()
        observer.join()
