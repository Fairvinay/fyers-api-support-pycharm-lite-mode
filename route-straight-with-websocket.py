from fyers_apiv3.FyersWebsocket import data_ws
from fyers_apiv3 import fyersModel as fyersV3
from flask import Flask, request, redirect, render_template ,  Response, render_template_string
from flask_cors import CORS
from flask import jsonify
from multiprocessing import Process
import requests
import threading
from threading import Thread
import webbrowser
import time , os , json
import sys , queue
import random   # <-- add this


# === Configuration ===
client_id = os.environ.get("client_id", "TRLV2A6GPL-100")
secret_key = os.environ.get("secret_key", "V72MPISUJC")
redirec_base_url = os.environ.get("redirec_base_url", "https://192.168.1.7:8888")
#redirect_uri = "https://192.168.1.4:8888/.netlify/functions/netlifystockfyersbridge/api/fyersauthcodeverify"
redirect_uri = redirec_base_url.rstrip("/") +"/.netlify/functions/netlifystockfyersbridge/api/fyersauthcodeverify"
response_type = "code"
grant_type = "authorization_code"
state = "python_test"

auth_code_received = None
flask_process = None  # Will store reference to the running Process


# Store the token globally after login
global_access_token = None
# Store the sessoni globally after login
global_session = None
# === Step 1: Flask server to receive auth_code ===
app = Flask(__name__)
cors_url = redirec_base_url.rstrip("/")
CORS(app, supports_credentials=True, resources={r"/stream*": {"origins": cors_url}})

# Read env variable and parse into list
allowed_origins = os.environ.get("ALLOWED_ORIGINS", "")
ALLOWED_ORIGINS = [origin.strip() for origin in allowed_origins.split(",") if origin.strip()]

if ALLOWED_ORIGINS:  # checks list is not empty
    print("Allowed origins found:", ALLOWED_ORIGINS)
else:
    ALLOWED_ORIGINS = [
        "https://successrate.netlify.app",
        "https://fyersbook.netlify.app",
        "https://onedinaar.com",
        "https://192.168.1.7:8888",
    ]
    print("Allowed origins configured from hard code")

headers	 = {
            "Content-Type": "text/event-stream",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": redirec_base_url.rstrip("/"),
            "Access-Control-Allow-Credentials": "true"
           }

class Queue:
    this_self=None
    def __init__(self):
        self.l = []
        self.cond = threading.Condition()

    def get(self):
        with self.cond:
            while not self.l:
                self.cond.wait()
            ret = self.l[0]
            self.l = self.l[1:]
            return ret

    def put(self, x):
        with self.cond:
            self.l.append(x)
            self.cond.notify()

class CustomError(Exception):
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

# A queue to pass messages from websocket thread to SSE stream queue.Queue()
# https://peps.python.org/pep-0583/
message_queue =  Queue()

# ---------------------
# Worker 1: Producer
# ---------------------
def worker1():
    while True:
        obj = {
            "ltp": round(random.uniform(30, 200), 2),  # random price
            "symbol": f"NSE:NIFTY{2591625050}{random.choice(['CE','PE'])}",  # random symbol random.randint(25000, 26000)
            "type": "sf"
        }
        message_queue.put(f"data: {json.dumps(obj)}\n\n")
        print(f"Produced: {obj}")
        time.sleep(1)  # produce every second

# ---------------------
# Worker 2: Consumer
# ---------------------
def worker2():
    while True:
        y = message_queue.get()
        print(f"Consumed: {y}")
        time.sleep(0.5)  # simulate processing delay


@app.errorhandler(CustomError)
def handle_custom_error(error):
    response = jsonify({"message": error.message})
    response.status_code = error.status_code
    return response

@app.errorhandler(Exception)
def handle_generic_exception(error):
    # Log the full traceback for debugging
    app.logger.exception("An unhandled exception occurred.")
    response = jsonify({"message": "An unexpected error occurred."})
    response.status_code = 500
    return response

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/raise_error')
def raise_error():
    raise CustomError("Something specific went wrong!", status_code=422)

