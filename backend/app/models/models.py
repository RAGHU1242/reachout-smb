from datetime import datetime
from typing import List, Optional
from sqlalchemy import (
    String, Text, Boolean, Integer, Float, ForeignKey, DateTime, Index, JSON
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin, generate_uuid, get_utc_now
from app.models.enums import (
    RoleEnum, ChannelEnum, ConversationStatus, MessageSenderType,
    LeadStatus, OrderStatus, PaymentStatus, FollowUpStatus, CustomerSource
)

# -------------------------------------------------------------
# User & Business Tenancy
# -------------------------------------------------------------

class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    business_memberships: Mapped[List["BusinessMember"]] = relationship(
        "BusinessMember", back_populates="user", cascade="all, delete-orphan"
    )

class Business(Base, TimestampMixin):
    __tablename__ = "businesses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    business_type: Mapped[str] = mapped_column(String(100), default="Retail / E-Commerce")
    location: Mapped[str] = mapped_column(String(255), default="Hyderabad, India")
    city: Mapped[str] = mapped_column(String(100), default="Hyderabad")
    currency: Mapped[str] = mapped_column(String(10), default="INR")
    languages: Mapped[List[str]] = mapped_column(JSON, default=lambda: ["Telugu", "English", "Hindi"])
    return_policy: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    members: Mapped[List["BusinessMember"]] = relationship(
        "BusinessMember", back_populates="business", cascade="all, delete-orphan"
    )
    products: Mapped[List["Product"]] = relationship(
        "Product", back_populates="business", cascade="all, delete-orphan"
    )
    categories: Mapped[List["ProductCategory"]] = relationship(
        "ProductCategory", back_populates="business", cascade="all, delete-orphan"
    )
    customers: Mapped[List["Customer"]] = relationship(
        "Customer", back_populates="business", cascade="all, delete-orphan"
    )
    conversations: Mapped[List["Conversation"]] = relationship(
        "Conversation", back_populates="business", cascade="all, delete-orphan"
    )
    orders: Mapped[List["Order"]] = relationship(
        "Order", back_populates="business", cascade="all, delete-orphan"
    )
    delivery_zones: Mapped[List["DeliveryZone"]] = relationship(
        "DeliveryZone", back_populates="business", cascade="all, delete-orphan"
    )
    channel_accounts: Mapped[List["ChannelAccount"]] = relationship(
        "ChannelAccount", back_populates="business", cascade="all, delete-orphan"
    )
    settings: Mapped[Optional["BusinessSettings"]] = relationship(
        "BusinessSettings", back_populates="business", uselist=False, cascade="all, delete-orphan", lazy="selectin"
    )
    ai_settings: Mapped[Optional["AISettings"]] = relationship(
        "AISettings", back_populates="business", uselist=False, cascade="all, delete-orphan", lazy="selectin"
    )

class BusinessMember(Base, TimestampMixin):
    __tablename__ = "business_members"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    business_id: Mapped[str] = mapped_column(String(36), ForeignKey("businesses.id", ondelete="CASCADE"), index=True, nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    role: Mapped[str] = mapped_column(String(50), default=RoleEnum.STAFF.value, nullable=False)

    business: Mapped["Business"] = relationship("Business", back_populates="members")
    user: Mapped["User"] = relationship("User", back_populates="business_memberships")

class BusinessSettings(Base, TimestampMixin):
    __tablename__ = "business_settings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    business_id: Mapped[str] = mapped_column(String(36), ForeignKey("businesses.id", ondelete="CASCADE"), unique=True, nullable=False)
    store_timings: Mapped[str] = mapped_column(String(255), default="Mon-Sat: 10:00 AM - 9:00 PM, Sun: 11:00 AM - 7:00 PM")
    contact_phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    contact_email: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    custom_instructions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    payment_methods: Mapped[List[str]] = mapped_column(JSON, default=lambda: ["UPI", "Cash on Delivery", "Card"])
    delivery_regions: Mapped[List[str]] = mapped_column(JSON, default=lambda: ["Hyderabad Metro", "Telangana", "All India"])

    business: Mapped["Business"] = relationship("Business", back_populates="settings")

class AISettings(Base, TimestampMixin):
    __tablename__ = "ai_settings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    business_id: Mapped[str] = mapped_column(String(36), ForeignKey("businesses.id", ondelete="CASCADE"), unique=True, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    model_name: Mapped[str] = mapped_column(String(100), default="gemini-2.5-flash")
    default_language: Mapped[str] = mapped_column(String(50), default="Telugu")
    auto_handoff_on_negative_sentiment: Mapped[bool] = mapped_column(Boolean, default=True)
    escalation_keywords: Mapped[List[str]] = mapped_column(JSON, default=lambda: [
        "human", "agent", "manager", "complaint", "fraud", "cheat", "scam", "police", "refund dispute"
    ])
    custom_prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    business: Mapped["Business"] = relationship("Business", back_populates="ai_settings")

# -------------------------------------------------------------
# Products, Inventory & Categories
# -------------------------------------------------------------

class ProductCategory(Base, TimestampMixin):
    __tablename__ = "product_categories"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    business_id: Mapped[str] = mapped_column(String(36), ForeignKey("businesses.id", ondelete="CASCADE"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    business: Mapped["Business"] = relationship("Business", back_populates="categories")
    products: Mapped[List["Product"]] = relationship("Product", back_populates="category")

class Product(Base, TimestampMixin):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    business_id: Mapped[str] = mapped_column(String(36), ForeignKey("businesses.id", ondelete="CASCADE"), index=True, nullable=False)
    category_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("product_categories.id", ondelete="SET NULL"), nullable=True)
    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    compare_at_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sku: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    stock: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    tags: Mapped[List[str]] = mapped_column(JSON, default=lambda: [])
    color: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    size: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    attributes: Mapped[dict] = mapped_column(JSON, default=lambda: {})

    business: Mapped["Business"] = relationship("Business", back_populates="products")
    category: Mapped[Optional["ProductCategory"]] = relationship("ProductCategory", back_populates="products")
    variants: Mapped[List["ProductVariant"]] = relationship("ProductVariant", back_populates="product", cascade="all, delete-orphan", lazy="selectin")
    images: Mapped[List["ProductImage"]] = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan", lazy="selectin")
    inventory_items: Mapped[List["Inventory"]] = relationship("Inventory", back_populates="product", cascade="all, delete-orphan")

class ProductVariant(Base, TimestampMixin):
    __tablename__ = "product_variants"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("products.id", ondelete="CASCADE"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    sku: Mapped[str] = mapped_column(String(100), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    stock: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    attributes: Mapped[dict] = mapped_column(JSON, default=lambda: {})

    product: Mapped["Product"] = relationship("Product", back_populates="variants")

class ProductImage(Base, TimestampMixin):
    __tablename__ = "product_images"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("products.id", ondelete="CASCADE"), index=True, nullable=False)
    image_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    alt_text: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)

    product: Mapped["Product"] = relationship("Product", back_populates="images")

class Inventory(Base, TimestampMixin):
    __tablename__ = "inventory"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    business_id: Mapped[str] = mapped_column(String(36), ForeignKey("businesses.id", ondelete="CASCADE"), index=True, nullable=False)
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("products.id", ondelete="CASCADE"), index=True, nullable=False)
    variant_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("product_variants.id", ondelete="SET NULL"), nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    low_stock_threshold: Mapped[int] = mapped_column(Integer, default=5)

    product: Mapped["Product"] = relationship("Product", back_populates="inventory_items")

# -------------------------------------------------------------
# Customers & CRM
# -------------------------------------------------------------

class Customer(Base, TimestampMixin):
    __tablename__ = "customers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    business_id: Mapped[str] = mapped_column(String(36), ForeignKey("businesses.id", ondelete="CASCADE"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(50), index=True, nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), index=True, nullable=True)
    preferred_language: Mapped[str] = mapped_column(String(50), default="Telugu")
    source: Mapped[str] = mapped_column(String(50), default=CustomerSource.INSTAGRAM.value)
    tags: Mapped[List[str]] = mapped_column(JSON, default=lambda: [])
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    order_count: Mapped[int] = mapped_column(Integer, default=0)
    total_spending: Mapped[float] = mapped_column(Float, default=0.0)
    last_interaction: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now)

    business: Mapped["Business"] = relationship("Business", back_populates="customers")
    addresses: Mapped[List["CustomerAddress"]] = relationship("CustomerAddress", back_populates="customer", cascade="all, delete-orphan")
    conversations: Mapped[List["Conversation"]] = relationship("Conversation", back_populates="customer", cascade="all, delete-orphan")
    orders: Mapped[List["Order"]] = relationship("Order", back_populates="customer")
    leads: Mapped[List["Lead"]] = relationship("Lead", back_populates="customer")

class CustomerAddress(Base, TimestampMixin):
    __tablename__ = "customer_addresses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customers.id", ondelete="CASCADE"), index=True, nullable=False)
    address_line: Mapped[str] = mapped_column(String(255), nullable=False)
    locality: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    city: Mapped[str] = mapped_column(String(100), default="Hyderabad")
    pincode: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    state: Mapped[str] = mapped_column(String(100), default="Telangana")
    is_default: Mapped[bool] = mapped_column(Boolean, default=True)

    customer: Mapped["Customer"] = relationship("Customer", back_populates="addresses")

