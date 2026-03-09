#how do we stop the asyncio python server

import asyncio
import json
import sys , queue
from fyers_apiv3.FyersWebsocket import data_ws
# A queue to pass messages from websocket thread to SSE stream
message_queue = queue.Queue()
acctoken = None
outgoing = asyncio.Queue()
tickers = ['NSE:NIFTY25O1425150CE']
async def run_server():
    task = asyncio.create_task(main())
    server = await asyncio.start_server(handle_client, 'localhost', 15555)
    async with server:
        try:
            await server.serve_forever()
        except asyncio.CancelledError:
            print("🛑 Server shutting down...")
            task.cancel()
            await task
async def handle_client(reader, writer):
     asyncio.create_task(handle_outgoing(writer, acctoken))
async def handle_outgoing(writer,access_token_input):
    while True:
         message = await outgoing.get()
         packet = json.dumps(message) + '\r\n'
         print("📡 Starting WebSocket with access_token...")

         def onmessage(message):
             """
              Callback function to handle incoming messages from the FyersDataSocket WebSocket.
              Parameters:
              message (dict): The received message from the WebSocket.
             """
             # return Response(f"data: {json.dumps(message)}\n\n", mimetype="text/event-stream")
             message_queue.put(f"data: {json.dumps(message)}\n\n")
             print("Response:", message)
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
            access_token=access_token_input,  # Access token in the format "appid:accesstoken"
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
         writer.write(packet.encode('utf-8'))
         await writer.drain()
async def main():
    # This is where you would do your main program logic
    while True:
        print('starting  asyncio server with fyers acess token ')