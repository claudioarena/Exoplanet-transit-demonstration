# TO RUN: python main.py --ip 0.0.0.0 --port 8000

import argparse
import webserver

debug = False
measure_masked = True

# check to see if this is the main thread of execution
if __name__ == '__main__':
    # construct the argument parser and parse command line arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--ip", type=str, default='0.0.0.0', help="Ip address of the device")
    ap.add_argument("-o", "--port", type=int, default='8000', help="Port number of the server (1024 to 65535)")
    args = vars(ap.parse_args())

    # start the flask webserver
    webserver.start_server(host=args["ip"], port=args["port"], measure_masked=measure_masked, debug=debug)