# -------------------------------------------------------------
# Conversations & Messages
# -------------------------------------------------------------

class Conversation(Base, TimestampMixin):
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    business_id: Mapped[str] = mapped_column(String(36), ForeignKey("businesses.id", ondelete="CASCADE"), index=True, nullable=False)
    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customers.id", ondelete="CASCADE"), index=True, nullable=False)
    channel: Mapped[str] = mapped_column(String(50), default=ChannelEnum.INSTAGRAM.value, index=True)
    status: Mapped[str] = mapped_column(String(50), default=ConversationStatus.AI_HANDLING.value, index=True)
    assigned_user_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    last_message_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now)
    is_ai_handled: Mapped[bool] = mapped_column(Boolean, default=True)
    handoff_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=lambda: {})

    business: Mapped["Business"] = relationship("Business", back_populates="conversations")
    customer: Mapped["Customer"] = relationship("Customer", back_populates="conversations")
    messages: Mapped[List["Message"]] = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", order_by="Message.created_at")

class ConversationParticipant(Base, TimestampMixin):
    __tablename__ = "conversation_participants"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    conversation_id: Mapped[str] = mapped_column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"), index=True, nullable=False)
    user_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    customer_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("customers.id", ondelete="CASCADE"), nullable=True)
    role: Mapped[str] = mapped_column(String(50), default="PARTICIPANT")