@app.route("/login")
def login():
    global global_session
    session = fyersV3.SessionModel(
        client_id=client_id,
        secret_key=secret_key,
        redirect_uri=redirect_uri,
        response_type="code",
        state=state
    )
    auth_url = session.generate_authcode()
    # Store the token globally after login
    global_session = session
    print("auth_url:",auth_url)
    return redirect(auth_url)


@app.after_request
def add_cors_headers(response):
    origin = request.headers.get("Origin")
    if origin in ALLOWED_ORIGINS:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Vary"] = "Origin"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Allow-Credentials"] = "true"
    return response

# 3. Handle Fyers redirect + trigger WebSocket
@app.route('/redirect')
def callback():
    global global_access_token
    auth_code = request.args.get('auth_code')
    received_state = request.args.get("state")
    #session = global_session if global_session is not None else None

    if not auth_code:
        return "❌ Authorization failed", 400

    try:
        session = fyersV3.SessionModel(
            client_id=client_id,
            secret_key=secret_key,
            redirect_uri=redirect_uri,
            response_type="code",
            grant_type="authorization_code"
        )
        session.set_token(auth_code)
        response = session.generate_token()
        if "access_token" in response:
            global_access_token = response["access_token"]
            access_token = response["access_token"]
            # Save token for later use
            # with open("access_token.txt", "w") as f:
            #    f.write(access_token)

            order_variables = {
                "secret_value": global_access_token
            }
            # Pass dictionary by unpacking
            if received_state == "python_test":
                return render_template("market-feed.html", **order_variables)
            elif received_state == "python_order":
                return render_template("orders.html", **order_variables)
            elif received_state == "python_position":
                return render_template("orders-positions.html", **order_variables)
            """
            # Trigger WebSocket
            threading.Thread(target=start_websocket, args=(access_token,)).start()

            def event_stream():
                while True:
                    msg = message_queue.get()
                    if msg is None:
                        break
                    yield msg

            return Response(event_stream(), mimetype="text/event-stream", headers=headers)
            """
        else:
            return f"❌ Failed to generate token: {response}"

    except Exception as e:
        return f"❌ Error: {str(e)}", 500


@app.route("/stream")
def stream():
    access_token = request.args.get("accessToken")
    print("Received access_token...")
    # Option 1: If repeated params
    tickers = request.args.getlist("tickers")
    print("Tickers:", tickers)
    print("Access Token:", access_token)
    # Start background websocket thread
    #threading.Thread(target=start_websocket, args=(access_token,tickers)).start()

    # Consumer function
    #def consumer():
    def event_stream():
        while True:
            msg = message_queue.get()
            if msg is None:
              break
            yield msg

        """
                def event_stream():
                    while True:
                        yield f"data: hello at {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                        time.sleep(1)
        """
    #    return Response(event_stream(), mimetype="text/event-stream")

    try:


        #Create producer and consumer threads
        #producer_thread = threading.Thread(target=start_websocket, args=(access_token,tickers))
        #consumer_thread = threading.Thread(target=consumer)

        # Start the threads
        #producer_thread.start()
        #consumer_thread.start()

        # Wait for producer to finish, then signal consumer to stop
        #producer_thread.join()
        #message_queue.put(None)
        #consumer_thread.join()
        #start_websocket(access_token, tickers);
        #threading.Thread(target=start_websocket, args=(access_token, tickers)).start()
        # ---------------------
        # Start threads
        # ---------------------
        t1 = threading.Thread(target=worker1, daemon=True)
        t2 = threading.Thread(target=worker2, daemon=True)

        t1.start()
        t2.start()
        #consumer();
        #return Response(consumer(), mimetype="text/event-stream", headers=headers)
    except Exception as e:
        print(f"Caught exception: {type(e)}")
        print(f"Exception message: {e}")
        #handle_generic_exception(f"Exception message: {e}")

    """
    def event_stream():
        while True:
            msg = message_queue.get()
            if msg is None:
                break
            yield msg
    
    def event_stream():
        while True:
            yield f"data: hello at {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            time.sleep(1)
    
    return Response(event_stream(), mimetype="text/event-stream")
    """
    return Response(event_stream(), mimetype="text/event-stream")

# 4. WebSocket Connection Function


    #yield message_queue.get()

