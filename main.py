from collections import Counter

events = ["page_view", "add_to_cart", "page_view", "purchase",
          "page_view", "add_to_cart", "page_view"]


counts = Counter(events)


jan_events = Counter({"page_view": 100, "purchase": 20})
feb_events = Counter({"page_view": 150, "purchase": 15})


total = jan_events + feb_events

print(total)