class Message(Base, TimestampMixin):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    conversation_id: Mapped[str] = mapped_column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"), index=True, nullable=False)
    sender_type: Mapped[str] = mapped_column(String(50), default=MessageSenderType.CUSTOMER.value, nullable=False)
    sender_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    channel: Mapped[str] = mapped_column(String(50), default=ChannelEnum.INSTAGRAM.value)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    media_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    media_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    is_internal: Mapped[bool] = mapped_column(Boolean, default=False)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=lambda: {})

    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="messages")

# -------------------------------------------------------------
# Leads & Lead Scoring
# -------------------------------------------------------------

class Lead(Base, TimestampMixin):
    __tablename__ = "leads"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    business_id: Mapped[str] = mapped_column(String(36), ForeignKey("businesses.id", ondelete="CASCADE"), index=True, nullable=False)
    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customers.id", ondelete="CASCADE"), index=True, nullable=False)
    conversation_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("conversations.id", ondelete="SET NULL"), nullable=True)
    product_interest: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    budget: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    purchase_intent: Mapped[str] = mapped_column(String(50), default="MEDIUM")
    score: Mapped[int] = mapped_column(Integer, default=50)  # 0 to 100
    status: Mapped[str] = mapped_column(String(50), default=LeadStatus.NEW.value, index=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    customer: Mapped["Customer"] = relationship("Customer", back_populates="leads")
    events: Mapped[List["LeadEvent"]] = relationship("LeadEvent", back_populates="lead", cascade="all, delete-orphan")

class LeadEvent(Base, TimestampMixin):
    __tablename__ = "lead_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    lead_id: Mapped[str] = mapped_column(String(36), ForeignKey("leads.id", ondelete="CASCADE"), index=True, nullable=False)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    score_delta: Mapped[int] = mapped_column(Integer, default=0)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    lead: Mapped["Lead"] = relationship("Lead", back_populates="events")

# -------------------------------------------------------------
# Delivery Zones & Orders
# -------------------------------------------------------------

class DeliveryZone(Base, TimestampMixin):
    __tablename__ = "delivery_zones"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    business_id: Mapped[str] = mapped_column(String(36), ForeignKey("businesses.id", ondelete="CASCADE"), index=True, nullable=False)
    city: Mapped[str] = mapped_column(String(100), default="Hyderabad")
    locality: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    pincode: Mapped[Optional[str]] = mapped_column(String(20), index=True, nullable=True)
    delivery_fee: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    minimum_order: Mapped[float] = mapped_column(Float, default=0.0)
    estimated_delivery: Mapped[str] = mapped_column(String(100), default="Same Day / Next Day")
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    business: Mapped["Business"] = relationship("Business", back_populates="delivery_zones")

class Order(Base, TimestampMixin):
    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    business_id: Mapped[str] = mapped_column(String(36), ForeignKey("businesses.id", ondelete="CASCADE"), index=True, nullable=False)
    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customers.id", ondelete="CASCADE"), index=True, nullable=False)
    conversation_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("conversations.id", ondelete="SET NULL"), nullable=True)
    order_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default=OrderStatus.NEW.value, index=True)
    subtotal: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    delivery_fee: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    discount: Mapped[float] = mapped_column(Float, default=0.0)
    total: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    delivery_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    delivery_zone_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("delivery_zones.id", ondelete="SET NULL"), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    payment_status: Mapped[str] = mapped_column(String(50), default=PaymentStatus.PENDING.value)

    business: Mapped["Business"] = relationship("Business", back_populates="orders")
    customer: Mapped["Customer"] = relationship("Customer", back_populates="orders")
    items: Mapped[List["OrderItem"]] = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan", lazy="selectin")
    payments: Mapped[List["Payment"]] = relationship("Payment", back_populates="order", cascade="all, delete-orphan")

