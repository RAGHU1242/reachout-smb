from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, EmailStr, Field, ConfigDict

# -------------------------------------------------------------
# Auth & User
# -------------------------------------------------------------

class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: str
    is_active: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# -------------------------------------------------------------
# Business & Multi-Tenancy
# -------------------------------------------------------------

class BusinessBase(BaseModel):
    name: str
    business_type: str = "Fashion & Apparel"
    location: str = "Hyderabad, India"
    city: str = "Hyderabad"
    currency: str = "INR"
    languages: List[str] = ["Telugu", "English", "Hindi"]
    description: Optional[str] = None
    return_policy: Optional[str] = None

class BusinessCreate(BusinessBase):
    slug: Optional[str] = None

class BusinessUpdate(BaseModel):
    name: Optional[str] = None
    business_type: Optional[str] = None
    location: Optional[str] = None
    city: Optional[str] = None
    currency: Optional[str] = None
    languages: Optional[List[str]] = None
    description: Optional[str] = None
    return_policy: Optional[str] = None
    active: Optional[bool] = None

class BusinessSettingsSchema(BaseModel):
    store_timings: str = "Mon-Sat: 10:00 AM - 9:00 PM"
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    custom_instructions: Optional[str] = None
    payment_methods: List[str] = ["UPI", "Cash on Delivery", "Card"]
    delivery_regions: List[str] = ["Hyderabad Metro", "Telangana", "All India"]
    model_config = ConfigDict(from_attributes=True)

class AISettingsSchema(BaseModel):
    enabled: bool = True
    model_name: str = "gemini-2.5-flash"
    default_language: str = "Telugu"
    auto_handoff_on_negative_sentiment: bool = True
    escalation_keywords: List[str] = [
        "human", "agent", "manager", "complaint", "fraud", "cheat", "scam", "refund dispute"
    ]
    custom_prompt: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class BusinessMemberResponse(BaseModel):
    id: str
    business_id: str
    user_id: str
    email: str
    full_name: str
    role: str
    status: str = "Active"
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class BusinessMemberInvite(BaseModel):
    email: str
    full_name: str
    role: str = "STAFF"

class BusinessResponse(BusinessBase):
    id: str
    slug: str
    active: bool
    created_at: datetime
    settings: Optional[BusinessSettingsSchema] = None
    ai_settings: Optional[AISettingsSchema] = None
    model_config = ConfigDict(from_attributes=True)

class OnboardingRequest(BaseModel):
    name: str
    business_type: str
    location: str
    city: str
    languages: List[str]
    currency: str = "INR"
    delivery_regions: List[str] = ["Hyderabad"]
    payment_methods: List[str] = ["UPI", "COD"]
    return_policy: Optional[str] = "7-day exchange for unworn items with tags."
    description: Optional[str] = None
    connect_instagram: bool = False
    connect_whatsapp: bool = False

# -------------------------------------------------------------
# Products & Inventory
# -------------------------------------------------------------

class ProductCategoryBase(BaseModel):
    name: str
    slug: Optional[str] = None
    description: Optional[str] = None

class ProductCategoryCreate(ProductCategoryBase):
    pass

class ProductCategoryResponse(ProductCategoryBase):
    id: str
    slug: str
    active: bool
    model_config = ConfigDict(from_attributes=True)

class ProductImageSchema(BaseModel):
    id: Optional[str] = None
    image_url: str
    alt_text: Optional[str] = None
    sort_order: int = 0
    is_primary: bool = False
    model_config = ConfigDict(from_attributes=True)

class ProductVariantSchema(BaseModel):
    id: Optional[str] = None
    name: str
    sku: str
    price: float
    stock: int = 0
    attributes: Dict[str, Any] = {}
    model_config = ConfigDict(from_attributes=True)

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    compare_at_price: Optional[float] = None
    sku: str
    stock: int = 0
    active: bool = True
    category_id: Optional[str] = None
    tags: List[str] = []
    color: Optional[str] = None
    size: Optional[str] = None
    attributes: Dict[str, Any] = {}

class ProductCreate(ProductBase):
    images: List[str] = []

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    compare_at_price: Optional[float] = None
    sku: Optional[str] = None
    stock: Optional[int] = None
    active: Optional[bool] = None
    category_id: Optional[str] = None
    tags: Optional[List[str]] = None
    color: Optional[str] = None
    size: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None

class ProductResponse(ProductBase):
    id: str
    business_id: str
    images: List[ProductImageSchema] = []
    variants: List[ProductVariantSchema] = []
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# -------------------------------------------------------------
# Customers
# -------------------------------------------------------------

class CustomerBase(BaseModel):
    name: str
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    preferred_language: str = "Telugu"
    source: str = "INSTAGRAM"
    tags: List[str] = []
    notes: Optional[str] = None

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    preferred_language: Optional[str] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None

class CustomerResponse(CustomerBase):
    id: str
    business_id: str
    order_count: int
    total_spending: float
    last_interaction: datetime
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# -------------------------------------------------------------
# Conversations & Messages
# -------------------------------------------------------------

class MessageBase(BaseModel):
    content: str
    media_url: Optional[str] = None
    media_type: Optional[str] = None
    is_internal: bool = False

class MessageCreate(MessageBase):
    sender_type: str = "AGENT"  # AGENT or AI or CUSTOMER
    channel: Optional[str] = None

class MessageResponse(MessageBase):
    id: str
    conversation_id: str
    sender_type: str
    sender_id: Optional[str] = None
    channel: str
    created_at: datetime
    metadata_json: Dict[str, Any] = {}
    model_config = ConfigDict(from_attributes=True)

