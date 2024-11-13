from quart import Quart, websocket, send_file
import asyncio
import json
import logging
import orderbook

app = Quart(__name__)
order_book = orderbook.OrderBook()
connected_clients = set()
logging.basicConfig(level=logging.INFO)

MAX_CONNECTIONS = 100

@app.route("/")
async def index():
    return await send_file("templates/index.html")

@app.websocket("/ws")
async def ws():
    if len(connected_clients) > MAX_CONNECTIONS:
        await websocket.send(json.dumps({"error" : "Max Connections"}))
        return
    
    client = websocket._get_current_object()
    connected_clients.add(client)
    logging.info("client connected")

    try:
        await client.send(json.dumps(order_book.get_order_book()))

        while True:
            data = await websocket.receive()
            try:
                order_data = json.loads(data)

                action = order_data.get("action")
                price = order_data.get("price")
                size = order_data.get("size")
                side = order_data.get("side")

                if action == "add": order_book.add_order(price, size, side)
                elif action ==  "remove": order_book.remove_order(price, size, side)
                else: 
                    await websocket.send(json.dumps({"error" : "Unsupported action"}))
                    continue

                await broadcast_order_book()

            except json.JSONDecodeError:
                logging.info("JSON load Error")
                await websocket.send(json.dumps({"error" : "JSON load Error"}))


    finally:
        connected_clients.remove(client)
        logging.info("client disconnected")

async def broadcast_order_book():
    order_book_data = order_book.get_order_book()
    message = json.dumps(order_book_data)
    await asyncio.gather(*(client.send(message) for client in connected_clients))

async def periodic_broadcast(interval=0.1):
    while True:
        await broadcast_order_book()
        asyncio.sleep(interval)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(periodic_broadcast())
    app.run(port=5000)
