import time
import os
import csv
import threading
import pandas as pd
from data_handling_realtime import (get_dataframe_from_file,
                                    leave_only_last_line,
                                    get_last_order_time_from_file,
                                    set_position_state_to_closed_before_start)
from signals_with_ob_short_long_realtime import hourly_engulf_signals
from orders_sender import last_candle_ohlc, send_buy_sell_orders
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# pd.set_option('display.max_rows', 100)  # Increase the number of rows shown
pd.set_option('display.max_columns', 9)  # Increase the number of columns shown
pd.set_option('display.width', 700)  # Increase the terminal width for better visibility

# ******************************************* ORDER PARAMETERS *******************************************************
volume_value = 1                    # 1000 MAX for stocks. Used only in AU3 (MT5 assigns volume itself)
risk_reward = 2                     # Risk/Reward ratio (Not used with multiple TP-s)
stop_loss_offset = 1                # Is added to SL for Shorts and subtracted for Longs (can be equal to spread)

# hardcoded_sr_levels = [('2024-11-02 16:19:00', 69245.00), ('2024-11-02 16:19:00', 69167.00)]  # Example support levels
current_candle_max_size = 500
current_candle_min_size = 5
ob_candle_max_size = 500
ob_candle_min_size = 5
max_time_waiting_for_entry = 40     # Minutes

level_lifetime_minutes = 60   # Minutes after interaction

clear_csv_before_start = True
# **************************************************************************************************************

"""
Watchdog module monitors csv changes for adding new OHLC row and trigger main.py function calls 
only when new data is added to the CSV
"""

# LIIKURI PATHS
base_path = os.getcwd()
file = 'OHLCVData_1.csv'


buy_signal_flag = True                    # MUST BE TRUE BEFORE ENTERING MAIN LOOP
sell_signal_flag = True                   # MUST BE TRUE BEFORE ENTERING MAIN LOOP
last_signal = None                        # Initiate last signal

# LEAVE ONLY FIRST OHLC IN CSV BEFORE CREATING DATAFRAME
if clear_csv_before_start:
    leave_only_last_line()
    print('Csv first lines cleared before starting script'.upper())

set_position_state_to_closed_before_start('closed')  # Set position state to closed before starting script

# +------------------------------------------------------------------+
# +------------------------------------------------------------------+


def start_entry_watcher():  # Function to watch for changes in active_position.csv
    class EntryHandler(FileSystemEventHandler):
        def on_modified(self, event):
            if 'active_position.csv' in event.src_path:
                print("[ENTRY EVENT] Detected new entry price.")
                entry = read_entry_price()
                candle = read_last_candle()
                if entry and candle:
                    sl, tp = calc_sl_tp(entry, candle)
                    write_sl_tp(sl, tp)

    def read_entry_price():
        try:
            with open('active_position.csv', 'r') as file:
                rows = list(csv.reader(file))
                if rows:
                    return float(rows[-1][0])
        except Exception as e:
            print(f"[ERROR] Reading active_position.csv: {e}")
        return None

    def read_last_candle():
        try:
            with open('OHLCVData_1.csv', 'r') as f:
                rows = list(csv.reader(f, delimiter=';'))
                if rows:
                    last = rows[-1]
                    return {
                        'open': float(last[4]),
                        'high': float(last[5]),
                        'low': float(last[6]),
                        'close': float(last[7])
                    }
        except Exception as e:
            print(f"[ERROR] Reading OHLCVData_1.csv: {e}")
        return None

    def calc_sl_tp(entry, candle):
        risk = 20  # You can make this dynamic later
        sl = entry - risk
        tp = entry + risk
        return round(sl, 2), round(tp, 2)

    def write_sl_tp(sl, tp):
        try:
            with open('SL_TP_orders.csv', 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([sl, tp])
            print(f"[ENTRY LOGIC] SL: {sl}, TP: {tp} written to SL_TP_orders.csv")
        except Exception as e:
            print(f"[ERROR] Writing SL_TP_orders.csv: {e}")

    observer = Observer()
    observer.schedule(EntryHandler(), path='.', recursive=False)
    observer.start()
    print('[ENTRY WATCHER] Started watching for active_position.csv changes...')


# +------------------------------------------------------------------+
# +------------------------------------------------------------------+
class CsvChangeHandler(FileSystemEventHandler):
    print("\nScript successfully started. Waiting for first candle to close...".upper())

    def on_modified(self, event):
        global buy_signal_flag, sell_signal_flag, last_signal
        # print(f"File modified: {event.src_path}")  # This should print on any modification
        if not event.src_path == os.path.join(base_path, file):  # CSV file path
            return
        print("CSV file updated; triggering function calls...")
        # Call a function that contains all main calls
        buy_signal_flag, sell_signal_flag, last_signal = run_main_functions(
            buy_signal_flag, sell_signal_flag, last_signal
        )


def run_main_functions(b_s_flag, s_s_flag, l_signal):
    print('\n********************************************************************************************************')
    print('\n********************************************************************************************************')

    # nt8_levels_path = 'nt8_levels.csv'
    # valid_levels_path = 'python_valid_levels.csv'
    # expired_levels_path = 'expired_levels.csv'

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
        # ob_candle_max_size,
        # ob_candle_min_size
    )

    print(f'\nCandles processed since start: {candle_counter}')

    last_order_timestamp = get_last_order_time_from_file()

    last_candle_high, last_candle_low, last_candle_close, ticker = last_candle_ohlc(dataframe_from_log)

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
        last_order_timestamp,
        risk_reward
    )

    l_signal = s_signal
    return b_s_flag, s_s_flag, l_signal


if __name__ == "__main__":
    try:
        # Start NT8 entry SL/TP logic in background
        entry_thread = threading.Thread(target=start_entry_watcher, daemon=True)
        entry_thread.start()
        print('Entry watcher started...Waiting for active_position.csv changes...')

        # Start main OHLCV observer
        event_handler = CsvChangeHandler()
        observer = Observer()
        observer.schedule(event_handler, base_path, recursive=False)  # CSV folder path
        observer.start()
        print(f'Watching for changes in: {base_path}')
    except FileNotFoundError as e:
        print(f'Error: {e}. \nPlease check that the path: {base_path} exists and is accessible.')

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
