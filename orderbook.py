class OrderBook:

    def __init__(self, depth=5) -> None:
        self.bids = {}
        self.asks = {}
        self.depth = depth

    def add_order(self, price, size, side):
        book = self.bids if side == "buy" else self.asks
        if price in book:
            book[price] += size
        else: book[price] = size

        self.match_orders()

    def remove_order(self, price, size, side):
        book = self.bids if side == "buy" else self.asks
        if price in book:
            book[price] -= size
            if book[price] <= 0: del book[price]
    
    def match_orders(self):

        while self.bids and self.asks:
            highest_bid = max(self.bids)
            lowest_ask = min(self.asks)

            if highest_bid >= lowest_ask:
                size = min(self.bids[highest_bid], self.asks[lowest_ask])

                self.bids[highest_bid] -= size
                self.asks[lowest_ask] -= size

                if self.bids[highest_bid] <= 0: del self.bids[highest_bid]
                if self.asks[lowest_ask] <= 0: del self.asks[lowest_ask]

            else: break

    def get_order_book(self):

        sorted_bids = sorted(self.bids.items(), key=lambda x: -x[0])[:self.depth]
        sorted_asks = sorted(self.asks.items())[:self.depth]

        return {
            "bids" : sorted_bids,
            "asks" : sorted_asks
        }