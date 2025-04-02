import pandas as pd
# from data_handling_realtime import get_position_state

"""
Main function analyzing price interaction with levels and long/short signals generation logics
"""


def hourly_engulf_signals(
        output_df,
        # max_time_waiting_for_entry,
        current_candle_max_size,
        current_candle_min_size,
        ob_candle_max_size,
        ob_candle_min_size
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
    # def check_time_limit(
    #         m_time_waiting_for_entry,
    #         subs_index,
    #         candle_time,
    #         lev_inter_signal_time,
    #         t_diff,
    #         trce
    # ):
    #
    #     if t_diff > m_time_waiting_for_entry:
    #         print(
    #             "xxxxxxxxxxxxxxxxx\n"
    #             f"x {trce}: Exceeded {m_time_waiting_for_entry}-minute window "
    #             f"at index {subs_index}, \n"
    #             f"x Level interaction time: {lev_inter_signal_time}, \n"
    #             f"x Candle time: {candle_time}, \n"
    #             f"x Time diff: {t_diff} minutes\n"
    #             "xxxxxxxxxxxxxxxxx"
    #         )
    #         return True
    #     return False

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
        # current_candle_time = row['Time']
        current_candle_body_size = abs(current_candle_open - current_candle_close)

        # Check if current candle is GREEN:
        if current_candle_close > current_candle_open:
            if current_candle_max_size >= current_candle_body_size >= current_candle_min_size:

                # **************************************************************************************************
                # SHORTS LOGICS BEGIN HERE
                # **************************************************************************************************

                side = 'short'

                for subsequent_index in range(index + 1, len(output_df)):
                    potential_ob_candle = output_df.iloc[subsequent_index]
                    potential_ob_candle_open = potential_ob_candle['Open']
                    potential_ob_candle_high = potential_ob_candle['High']
                    potential_ob_candle_low = potential_ob_candle['Low']
                    potential_ob_candle_close = potential_ob_candle['Close']

                    potential_ob_body_size = abs(potential_ob_candle_open - potential_ob_candle_close)
                    potential_ob_doji = (potential_ob_body_size * 100) / (potential_ob_candle_high - potential_ob_candle_low)
                    potential_ob_time = pd.to_datetime(potential_ob_candle['Time'])

                    print(f"Looking for RED candle at index {subsequent_index}, "
                          f"Time: {potential_ob_time}")

                    # If candle is RED
                    if potential_ob_candle_close < potential_ob_candle_open:
                        print(
                            f"○ Last RED candle found at index {subsequent_index}, "
                            f"Time: {potential_ob_time}"
                        )
                        # If RED candle closed below initial GREEN candle:
                        if potential_ob_candle_close < current_candle_low:
                            print(
                                f"○ RED candle has closed BELOW initial candle  {subsequent_index}, "
                                f"Time: {potential_ob_time}"
                            )
                            # If the size of candle is within limits:
                            if ob_candle_max_size >= potential_ob_body_size >= ob_candle_min_size:
                                if potential_ob_doji >= 15:

                                    print('SEND SELL_LIMIT.1A')
                                    signal = f'-100+{subsequent_index}'

                                    signals_counter += 1

                                    s_signal, n_index, t_price, s_time = signal_triggered_output(
                                        subsequent_index,
                                        potential_ob_time,
                                        potential_ob_candle_low,
                                        side,
                                        signal
                                    )
                                else:
                                    print(f"RED candle is doji (has body {potential_ob_doji})%")
                            else:
                                print(f"RED candle size ({potential_ob_body_size}) is not within limits")
                        else:
                            print(f"RED candle hasn't closed BELOW initial candle")
                    else:
                        print(f"Candle is not RED, checking next candle")

        # If first condition is not true then is RED, and we are looking for longs:
        else:
            #  ********************************************************************************************
            #  LONGS LOGICS BEGIN HERE
            #  ********************************************************************************************

            side = 'long'

            for subsequent_index in range(index + 1, len(output_df)):
                potential_ob_candle = output_df.iloc[subsequent_index]
                potential_ob_candle_open = potential_ob_candle['Open']
                potential_ob_candle_high = potential_ob_candle['High']
                potential_ob_candle_low = potential_ob_candle['Low']
                potential_ob_candle_close = potential_ob_candle['Close']

                potential_ob_body_size = abs(potential_ob_candle_open - potential_ob_candle_close)
                potential_ob_doji = (potential_ob_body_size * 100) / (potential_ob_candle_high - potential_ob_candle_low)
                potential_ob_time = pd.to_datetime(potential_ob_candle['Time'])

                print(
                    f"Looking for GREEN candle at index {subsequent_index}, "
                    f"Time: {potential_ob_time}"
                )

                # If candle is GREEN
                if potential_ob_candle_close > potential_ob_candle_open:

                    print(
                        f"○ Last GREEN candle found at index {subsequent_index}, "
                        f"Time: {potential_ob_time}"
                    )
                    # If GREEN candle closed ABOVE initial GREEN candle:
                    if potential_ob_candle_close > current_candle_high:
                        print(
                            f"○ GREEN candle has closed ABOVE initial candle  {subsequent_index}, "
                            f"Time: {potential_ob_time}"
                        )
                        # If the size of candle is within limits:
                        if ob_candle_max_size >= potential_ob_body_size >= ob_candle_min_size:
                            if potential_ob_doji >= 15:

                                print('SEND BUY_LIMIT.2A')
                                signal = f'100+{subsequent_index}'
                                signals_counter += 1

                                s_signal, n_index, t_price, s_time = signal_triggered_output(
                                    subsequent_index,
                                    potential_ob_time,
                                    potential_ob_candle_low,
                                    side,
                                    signal
                                )
                            else:
                                print(f"GREEN candle is doji (has body {potential_ob_doji})%")
                        else:
                            print(f"GREEN candle size ({potential_ob_body_size}) is not within limits")
                    else:
                        print(f"GREEN candle hasn't closed ABOVE initial candle")
                else:
                    print(f"Candle is not GREEN, checking next candle")

    return (
            s_signal,   # signal 100 or -100
            n_index,    # index
            t_price,    # stop-market order price
            candle_counter,
            s_time,
            signals_counter
    )