class OrderItem(Base, TimestampMixin):
    __tablename__ = "order_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    order_id: Mapped[str] = mapped_column(String(36), ForeignKey("orders.id", ondelete="CASCADE"), index=True, nullable=False)
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    variant_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("product_variants.id", ondelete="SET NULL"), nullable=True)
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    total_price: Mapped[float] = mapped_column(Float, nullable=False)

    order: Mapped["Order"] = relationship("Order", back_populates="items")
    product: Mapped["Product"] = relationship("Product")

class Payment(Base, TimestampMixin):
    __tablename__ = "payments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    order_id: Mapped[str] = mapped_column(String(36), ForeignKey("orders.id", ondelete="CASCADE"), index=True, nullable=False)
    business_id: Mapped[str] = mapped_column(String(36), ForeignKey("businesses.id", ondelete="CASCADE"), index=True, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="INR")
    status: Mapped[str] = mapped_column(String(50), default=PaymentStatus.PENDING.value)
    provider: Mapped[str] = mapped_column(String(50), default="MOCK")
    transaction_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=lambda: {})

    order: Mapped["Order"] = relationship("Order", back_populates="payments")

# -------------------------------------------------------------
# Follow-Up Jobs & Automation
# -------------------------------------------------------------

class FollowUpJob(Base, TimestampMixin):
    __tablename__ = "follow_up_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    business_id: Mapped[str] = mapped_column(String(36), ForeignKey("businesses.id", ondelete="CASCADE"), index=True, nullable=False)
    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customers.id", ondelete="CASCADE"), index=True, nullable=False)
    conversation_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("conversations.id", ondelete="SET NULL"), nullable=True)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    channel: Mapped[str] = mapped_column(String(50), default=ChannelEnum.INSTAGRAM.value)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    reason: Mapped[str] = mapped_column(String(255), default="Product enquiry follow-up")
    status: Mapped[str] = mapped_column(String(50), default=FollowUpStatus.SCHEDULED.value, index=True)
    executed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

# -------------------------------------------------------------
# Knowledge Base
# -------------------------------------------------------------

