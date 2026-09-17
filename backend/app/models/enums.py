import enum

class RoleEnum(str, enum.Enum):
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    STAFF = "STAFF"
    VIEWER = "VIEWER"

class ChannelEnum(str, enum.Enum):
    INSTAGRAM = "INSTAGRAM"
    WHATSAPP = "WHATSAPP"
    WEBSITE = "WEBSITE"
    MOCK = "MOCK"

class ConversationStatus(str, enum.Enum):
    OPEN = "OPEN"
    AI_HANDLING = "AI_HANDLING"
    HUMAN_REQUIRED = "HUMAN_REQUIRED"
    WAITING_CUSTOMER = "WAITING_CUSTOMER"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"

class MessageSenderType(str, enum.Enum):
    CUSTOMER = "CUSTOMER"
    AI = "AI"
    AGENT = "AGENT"
    SYSTEM = "SYSTEM"

class LeadStatus(str, enum.Enum):
    NEW = "NEW"
    CONTACTED = "CONTACTED"
    QUALIFIED = "QUALIFIED"
    HOT = "HOT"
    WARM = "WARM"
    COLD = "COLD"
    CONVERTED = "CONVERTED"
    LOST = "LOST"

class OrderStatus(str, enum.Enum):
    NEW = "NEW"
    ITEMS_SELECTED = "ITEMS_SELECTED"
    ADDRESS_REQUIRED = "ADDRESS_REQUIRED"
    ADDRESS_CONFIRMED = "ADDRESS_CONFIRMED"
    PAYMENT_PENDING = "PAYMENT_PENDING"
    PAYMENT_CONFIRMED = "PAYMENT_CONFIRMED"
    CONFIRMED = "CONFIRMED"
    PROCESSING = "PROCESSING"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    REFUNDED = "REFUNDED"

class PaymentStatus(str, enum.Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"

class FollowUpStatus(str, enum.Enum):
    SCHEDULED = "SCHEDULED"
    SENT = "SENT"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class CustomerSource(str, enum.Enum):
    INSTAGRAM = "INSTAGRAM"
    WHATSAPP = "WHATSAPP"
    WEBSITE = "WEBSITE"
    MANUAL = "MANUAL"
    OTHER = "OTHER"
