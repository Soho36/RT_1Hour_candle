from data_handling_realtime import active_position, write_sl_tp


"""
Main function analyzing price interaction with levels and long/short signals generation logics
"""


def hourly_engulf_signals(
        output_df,
        # max_time_waiting_for_entry,
        current_candle_max_size,
        current_candle_min_size,
        # ob_candle_max_size,
        # ob_candle_min_size
):
    # signals_threshold = 10
    n_index = None
    s_signal = None
    t_price = None
    s_time = None
    candle_counter = 0
    signals_counter = 0

    output_df.reset_index(inplace=True)

    """
    Function to check if the time difference has exceeded the time limit and print the necessary information.
    Returns True if the time limit is exceeded, otherwise False.
    """


    """
    Print triggered signals
    """
    def signal_triggered_output(
            nn_index,
            sig_time,
            tt_price,
            t_side,
            ss_signal
    ):

        print(
            "++++++++++++++++++++++++++\n"
            f"+ {t_side.capitalize()} triggered at index {nn_index}, "
            f"Time: {sig_time}, "
            f"Stop-market price: {tt_price}\n"
            f"+ s_signal: {ss_signal}\n"
            "++++++++++++++++++++++++++"
        )
        print('-----------------------------------------------------------------------------------------------------')
        return ss_signal, nn_index, tt_price, sig_time     # RETURNS SIGNAL FOR send_buy_sell_orders()

    # Start looping through dataframe
    for index, row in output_df.iterrows():
        candle_counter += 1

        current_candle_open = row['Open']
        current_candle_close = row['Close']
        current_candle_high = row['High']
        current_candle_low = row['Low']
        current_candle_time = row['Time']
        current_candle_range = abs(current_candle_high - current_candle_low)
        initial_tp_longs = current_candle_high + current_candle_range
        initial_tp_shorts = current_candle_low - current_candle_range

        # Check if current candle is GREEN:
        if current_candle_close > current_candle_open:
            if current_candle_max_size >= current_candle_range >= current_candle_min_size:
                print(
                    f"○ GREEN candle found at index {index}, candle size is OK, "
                    f"Time: {current_candle_time}\n"
                    f"Min: {current_candle_min_size}, Body: {current_candle_range}, Max: {current_candle_max_size}"
                )
                print('SEND SELL_STOP')
                signal = f'-100+{index}'

                signals_counter += 1
                side = 'short'

                s_signal, n_index, t_price, s_time = signal_triggered_output(
                    index,
                    current_candle_time,
                    current_candle_low,
                    side,
                    signal
                )

            else:
                print("GREEN candle size is not OK")
        # if active_position():
        #     print("Active position is open (shorts)")
        #     write_sl_tp(current_candle_low, initial_tp_shorts)
        #     print("SL and TP orders are written to file (shorts)")

        # IF FIRST CONDITION IS NOT TRUE THEN CANDLE IS RED, AND WE ARE LOOKING FOR LONGS:
        else:
            if current_candle_max_size >= current_candle_range >= current_candle_min_size:
                print(
                    f"○ RED candle found at index {index}, candle size is OK, "
                    f"Time: {current_candle_time}\n"
                    f"Min: {current_candle_min_size}, Body: {current_candle_range}, Max: {current_candle_max_size}"
                )
                print('SEND BUY_STOP')
                signal = f'100+{index}'
                signals_counter += 1
                side = 'long'

                s_signal, n_index, t_price, s_time = signal_triggered_output(
                    index,
                    current_candle_time,
                    current_candle_high,
                    side,
                    signal
                )

            else:
                print("RED candle size is not OK")

        if active_position():
            print("Active position is open (longs)")
            write_sl_tp(initial_tp_longs)
            print("SL and TP orders are written to file (longs)")

    return (
            s_signal,   # signal 100 or -100
            n_index,    # index
            t_price,    # stop-market order price
            candle_counter,
            s_time,
            signals_counter
    )
