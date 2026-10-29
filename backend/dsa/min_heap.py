import heapq

class LowStockMinHeap:
    def __init__(self):
        self.heap = []  # Stores tuples of (quantity, sku, product_name)

    def add_or_update(self, sku: str, name: str, quantity: int, threshold: int = 10):
        # We only care about items at or below threshold
        if quantity <= threshold:
            # Remove existing if present to avoid duplicates
            self.remove(sku)
            heapq.heappush(self.heap, (quantity, sku, name))

    def remove(self, sku: str):
        self.heap = [(q, s, n) for q, s, n in self.heap if s != sku]
        heapq.heapify(self.heap)

    def get_low_stock_alerts(self, limit: int = 5) -> list:
        # Returns items sorted by lowest quantity first O(K log N)
        sorted_heap = sorted(self.heap)
        return [{"sku": s, "name": n, "quantity": q} for q, s, n in sorted_heap[:limit]]