class ConversationResponse(BaseModel):
    id: str
    business_id: str
    customer_id: str
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    channel: str
    status: str
    is_ai_handled: bool
    handoff_reason: Optional[str] = None
    last_message_at: datetime
    created_at: datetime
    latest_message: Optional[MessageResponse] = None
    preferred_language: Optional[str] = None
    lead_score: Optional[int] = None
    lead_status: Optional[str] = None
    lead_product_interest: Optional[str] = None
    lead_budget: Optional[float] = None
    lead_notes: Optional[str] = None
    delivery_locality: Optional[str] = None
    delivery_fee: Optional[float] = None
    model_config = ConfigDict(from_attributes=True)

class HumanHandoffRequest(BaseModel):
    reason: str = "Manual staff takeover"
    is_ai_handled: bool = False

# -------------------------------------------------------------
# Leads
# -------------------------------------------------------------

class LeadBase(BaseModel):
    product_interest: Optional[str] = None
    budget: Optional[float] = None
    purchase_intent: str = "MEDIUM"
    score: int = 50
    status: str = "NEW"
    notes: Optional[str] = None

class LeadCreate(LeadBase):
    customer_id: str
    conversation_id: Optional[str] = None

class LeadUpdate(BaseModel):
    product_interest: Optional[str] = None
    budget: Optional[float] = None
    purchase_intent: Optional[str] = None
    score: Optional[int] = None
    status: Optional[str] = None
    notes: Optional[str] = None

class LeadResponse(LeadBase):
    id: str
    business_id: str
    customer_id: str
    customer_name: Optional[str] = None
    conversation_id: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# -------------------------------------------------------------
# Delivery Zones
# -------------------------------------------------------------

class DeliveryZoneBase(BaseModel):
    city: str = "Hyderabad"
    locality: str
    pincode: Optional[str] = None
    delivery_fee: float = 0.0
    minimum_order: float = 0.0
    estimated_delivery: str = "Same Day / Next Day"
    active: bool = True

class DeliveryZoneCreate(DeliveryZoneBase):
    pass

class DeliveryZoneResponse(DeliveryZoneBase):
    id: str
    business_id: str
    model_config = ConfigDict(from_attributes=True)

class DeliveryCalculationRequest(BaseModel):
    locality: Optional[str] = None
    pincode: Optional[str] = None
    subtotal: float = 0.0

class DeliveryCalculationResponse(BaseModel):
    zone_id: Optional[str] = None
    locality: Optional[str] = None
    delivery_fee: float
    free_delivery: bool
    estimated_delivery: str
    total: float

# -------------------------------------------------------------
# Orders
# -------------------------------------------------------------

class OrderItemCreate(BaseModel):
    product_id: str
    variant_id: Optional[str] = None
    quantity: int = 1

class OrderCreate(BaseModel):
    customer_id: str
    conversation_id: Optional[str] = None
    items: List[OrderItemCreate]
    delivery_address: str
    locality: Optional[str] = None
    pincode: Optional[str] = None
    notes: Optional[str] = None

class OrderItemResponse(BaseModel):
    id: str
    product_id: str
    product_name: str
    unit_price: float
    quantity: int
    total_price: float
    model_config = ConfigDict(from_attributes=True)

class OrderResponse(BaseModel):
    id: str
    business_id: str
    customer_id: str
    customer_name: Optional[str] = None
    order_number: str
    status: str
    subtotal: float
    delivery_fee: float
    discount: float
    total: float
    delivery_address: Optional[str] = None
    payment_status: str
    created_at: datetime
    items: List[OrderItemResponse] = []
    model_config = ConfigDict(from_attributes=True)

class OrderStatusUpdate(BaseModel):
    status: str

# -------------------------------------------------------------
# Follow-Up Jobs
# -------------------------------------------------------------

class FollowUpCreate(BaseModel):
    customer_id: str
    conversation_id: Optional[str] = None
    scheduled_at: datetime
    channel: str = "INSTAGRAM"
    message: str
    reason: str = "Enquiry follow-up"

class FollowUpResponse(BaseModel):
    id: str
    business_id: str
    customer_id: str
    customer_name: Optional[str] = None
    conversation_id: Optional[str] = None
    scheduled_at: datetime
    channel: str
    message: str
    reason: str
    status: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# -------------------------------------------------------------
# Analytics
# -------------------------------------------------------------

class HourlyVolumeItem(BaseModel):
    time: str
    count: int
    percentage: float

class TopProductItem(BaseModel):
    name: str
    price: float
    orders: int
    enquiries: int

class AnalyticsOverview(BaseModel):
    business_name: Optional[str] = None
    city: Optional[str] = None
    total_revenue: float
    total_orders: int
    new_leads: int
    hot_leads: int
    total_conversations: int
    ai_handled_count: int
    human_handoff_count: int
    conversion_rate: float
    ai_handling_rate: float
    recent_orders: List[OrderResponse] = []
    hot_leads_list: List[LeadResponse] = []
    hourly_volume: List[HourlyVolumeItem] = []
    top_products: List[TopProductItem] = []
    insights: List[str] = []

# -------------------------------------------------------------
# Simulator
# -------------------------------------------------------------

class SimulatorMessageRequest(BaseModel):
    business_id: Optional[str] = None
    channel: str = "INSTAGRAM"  # INSTAGRAM or WHATSAPP
    customer_name: str = "Sneha Reddy"
    customer_phone: Optional[str] = "+919876543210"
    message: str = "Anna red saree undha?"

class SimulatorMessageResponse(BaseModel):
    conversation_id: str
    customer_id: str
    incoming_message: MessageResponse
    ai_response: MessageResponse
    detected_intent: Optional[str] = None
    recommended_products: List[Dict[str, Any]] = []
    tool_calls_executed: List[str] = []
