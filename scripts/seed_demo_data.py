import asyncio
import sys
import os

# Add backend directory to sys.path so we can import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from sqlalchemy import select
from app.database.session import AsyncSessionLocal, engine
from app.models.base import Base
from app.models.models import (
    User, Business, BusinessMember, BusinessSettings, AISettings,
    ProductCategory, Product, ProductImage, DeliveryZone, Customer,
    Conversation, Message, Lead, Order, OrderItem
)
from app.models.enums import (
    RoleEnum, ConversationStatus, MessageSenderType, LeadStatus, OrderStatus,
    PaymentStatus, ChannelEnum, CustomerSource
)
from app.core.security import get_password_hash

DEMO_PRODUCTS = [
    {
        "name": "Crimson Kanjeevaram Silk Saree",
        "description": "Authentic crimson red pure silk saree with pure zari border and intricate peacock motifs. Perfect for weddings and festivals.",
        "price": 1299.0,
        "compare_at": 1899.0,
        "sku": "RF-KAN-001",
        "stock": 15,
        "color": "Red",
        "category": "Silk Sarees",
        "image": "https://images.unsplash.com/photo-1610030469983-98e550d6193c?auto=format&fit=crop&w=800&q=80"
    },
    {
        "name": "Royal Emerald Green Banarasi Saree",
        "description": "Exquisite emerald green Banarasi silk saree with gold floral jaal work and rich pallu.",
        "price": 1499.0,
        "compare_at": 2199.0,
        "sku": "RF-BAN-002",
        "stock": 10,
        "color": "Green",
        "category": "Silk Sarees",
        "image": "https://images.unsplash.com/photo-1617627143750-d86bc21e42bb?auto=format&fit=crop&w=800&q=80"
    },
    {
        "name": "Peacock Blue Gadwal Saree",
        "description": "Traditional Gadwal cotton-silk body with contrasting pure silk temple borders in vibrant peacock blue.",
        "price": 1399.0,
        "compare_at": 1799.0,
        "sku": "RF-GAD-003",
        "stock": 12,
        "color": "Blue",
        "category": "Silk Sarees",
        "image": "https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?auto=format&fit=crop&w=800&q=80"
    },
    {
        "name": "Pochampally Ikkat Black & Red Saree",
        "description": "Handwoven geometric Pochampally Ikkat pure cotton saree from Telangana weavers.",
        "price": 999.0,
        "compare_at": 1499.0,
        "sku": "RF-IKK-004",
        "stock": 25,
        "color": "Black",
        "category": "Handloom Sarees",
        "image": "https://images.unsplash.com/photo-1609357605129-26f69add5d6e?auto=format&fit=crop&w=800&q=80"
    },
    {
        "name": "Mangalagiri Mustard Cotton Saree",
        "description": "Breathable pure Mangalagiri cotton saree with zari Nizam border and solid body.",
        "price": 850.0,
        "compare_at": 1199.0,
        "sku": "RF-MAN-005",
        "stock": 30,
        "color": "Yellow",
        "category": "Cotton Sarees",
        "image": "https://images.unsplash.com/photo-1610030469854-c9f77f3747eb?auto=format&fit=crop&w=800&q=80"
    },
    {
        "name": "Pastel Pink Chanderi Saree",
        "description": "Delicate lightweight Chanderi saree with silver zari butis and running blouse piece.",
        "price": 1199.0,
        "compare_at": 1650.0,
        "sku": "RF-CHA-006",
        "stock": 14,
        "color": "Pink",
        "category": "Party Wear",
        "image": "https://images.unsplash.com/photo-1605296867304-46d5465a13f1?auto=format&fit=crop&w=800&q=80"
    },
    {
        "name": "Golden Yellow Uppada Pattu Saree",
        "description": "Pure Jamdani Uppada silk saree renowned for lightweight drape and pure gold tissue highlights.",
        "price": 2499.0,
        "compare_at": 3299.0,
        "sku": "RF-UPP-007",
        "stock": 8,
        "color": "Yellow",
        "category": "Silk Sarees",
        "image": "https://images.unsplash.com/photo-1610030469668-932d0941910c?auto=format&fit=crop&w=800&q=80"
    },
    {
        "name": "Midnight Maroon Velvet Designer Saree",
        "description": "Opulent velvet and georgette combination party wear saree with embroidered scalloped border.",
        "price": 1799.0,
        "compare_at": 2599.0,
        "sku": "RF-VEL-008",
        "stock": 9,
        "color": "Maroon",
        "category": "Party Wear",
        "image": "https://images.unsplash.com/photo-1610030469983-98e550d6193c?auto=format&fit=crop&w=800&q=80"
    },
    {
        "name": "Kalamkari Handprinted Saree",
        "description": "Natural dye organic cotton Srikalahasti Kalamkari painted mythological artwork saree.",
        "price": 1450.0,
        "compare_at": 1999.0,
        "sku": "RF-KAL-009",
        "stock": 18,
        "color": "Beige",
        "category": "Handloom Sarees",
        "image": "https://images.unsplash.com/photo-1617627143750-d86bc21e42bb?auto=format&fit=crop&w=800&q=80"
    },
    {
        "name": "Venkatagiri Pure Zari Saree",
        "description": "Fine count cotton-silk Venkatagiri saree from Nellore district with pure silver and gold zari work.",
        "price": 1899.0,
        "compare_at": 2400.0,
        "sku": "RF-VEN-010",
        "stock": 7,
        "color": "Orange",
        "category": "Silk Sarees",
        "image": "https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?auto=format&fit=crop&w=800&q=80"
    },
    {
        "name": "Lavender Organza Floral Saree",
        "description": "Sheer glass organza saree featuring hand-painted lavender blooms and delicate pearl piping.",
        "price": 1599.0,
        "compare_at": 2199.0,
        "sku": "RF-ORG-011",
        "stock": 11,
        "color": "Purple",
        "category": "Party Wear",
        "image": "https://images.unsplash.com/photo-1609357605129-26f69add5d6e?auto=format&fit=crop&w=800&q=80"
    },
    {
        "name": "Narayanpet Handloom Cotton Saree",
        "description": "Checked Narayanpet handloom cotton saree with vibrant contrast borders and temple motifs.",
        "price": 799.0,
        "compare_at": 1099.0,
        "sku": "RF-NAR-012",
        "stock": 35,
        "color": "Green",
        "category": "Cotton Sarees",
        "image": "https://images.unsplash.com/photo-1610030469854-c9f77f3747eb?auto=format&fit=crop&w=800&q=80"
    },
    {
        "name": "Dharmavaram Bridal Silk Saree",
        "description": "Heavy bridal brocade saree with contrast double-shade pallu and embossed motifs.",
        "price": 2899.0,
        "compare_at": 3999.0,
        "sku": "RF-DHA-013",
        "stock": 6,
        "color": "Red",
        "category": "Bridal Wear",
        "image": "https://images.unsplash.com/photo-1605296867304-46d5465a13f1?auto=format&fit=crop&w=800&q=80"
    },
    {
        "name": "Mulmul Soft Dailywear Saree",
        "description": "Feather-light Jaipur block print pure mulmul cotton saree for daily all-day comfort.",
        "price": 699.0,
        "compare_at": 999.0,
        "sku": "RF-MUL-014",
        "stock": 40,
        "color": "Indigo",
        "category": "Cotton Sarees",
        "image": "https://images.unsplash.com/photo-1610030469668-932d0941910c?auto=format&fit=crop&w=800&q=80"
    },
    {
        "name": "Teal Blue Georgette Sequin Saree",
        "description": "Glamorous party wear georgette saree embellished with tone-on-tone micro sequins.",
        "price": 1699.0,
        "compare_at": 2399.0,
        "sku": "RF-SEQ-015",
        "stock": 13,
        "color": "Teal",
        "category": "Party Wear",
        "image": "https://images.unsplash.com/photo-1610030469983-98e550d6193c?auto=format&fit=crop&w=800&q=80"
    },
    {
        "name": "Chettinad Cotton Earthy Saree",
        "description": "Traditional Tamil Nadu Chettinad thick weave cotton saree in earthy terracotta checks.",
        "price": 899.0,
        "compare_at": 1250.0,
        "sku": "RF-CHE-016",
        "stock": 20,
        "color": "Brown",
        "category": "Cotton Sarees",
        "image": "https://images.unsplash.com/photo-1617627143750-d86bc21e42bb?auto=format&fit=crop&w=800&q=80"
    },
    {
        "name": "Paithani Peacock Pallu Saree",
        "description": "Maharashtra heritage Paithani silk saree with vibrant kaleidoscopic peacock woven pallu.",
        "price": 2799.0,
        "compare_at": 3800.0,
        "sku": "RF-PAI-017",
        "stock": 5,
        "color": "Purple",
        "category": "Bridal Wear",
        "image": "https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?auto=format&fit=crop&w=800&q=80"
    },
    {
        "name": "Ajrakh Modal Silk Saree",
        "description": "Eco-friendly modal silk saree with traditional Kutch indigo and madder red hand block printing.",
        "price": 1499.0,
        "compare_at": 1999.0,
        "sku": "RF-AJR-018",
        "stock": 16,
        "color": "Navy",
        "category": "Handloom Sarees",
        "image": "https://images.unsplash.com/photo-1609357605129-26f69add5d6e?auto=format&fit=crop&w=800&q=80"
    },
    {
        "name": "Crimson Wedding Trousseau Pattu Saree",
        "description": "Grand bridal silk saree featuring temple border, floral brocade body, and heavy bridal pallu.",
        "price": 3199.0,
        "compare_at": 4500.0,
        "sku": "RF-BRI-019",
        "stock": 4,
        "color": "Red",
        "category": "Bridal Wear",
        "image": "https://images.unsplash.com/photo-1610030469854-c9f77f3747eb?auto=format&fit=crop&w=800&q=80"
    },
    {
        "name": "Linen Silver Zari Striped Saree",
        "description": "Pure 100-count organic linen saree in pristine mint green with subtle silver zari horizontal stripes.",
        "price": 1350.0,
        "compare_at": 1750.0,
        "sku": "RF-LIN-020",
        "stock": 22,
        "color": "Mint Green",
        "category": "Handloom Sarees",
        "image": "https://images.unsplash.com/photo-1605296867304-46d5465a13f1?auto=format&fit=crop&w=800&q=80"
    }
]

