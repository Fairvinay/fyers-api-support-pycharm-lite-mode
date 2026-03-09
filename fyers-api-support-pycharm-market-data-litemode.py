from fyers_apiv3.FyersWebsocket import data_ws

user_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcHBfaWQiOiJUUkxWMkE2R1BMIiwidXVpZCI6ImZiYjE2MTUxMWEyNzQyYzFiOWFiMzBkM2VmYTM0MjA3IiwiaXBBZGRyIjoiIiwibm9uY2UiOiIiLCJzY29wZSI6IiIsImRpc3BsYXlfbmFtZSI6IlhWMzEzNjAiLCJvbXMiOiJLMSIsImhzbV9rZXkiOiIwMmNjNTVmZmRkM2IzODZhNTg4NGY4Zjg3N2E3Y2Y5YjJjYTc5N2U0MWEzNjk4YWJkZmRhY2ExZCIsImlzRGRwaUVuYWJsZWQiOiJOIiwiaXNNdGZFbmFibGVkIjoiTiIsImF1ZCI6IltcImQ6MVwiLFwiZDoyXCIsXCJ4OjBcIixcIng6MVwiLFwieDoyXCJdIiwiZXhwIjoxNzU2OTk5NTk0LCJpYXQiOjE3NTY5Njk1OTQsImlzcyI6ImFwaS5sb2dpbi5meWVycy5pbiIsIm5iZiI6MTc1Njk2OTU5NCwic3ViIjoiYXV0aF9jb2RlIn0.XfPOp4Fix7oofRSHLy3IQiwP0WZX29oICk14ISjWvWw"


def onmessage(message):
    """
    Callback function to handle incoming messages from the FyersDataSocket WebSocket.
    Parameters:
    message (dict): The received message from the WebSocket.
    """
    print("Response:", message)
def onerror(message):
    """
    Callback function to handle WebSocket errors.
    Parameters:
    message (dict): The error message received from the WebSocket.
    """
    print("Error:", message)
def onclose(message):
    """
    Callback function to handle WebSocket connection close events.
    """
    print("Connection closed:", message)
def onopen():
    """
    Callback function to subscribe to data type and symbols upon WebSocket connection.
    """
    # Specify the data type and symbols you want to subscribe to
data_type = "SymbolUpdate"
    # Subscribe to the specified symbols and data type
symbols = ['NSE:NIFTY2590924900PE', 'NSE:NIFTY50-INDEX', 'NSE:NIFTY2590924900CE', 'NSE:NIFTY2590925000PE', 'NSE:NIFTY2590925000CE']
    # Create a FyersDataSocket instance with the provided parameters
fyers = data_ws.FyersDataSocket(
    access_token=user_token, # Access token in the format "appid:accesstoken"
    log_path="", # Path to save logs. Leave empty to auto-create logs in the current directory.
    litemode=True, # Lite mode disabled. Set to True if you want a lite response.
    write_to_file=False, # Save response in a log file instead of printing it.
    reconnect=True, # Enable auto-reconnection to WebSocket on disconnection.
    on_connect=onopen, # Callback function to subscribe to data upon connection.
    on_close=onclose, # Callback function to handle WebSocket connection close events.
    on_error=onerror, # Callback function to handle WebSocket errors.
    on_message=onmessage # Callback function to handle incoming messages from the WebSocket.
    )
fyers.subscribe(symbols=symbols, data_type=data_type)
    # Keep the socket running to receive real-time data
fyers.keep_running()
    # Replace the sample access token with your actual access token obtained from Fyers
access_token = user_token

# Establish a connection to the Fyers WebSocket
fyers.connect()