class KnowledgeDocument(Base, TimestampMixin):
    __tablename__ = "knowledge_documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    business_id: Mapped[str] = mapped_column(String(36), ForeignKey("businesses.id", ondelete="CASCADE"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(50), default="FAQ")
    content: Mapped[str] = mapped_column(Text, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    chunks: Mapped[List["KnowledgeChunk"]] = relationship("KnowledgeChunk", back_populates="document", cascade="all, delete-orphan")

class KnowledgeChunk(Base, TimestampMixin):
    __tablename__ = "knowledge_chunks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    document_id: Mapped[str] = mapped_column(String(36), ForeignKey("knowledge_documents.id", ondelete="CASCADE"), index=True, nullable=False)
    business_id: Mapped[str] = mapped_column(String(36), ForeignKey("businesses.id", ondelete="CASCADE"), index=True, nullable=False)
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, default=0)

    document: Mapped["KnowledgeDocument"] = relationship("KnowledgeDocument", back_populates="chunks")

# -------------------------------------------------------------
# Channel Accounts & Webhooks
# -------------------------------------------------------------

class ChannelAccount(Base, TimestampMixin):
    __tablename__ = "channel_accounts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    business_id: Mapped[str] = mapped_column(String(36), ForeignKey("businesses.id", ondelete="CASCADE"), index=True, nullable=False)
    channel: Mapped[str] = mapped_column(String(50), nullable=False)
    account_id: Mapped[str] = mapped_column(String(255), index=True, nullable=False)  # IG User ID or WA Phone ID
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    display_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="CONNECTED")
    last_webhook_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    business: Mapped["Business"] = relationship("Business", back_populates="channel_accounts")
    credentials_metadata: Mapped[Optional["ChannelCredentialsMetadata"]] = relationship(
        "ChannelCredentialsMetadata", back_populates="channel_account", uselist=False, cascade="all, delete-orphan"
    )

class ChannelCredentialsMetadata(Base, TimestampMixin):
    __tablename__ = "channel_credentials_metadata"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    channel_account_id: Mapped[str] = mapped_column(String(36), ForeignKey("channel_accounts.id", ondelete="CASCADE"), unique=True, nullable=False)
    token_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    scopes: Mapped[List[str]] = mapped_column(JSON, default=lambda: [])
    metadata_json: Mapped[dict] = mapped_column(JSON, default=lambda: {})

    channel_account: Mapped["ChannelAccount"] = relationship("ChannelAccount", back_populates="credentials_metadata")

class WebhookEvent(Base, TimestampMixin):
    __tablename__ = "webhook_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    event_id: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)  # For idempotency
    channel: Mapped[str] = mapped_column(String(50), nullable=False)
    business_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("businesses.id", ondelete="SET NULL"), nullable=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    payload_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    processing_status: Mapped[str] = mapped_column(String(50), default="PROCESSED")
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), default=get_utc_now)

# -------------------------------------------------------------
# AI Sessions & Tool Calls
# -------------------------------------------------------------

class AISession(Base, TimestampMixin):
    __tablename__ = "ai_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    conversation_id: Mapped[str] = mapped_column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"), index=True, nullable=False)
    model_name: Mapped[str] = mapped_column(String(100), default="gemini-2.5-flash")
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)

    tool_calls: Mapped[List["AIToolCall"]] = relationship("AIToolCall", back_populates="session", cascade="all, delete-orphan")

class AIToolCall(Base, TimestampMixin):
    __tablename__ = "ai_tool_calls"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("ai_sessions.id", ondelete="CASCADE"), index=True, nullable=False)
    tool_name: Mapped[str] = mapped_column(String(100), nullable=False)
    arguments_json: Mapped[dict] = mapped_column(JSON, default=lambda: {})
    result_json: Mapped[dict] = mapped_column(JSON, default=lambda: {})
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    duration_ms: Mapped[int] = mapped_column(Integer, default=0)

    session: Mapped["AISession"] = relationship("AISession", back_populates="tool_calls")

# -------------------------------------------------------------
# Notifications & Audit Logs
# -------------------------------------------------------------

class Notification(Base, TimestampMixin):
    __tablename__ = "notifications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    business_id: Mapped[str] = mapped_column(String(36), ForeignKey("businesses.id", ondelete="CASCADE"), index=True, nullable=False)
    user_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    link: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)

class AuditLog(Base, TimestampMixin):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    business_id: Mapped[str] = mapped_column(String(36), ForeignKey("businesses.id", ondelete="CASCADE"), index=True, nullable=False)
    user_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    details_json: Mapped[dict] = mapped_column(JSON, default=lambda: {})
