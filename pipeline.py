import sys
from modules import acquisition
import io

host = ''
mode = ''


def init_pipeline():
    print("Initializing Pipeline")

    if len(sys.argv) != 3:
        sys.exit("Illegal amount of arguments")

    global host
    host = sys.argv[1]
    global mode
    mode = sys.argv[2]

    print(f"Running pipeline with host {host} and mode {mode}")

    stream = acquisition.start_proxy(host)

    while True:
        s = stream.getvalue()
        if s != '':
            print(s)
            stream.flush()


if __name__ == '__main__':
    init_pipeline()