DELIVERY_ZONES = [
    {"locality": "Miyapur", "fee": 50.0, "pincode": "500049"},
    {"locality": "Kukatpally", "fee": 50.0, "pincode": "500072"},
    {"locality": "Gachibowli", "fee": 70.0, "pincode": "500032"},
    {"locality": "Banjara Hills", "fee": 80.0, "pincode": "500034"},
    {"locality": "Secunderabad", "fee": 60.0, "pincode": "500003"}
]

DEMO_CUSTOMERS = [
    {"name": "Sneha Reddy", "phone": "+919876543210", "email": "sneha.reddy@gmail.com", "lang": "Telugu", "src": "INSTAGRAM"},
    {"name": "Priyanka Rao", "phone": "+919876543211", "email": "priyanka.rao@gmail.com", "lang": "Telugu", "src": "WHATSAPP"},
    {"name": "Ananya Sharma", "phone": "+919876543212", "email": "ananya.sharma@yahoo.com", "lang": "Hindi", "src": "INSTAGRAM"},
    {"name": "Kavitha Murthy", "phone": "+919876543213", "email": "kavitha.m@outlook.com", "lang": "English", "src": "WHATSAPP"},
    {"name": "Lavanya Goud", "phone": "+919876543214", "email": "lavanya.g@gmail.com", "lang": "Telugu", "src": "INSTAGRAM"},
    {"name": "Sunita Verma", "phone": "+919876543215", "email": "sunita.v@gmail.com", "lang": "Hindi", "src": "WHATSAPP"},
    {"name": "Divya Teja", "phone": "+919876543216", "email": "divya.t@gmail.com", "lang": "Telugu", "src": "INSTAGRAM"},
    {"name": "Meera Nair", "phone": "+919876543217", "email": "meera.nair@gmail.com", "lang": "English", "src": "WHATSAPP"},
    {"name": "Aparna Chowdary", "phone": "+919876543218", "email": "aparna.c@gmail.com", "lang": "Telugu", "src": "INSTAGRAM"},
    {"name": "Pooja Agarwal", "phone": "+919876543219", "email": "pooja.ag@gmail.com", "lang": "Hindi", "src": "WHATSAPP"}
]