# 5. WebSocket Connection Function
# Consumer function
def consumer_old():
    def event_stream():
        while True:
            msg = message_queue.get()
            if msg is None:
                break
            yield msg

    """
    def event_stream():
        while True:
            yield f"data: hello at {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            time.sleep(1)
    """
    return Response(event_stream(), mimetype="text/event-stream")
def start_websocket(access_token_input, tickers):
    print("📡 Starting WebSocket with access_token...")

    def onmessage(message):
        """
        Callback function to handle incoming messages from the FyersDataSocket WebSocket.

        Parameters:
            message (dict): The received message from the WebSocket.

        """
        message_queue.put(f"data: {json.dumps(message)}\n\n")
        print("Response:", message)
        # return Response(f"data: {json.dumps(message)}\n\n", mimetype="text/event-stream")

    def onerror(message):
        """
        Callback function to handle WebSocket errors.

        Parameters:
            message (dict): The error message received from the WebSocket.


        """
        message_queue.put(f"data: {json.dumps(message)}\n\n")
        print("Error:", message)
        # return Response(f"data: {json.dumps(message)}\n\n", mimetype="text/event-stream")

    def onclose(message):
        """
        Callback function to handle WebSocket connection close events.
        """
        message_queue.put(f"data: {json.dumps(message)}\n\n")
        print("Connection closed:", message)
        # return Response(f"data: {json.dumps(message)}\n\n", mimetype="text/event-stream")

    def onopen():
        """
        Callback function to subscribe to data type and symbols upon WebSocket connection.

        """
        # Specify the data type and symbols you want to subscribe to
        data_type = "SymbolUpdate"

        # Subscribe to the specified symbols and data type
        # symbols = ['NSE:NIFTY2590924900PE', 'NSE:NIFTY50-INDEX', 'NSE:NIFTY2590924900CE', 'NSE:NIFTY2590925000PE',
        #           'NSE:NIFTY2590925000CE']
        # Validate: must be a list, non-empty, and all elements non-empty strings
        if isinstance(tickers, list) and len(tickers) > 0 and all(t.strip() for t in tickers):
            symbols = tickers
        else:
            # Default fallback
            symbols = [
                "BSE:SENSEX-INDEX",
                "NSE:NIFTY50-INDEX",
                "NSE:NIFTYBANK-INDEX"
            ]
        fyers.subscribe(symbols=symbols, data_type=data_type)
        ter = "connected"
        message_queue.put(f"data: {json.dumps(ter)}\n\n")
        # return Response(f"data: {json.dumps(ter)}\n\n", mimetype="text/event-stream")

    # Replace the sample access token with your actual access token obtained from Fyers
    access_token = access_token_input

    # Create a FyersDataSocket instance with the provided parameters
    fyers = data_ws.FyersDataSocket(
        access_token=access_token,  # Access token in the format "appid:accesstoken"
        log_path="",  # Path to save logs. Leave empty to auto-create logs in the current directory.
        litemode=True,  # Lite mode disabled. Set to True if you want a lite response.
        write_to_file=False,  # Save response in a log file instead of printing it.
        reconnect=True,  # Enable auto-reconnection to WebSocket on disconnection.
        on_connect=onopen,  # Callback function to subscribe to data upon connection.
        on_close=onclose,  # Callback function to handle WebSocket connection close events.
        on_error=onerror,  # Callback function to handle WebSocket errors.
        on_message=onmessage  # Callback function to handle incoming messages from the WebSocket.
    )

    # Keep the socket running to receive real-time data
    fyers.keep_running()

    # Establish a connection to the Fyers WebSocket
    fyers.connect()
def run_flask():
    port = int(os.environ.get("PORT", 9384))  # Render sets PORT env variable
    cert_file = os.path.join(os.path.dirname(__file__), "ssl.crt/server.crt")
    key_file = os.path.join(os.path.dirname(__file__), "ssl.key/server.key")
    app.run( port=port,debug=False, use_reloader=False,ssl_context=(cert_file, key_file))


#new running main
def main():
    #flask_thread = Thread(target=run_flask)
    #flask_thread.start()
    flask_process = Process(target=run_flask)
    flask_process.start()

    print("✅ Flask server started.")

if __name__ == '__main__':
    main()
