# import pandas as pd
# from data_handling_realtime import get_position_state

"""
Main function analyzing price interaction with levels and long/short signals generation logics
"""


def hourly_engulf_signals(
        output_df,
        # max_time_waiting_for_entry,
        ob_candle_size
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
            ss_signal,
            sig_counter
    ):

        print(
            "++++++++++++++++++++++++++\n"
            f"+ {t_side.capitalize()} triggered at index {nn_index}, "
            f"Time: {sig_time}, "
            f"Stop-market price: {tt_price}\n"
            f"+ s_signal: {ss_signal}\n"
            f"signals count: {sig_counter}\n"
            "++++++++++++++++++++++++++"
        )
        print('-----------------------------------------------------------------------------------------------------')
        return ss_signal, nn_index, tt_price, sig_time     # RETURNS SIGNAL FOR send_buy_sell_orders()

    for index, row in output_df.iterrows():
        previous_close = output_df.iloc[index - 1]['Close'] if index > 0 else None
        previous_open = output_df.iloc[index - 1]['Open'] if index > 0 else None
        current_candle_close = row['Close']
        current_candle_open = row['Open']
        current_candle_high = row['High']
        current_candle_low = row['Low']
        current_candle_time = row['Time']
        ob_body = abs(current_candle_open - current_candle_close)

        potential_ob_doji = (
                (ob_body * 100) /
                (current_candle_high - current_candle_low))

        # Convert to datetime for time calculations
        # potential_ob_time = pd.to_datetime(current_candle_time)

        # **************************************************************************************************
        # SHORTS LOGICS BEGIN HERE
        # **************************************************************************************************

        side = 'short'
        # Check if the previous candle is green:
        if previous_close > previous_open:

            # Check if the current candle is red:
            if current_candle_close < current_candle_open:

                # Check if OB candle size is within threshold:
                if current_candle_high - current_candle_low <= ob_candle_size:

                    # Check if OB size is OK
                    if potential_ob_doji >= 15:
                        if ob_body >= 5:
                            print('SEND SELL LIMIT ORDER')
                            signal = f'-100+{index}'

                            signals_counter += 1

                            s_signal, n_index, t_price, s_time = signal_triggered_output(
                                index,
                                current_candle_time,
                                current_candle_low,
                                side,
                                signal,
                                signals_counter
                            )
                        else:
                            print(
                                f"Green candle (has too small body {ob_body})")
                    else:
                        print(f"Green candle is doji (has body {potential_ob_doji})%")
                else:
                    print(f"Green candle is bigger than max size ({ob_candle_size})")

            #  ********************************************************************************************
            #  LONGS LOGICS BEGIN HERE
            #  ********************************************************************************************

            side = 'long'
            # Check if the previous candle is red:
            if previous_close < previous_open:

                # Check if the current candle is green:
                if current_candle_close > current_candle_open:

                    # Check if OB candle size is within threshold:
                    if current_candle_high - current_candle_low <= ob_candle_size:

                        # Check if OB size is OK
                        if potential_ob_doji >= 15:
                            if ob_body >= 5:
                                print('SEND BUY LIMIT ORDER')
                                signal = f'100+{index}'

                                signals_counter += 1

                                s_signal, n_index, t_price, s_time = signal_triggered_output(
                                    index,
                                    current_candle_time,
                                    current_candle_high,
                                    side,
                                    signal,
                                    signals_counter
                                )
                            else:
                                print(f"Red candle (has too small body {ob_body})")
                        else:
                            print(f"Red candle is doji (has body {potential_ob_doji})%")
                    else:
                        print(f"Red candle is bigger than max size ({ob_candle_size})")
        # else:
        #     print(f"Signals_threshold: {signals_threshold} reached")

    return (
            s_signal,
            n_index,
            t_price,
            candle_counter,
            s_time,
            signals_counter
    )