async def seed_data():
    print("Beginning seed of Rani Fashions...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        # 1. Create Demo User
        u_res = await db.execute(select(User).where(User.email == "demo@reachoutsmb.com"))
        user = u_res.scalar_one_or_none()
        if not user:
            user = User(
                email="demo@reachoutsmb.com",
                full_name="Raghu - Rani Fashions",
                hashed_password=get_password_hash("password123"),
                is_active=True
            )
            db.add(user)
            await db.flush()
            print(f"Created demo user: {user.email}")

        # 2. Create Business: Rani Fashions
        b_res = await db.execute(select(Business).where(Business.slug == "rani-fashions"))
        business = b_res.scalar_one_or_none()
        if not business:
            business = Business(
                name="Rani Fashions",
                slug="rani-fashions",
                business_type="Fashion / Sarees & Ethnic Wear",
                location="Hyderabad, Telangana",
                city="Hyderabad",
                currency="INR",
                languages=["Telugu", "English", "Hindi"],
                description="Authentic South Indian handloom, Kanjeevaram, Banarasi & designer sarees at fair prices.",
                return_policy="7-day easy exchange for unstitched sarees with original tags.",
                active=True
            )
            db.add(business)
            await db.flush()

            # Membership
            member = BusinessMember(
                business_id=business.id,
                user_id=user.id,
                role=RoleEnum.OWNER.value
            )
            db.add(member)

            # Business Settings
            settings = BusinessSettings(
                business_id=business.id,
                store_timings="Mon-Sat: 10:00 AM - 9:00 PM, Sun: 11:00 AM - 7:00 PM",
                contact_phone="+919876543210",
                contact_email="care@ranifashions.com",
                payment_methods=["UPI", "Cash on Delivery", "Cards"],
                delivery_regions=["Hyderabad Metro", "Telangana", "All India"]
            )
            db.add(settings)

            # AI Settings
            ai_settings = AISettings(
                business_id=business.id,
                enabled=True,
                model_name="gemini-2.5-flash",
                default_language="Telugu",
                escalation_keywords=["human", "agent", "manager", "complaint", "fraud", "police"]
            )
            db.add(ai_settings)
            print("Created Rani Fashions business profile.")

        # 3. Delivery Zones
        for z in DELIVERY_ZONES:
            existing_z = await db.execute(
                select(DeliveryZone).where(
                    DeliveryZone.business_id == business.id,
                    DeliveryZone.locality == z["locality"]
                )
            )
            if not existing_z.scalar_one_or_none():
                db.add(DeliveryZone(
                    business_id=business.id,
                    city="Hyderabad",
                    locality=z["locality"],
                    pincode=z["pincode"],
                    delivery_fee=z["fee"],
                    minimum_order=0.0,
                    estimated_delivery="Same Day / Next Day",
                    active=True
                ))
        print("Created 5 delivery zones.")

        # 4. Categories & Products
        category_map = {}
        category_names = ["Silk Sarees", "Handloom Sarees", "Cotton Sarees", "Party Wear", "Bridal Wear"]
        for cname in category_names:
            c_slug = cname.lower().replace(" ", "-")
            c_res = await db.execute(
                select(ProductCategory).where(
                    ProductCategory.business_id == business.id,
                    ProductCategory.slug == c_slug
                )
            )
            cat = c_res.scalar_one_or_none()
            if not cat:
                cat = ProductCategory(
                    business_id=business.id,
                    name=cname,
                    slug=c_slug,
                    description=f"Curated collection of {cname}"
                )
                db.add(cat)
                await db.flush()
            category_map[cname] = cat.id

        created_products = []
        for p_data in DEMO_PRODUCTS:
            p_res = await db.execute(
                select(Product).where(Product.business_id == business.id, Product.sku == p_data["sku"])
            )
            prod = p_res.scalar_one_or_none()
            if not prod:
                cat_id = category_map.get(p_data["category"])
                prod = Product(
                    business_id=business.id,
                    category_id=cat_id,
                    name=p_data["name"],
                    description=p_data["description"],
                    price=p_data["price"],
                    compare_at_price=p_data["compare_at"],
                    sku=p_data["sku"],
                    stock=p_data["stock"],
                    color=p_data["color"],
                    active=True,
                    tags=["saree", p_data["color"].lower(), p_data["category"].lower()]
                )
                db.add(prod)
                await db.flush()

                # Add primary image
                img = ProductImage(
                    product_id=prod.id,
                    image_url=p_data["image"],
                    alt_text=prod.name,
                    is_primary=True,
                    sort_order=0
                )
                db.add(img)
            created_products.append(prod)
        print(f"Created/verified {len(DEMO_PRODUCTS)} products.")

        # 5. Customers
        customer_objs = []
        for c in DEMO_CUSTOMERS:
            cust_res = await db.execute(
                select(Customer).where(Customer.business_id == business.id, Customer.phone == c["phone"])
            )
            cust = cust_res.scalar_one_or_none()
            if not cust:
                cust = Customer(
                    business_id=business.id,
                    name=c["name"],
                    phone=c["phone"],
                    email=c["email"],
                    preferred_language=c["lang"],
                    source=c["src"],
                    tags=["demo-customer", c["lang"].lower()],
                    order_count=0,
                    total_spending=0.0
                )
                db.add(cust)
                await db.flush()
            customer_objs.append(cust)
        print("Created/verified 10 customers.")

        # 6. Conversations & Messages
        for idx, cust in enumerate(customer_objs):
            conv_res = await db.execute(
                select(Conversation).where(
                    Conversation.business_id == business.id,
                    Conversation.customer_id == cust.id
                )
            )
            conv = conv_res.scalar_one_or_none()
            channel = cust.source
            if not conv:
                conv = Conversation(
                    business_id=business.id,
                    customer_id=cust.id,
                    channel=channel,
                    status=ConversationStatus.AI_HANDLING.value if idx != 2 else ConversationStatus.HUMAN_REQUIRED.value,
                    is_ai_handled=(idx != 2),
                    handoff_reason="Customer requested human agent" if idx == 2 else None
                )
                db.add(conv)
                await db.flush()

                # Add initial sample messages
                if cust.preferred_language == "Telugu":
                    msg1 = Message(
                        conversation_id=conv.id,
                        sender_type=MessageSenderType.CUSTOMER.value,
                        sender_id=cust.phone,
                        channel=channel,
                        content="Anna red saree undha?"
                    )
                    msg2 = Message(
                        conversation_id=conv.id,
                        sender_type=MessageSenderType.AI.value,
                        channel=channel,
                        content="ఉందండి 😊 మా దగ్గర అందమైన Crimson Kanjeevaram Silk Saree స్టాక్ లో ఉంది! ధర: ₹1,299.",
                        media_url="https://images.unsplash.com/photo-1610030469983-98e550d6193c?auto=format&fit=crop&w=800&q=80",
                        media_type="image/jpeg"
                    )
                elif cust.preferred_language == "Hindi":
                    msg1 = Message(
                        conversation_id=conv.id,
                        sender_type=MessageSenderType.CUSTOMER.value,
                        sender_id=cust.phone,
                        channel=channel,
                        content="Namaste, Banarasi saree dikhao please."
                    )
                    msg2 = Message(
                        conversation_id=conv.id,
                        sender_type=MessageSenderType.AI.value,
                        channel=channel,
                        content="नमस्ते जी 😊 हमारे पास Royal Emerald Green Banarasi Saree उपलब्ध है। कीमत: ₹1,499.",
                        media_url="https://images.unsplash.com/photo-1617627143750-d86bc21e42bb?auto=format&fit=crop&w=800&q=80",
                        media_type="image/jpeg"
                    )
                else:
                    msg1 = Message(
                        conversation_id=conv.id,
                        sender_type=MessageSenderType.CUSTOMER.value,
                        sender_id=cust.phone,
                        channel=channel,
                        content="Hi! Do you have silk sarees under 1500?"
                    )
                    msg2 = Message(
                        conversation_id=conv.id,
                        sender_type=MessageSenderType.AI.value,
                        channel=channel,
                        content="Hello! Yes, we have gorgeous Crimson Kanjeevaram & Gadwal silk sarees starting from ₹1,299.",
                        media_url="https://images.unsplash.com/photo-1610030469983-98e550d6193c?auto=format&fit=crop&w=800&q=80",
                        media_type="image/jpeg"
                    )
                db.add(msg1)
                db.add(msg2)

        # 7. Leads (10 leads)
        for idx, cust in enumerate(customer_objs):
            existing_lead = await db.execute(
                select(Lead).where(Lead.business_id == business.id, Lead.customer_id == cust.id)
            )
            if not existing_lead.scalar_one_or_none():
                lead_status = LeadStatus.HOT.value if idx < 4 else (LeadStatus.WARM.value if idx < 8 else LeadStatus.CONVERTED.value)
                score = 90 if idx < 4 else (65 if idx < 8 else 100)
                lead = Lead(
                    business_id=business.id,
                    customer_id=cust.id,
                    product_interest="Kanjeevaram & Banarasi Sarees",
                    budget=1500.0,
                    purchase_intent="HIGH" if idx < 6 else "MEDIUM",
                    score=score,
                    status=lead_status,
                    notes=f"Inquired via {cust.source} for wedding occasion."
                )
                db.add(lead)
        print("Created 10 leads with scoring.")

        # 8. Orders (8 orders)
        for idx in range(8):
            ord_num = f"RO-20260917-100{idx+1}"
            ord_check = await db.execute(select(Order).where(Order.order_number == ord_num))
            if not ord_check.scalar_one_or_none():
                cust = customer_objs[idx]
                prod = created_products[idx % len(created_products)]
                delivery_fee = 50.0
                total = prod.price + delivery_fee
                status_val = OrderStatus.CONFIRMED.value if idx < 3 else (OrderStatus.SHIPPED.value if idx < 6 else OrderStatus.DELIVERED.value)

                order = Order(
                    business_id=business.id,
                    customer_id=cust.id,
                    order_number=ord_num,
                    status=status_val,
                    subtotal=prod.price,
                    delivery_fee=delivery_fee,
                    discount=0.0,
                    total=total,
                    delivery_address=f"Flat {200+idx}, Sri Sai Residency, Miyapur, Hyderabad - 500049",
                    payment_status=PaymentStatus.PAID.value if status_val == OrderStatus.DELIVERED.value else PaymentStatus.PENDING.value
                )
                db.add(order)
                await db.flush()

                order_item = OrderItem(
                    order_id=order.id,
                    product_id=prod.id,
                    product_name=prod.name,
                    unit_price=prod.price,
                    quantity=1,
                    total_price=prod.price
                )
                db.add(order_item)

                cust.order_count += 1
                cust.total_spending += total
        print("Created 8 orders with line items.")

        await db.commit()
        print("Demo seed for Rani Fashions finished successfully!")

if __name__ == "__main__":
    asyncio.run(seed_data())
