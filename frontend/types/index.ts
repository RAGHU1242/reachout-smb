export interface User {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  created_at: string;
}

export interface Business {
  id: string;
  name: string;
  slug: string;
  business_type: string;
  location: string;
  city: string;
  currency: string;
  languages: string[];
  description?: string;
  return_policy?: string;
  active: boolean;
  created_at: string;
}

export interface ProductImage {
  id?: string;
  image_url: string;
  alt_text?: string;
  sort_order: number;
  is_primary: boolean;
}

export interface Product {
  id: string;
  business_id: string;
  name: string;
  description?: string;
  price: number;
  compare_at_price?: number;
  sku: string;
  stock: number;
  active: boolean;
  category_id?: string;
  tags: string[];
  color?: string;
  size?: string;
  images: ProductImage[];
  created_at: string;
}

export interface Customer {
  id: string;
  business_id: string;
  name: string;
  phone?: string;
  email?: string;
  preferred_language: string;
  source: string;
  tags: string[];
  notes?: string;
  order_count: number;
  total_spending: number;
  last_interaction: string;
  created_at: string;
}

export interface Message {
  id: string;
  conversation_id: string;
  sender_type: 'CUSTOMER' | 'AI' | 'AGENT' | 'SYSTEM';
  sender_id?: string;
  channel: 'INSTAGRAM' | 'WHATSAPP' | 'WEBSITE' | 'MOCK';
  content: string;
  media_url?: string;
  media_type?: string;
  is_internal: boolean;
  created_at: string;
}

export interface Conversation {
  id: string;
  business_id: string;
  customer_id: string;
  customer_name?: string;
  customer_phone?: string;
  channel: 'INSTAGRAM' | 'WHATSAPP' | 'WEBSITE' | 'MOCK';
  status: 'OPEN' | 'AI_HANDLING' | 'HUMAN_REQUIRED' | 'WAITING_CUSTOMER' | 'RESOLVED' | 'CLOSED';
  is_ai_handled: boolean;
  handoff_reason?: string;
  last_message_at: string;
  created_at: string;
  latest_message?: Message;
  preferred_language?: string;
  lead_score?: number;
  lead_status?: string;
  lead_product_interest?: string;
  lead_budget?: number;
  lead_notes?: string;
  delivery_locality?: string;
  delivery_fee?: number;
}

export interface Lead {
  id: string;
  business_id: string;
  customer_id: string;
  customer_name?: string;
  conversation_id?: string;
  product_interest?: string;
  budget?: number;
  purchase_intent: string;
  score: number;
  status: 'NEW' | 'CONTACTED' | 'QUALIFIED' | 'HOT' | 'WARM' | 'COLD' | 'CONVERTED' | 'LOST';
  notes?: string;
  created_at: string;
}

export interface OrderItem {
  id: string;
  product_id: string;
  product_name: string;
  unit_price: number;
  quantity: number;
  total_price: number;
}

export interface Order {
  id: string;
  business_id: string;
  customer_id: string;
  customer_name?: string;
  order_number: string;
  status: string;
  subtotal: number;
  delivery_fee: number;
  discount: number;
  total: number;
  delivery_address?: string;
  payment_status: string;
  created_at: string;
  items: OrderItem[];
}

export interface DeliveryZone {
  id: string;
  business_id: string;
  city: string;
  locality: string;
  pincode?: string;
  delivery_fee: number;
  minimum_order: number;
  estimated_delivery: string;
  active: boolean;
}

export interface FollowUp {
  id: string;
  business_id: string;
  customer_id: string;
  customer_name?: string;
  conversation_id?: string;
  scheduled_at: string;
  channel: string;
  message: string;
  reason: string;
  status: string;
  created_at: string;
}

export interface TeamMember {
  id: string;
  business_id: string;
  user_id: string;
  email: string;
  full_name: string;
  role: string;
  status: string;
  created_at: string;
}

export interface HourlyVolumeItem {
  time: string;
  count: number;
  percentage: number;
}

export interface TopProductItem {
  name: string;
  price: number;
  orders: number;
  enquiries: number;
}

export interface AnalyticsOverview {
  business_name?: string;
  city?: string;
  total_revenue: number;
  total_orders: number;
  new_leads: number;
  hot_leads: number;
  total_conversations: number;
  ai_handled_count: number;
  human_handoff_count: number;
  conversion_rate: number;
  ai_handling_rate: number;
  recent_orders: Order[];
  hot_leads_list: Lead[];
  hourly_volume?: HourlyVolumeItem[];
  top_products?: TopProductItem[];
  insights?: string[];
}

export interface SimulatorMessageResponse {
  conversation_id: string;
  customer_id: string;
  incoming_message: Message;
  ai_response: Message;
  detected_intent?: string;
  recommended_products: any[];
  tool_calls_executed: string[];
}
