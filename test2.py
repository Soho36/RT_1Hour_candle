from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


base_path = os.getcwd()
file = 'OHLCVData_1.csv'

class CsvChangeHandler(FileSystemEventHandler):
    # print("\nScript successfully started. Waiting for first candle to close...".upper())
    print(Fore.YELLOW + Style.BRIGHT + "\nScript successfully started. Waiting for first candle to close...".upper())

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


if __name__ == "__main__":
    try:
        event_handler = CsvChangeHandler()
        observer = Observer()
        observer.schedule(event_handler, base_path, recursive=False)  # CSV folder path
        observer.start()
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
