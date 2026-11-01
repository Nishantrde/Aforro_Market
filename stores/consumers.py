from channels.generic.websocket import AsyncJsonWebsocketConsumer

class StockConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("stock", self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        # TODO: group_discard, same arguments as group_add
        await self.channel_layer.group_discard("stock", self.channel_layer)
                

    async def stock_update(self, event):
        # runs when someone sends {"type": "stock.update", ...} to the group
        await self.send_json({"store_id": event["store_id"], "product_id": event["product_id"], "stock": event["stock"]})