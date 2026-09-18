import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

def get(url):
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

def post(url, data):
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

print("1. Checking /health ...")
h = get("http://127.0.0.1:8000/health")
print("  Status:", h)

print("\n2. Checking /api/v1/analytics/overview ...")
a = get("http://127.0.0.1:8000/api/v1/analytics/overview")
rev = a.get("total_revenue")
orders_count = a.get("total_orders")
hot_leads = a.get("hot_leads")
print(f"  Total Revenue: Rs {rev}, Total Orders: {orders_count}, Hot Leads: {hot_leads}")

print("\n3. Checking /api/v1/products ...")
p = get("http://127.0.0.1:8000/api/v1/products")
print(f"  Retrieved {len(p)} products from database.")
print(f"  First product: {p[0]['name']} - Rs {p[0]['price']}")

print("\n4. Checking /api/v1/orders ...")
o = get("http://127.0.0.1:8000/api/v1/orders")
print(f"  Retrieved {len(o)} orders.")
print(f"  Latest order: #{o[0]['order_number']} - {o[0]['customer_name']} ({o[0]['status']}) - Rs {o[0]['total']}")

print("\n5. Verifying Telugu Sales Flow ...")
r1 = post("http://127.0.0.1:8000/api/v1/simulator/message", {
    "channel": "INSTAGRAM",
    "customer_name": "Supabase Test Customer",
    "customer_phone": "+919988112233",
    "message": "Anna red saree undha?"
})
print("  Inquiry Reply:", r1["ai_response"]["content"].splitlines()[0])
print("  Image URL:", r1["ai_response"]["media_url"])

r2 = post("http://127.0.0.1:8000/api/v1/simulator/message", {
    "channel": "INSTAGRAM",
    "customer_name": "Supabase Test Customer",
    "customer_phone": "+919988112233",
    "message": "Delivery Miyapur?"
})
print("  Delivery Reply:", r2["ai_response"]["content"])

r3 = post("http://127.0.0.1:8000/api/v1/simulator/message", {
    "channel": "INSTAGRAM",
    "customer_name": "Supabase Test Customer",
    "customer_phone": "+919988112233",
    "message": "Okay book it. Flat 304, Miyapur, Hyderabad"
})
print("  Order Confirmation:", r3["ai_response"]["content"].splitlines()[0])
for line in r3["ai_response"]["content"].splitlines()[2:]:
    if "Order #" in line or "Total" in line:
        print(" ", line)
