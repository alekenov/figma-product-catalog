from datetime import datetime
from typing import Optional, List
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship, JSON, Column, Index
from sqlalchemy import DateTime, func
from pydantic import field_serializer
from utils import kopecks_to_tenge, tenge_to_kopecks, format_price_tenge


# ===============================
# Enums
# ===============================

class ProductType(str, Enum):
    FLOWERS = "flowers"
    SWEETS = "sweets"
    FRUITS = "fruits"
    GIFTS = "gifts"


class OrderStatus(str, Enum):
    NEW = "new"
    PAID = "paid"
    ACCEPTED = "accepted"
    ASSEMBLED = "assembled"
    IN_DELIVERY = "in_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


# ===============================
# Product Models
# ===============================

class ProductBase(SQLModel):
    """Shared product fields"""
    name: str = Field(max_length=200)
    price: int = Field(description="Price in tenge (kopecks)")
    type: ProductType = Field(default=ProductType.FLOWERS)
    description: Optional[str] = Field(default=None, max_length=1000)
    manufacturingTime: Optional[int] = Field(default=None, description="Manufacturing time in minutes")
    width: Optional[int] = Field(default=None)
    height: Optional[int] = Field(default=None)
    shelfLife: Optional[int] = Field(default=None)
    enabled: bool = Field(default=True)
    is_featured: bool = Field(default=False)
    colors: Optional[List[str]] = Field(default=None, sa_column=Column(JSON))
    occasions: Optional[List[str]] = Field(default=None, sa_column=Column(JSON))
    cities: Optional[List[str]] = Field(default=None, sa_column=Column(JSON))
    tags: Optional[List[str]] = Field(default=None, sa_column=Column(JSON), description="Filter tags like urgent, budget, discount")
    image: Optional[str] = Field(default=None, max_length=500)


class Product(ProductBase, table=True):
    """Product table model"""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now())
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now(), onupdate=func.now())
    )

    # Relationships
    order_items: List["OrderItem"] = Relationship(back_populates="product")
    recipes: List["ProductRecipe"] = Relationship(back_populates="product")


class ProductCreate(ProductBase):
    """Schema for creating products"""
    pass


class ProductUpdate(SQLModel):
    """Schema for updating products"""
    name: Optional[str] = Field(default=None, max_length=200)
    price: Optional[int] = None
    type: Optional[ProductType] = None
    description: Optional[str] = Field(default=None, max_length=1000)
    manufacturingTime: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    shelfLife: Optional[int] = None
    enabled: Optional[bool] = None
    is_featured: Optional[bool] = None
    colors: Optional[List[str]] = None
    occasions: Optional[List[str]] = None
    cities: Optional[List[str]] = None
    image: Optional[str] = None


class ProductRead(ProductBase):
    """Schema for reading products"""
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ===============================
# Product Variant Models (Size/Price variations)
# ===============================

class ProductVariantBase(SQLModel):
    """Shared product variant fields"""
    product_id: int = Field(foreign_key="product.id")
    size: str = Field(max_length=10, description="S, M, L, XL, etc.")
    price: int = Field(description="Price in kopecks for this variant")
    enabled: bool = Field(default=True)


class ProductVariant(ProductVariantBase, table=True):
    """Product variant table model"""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now())
    )


class ProductVariantCreate(ProductVariantBase):
    """Schema for creating product variants"""
    pass


class ProductVariantRead(ProductVariantBase):
    """Schema for reading product variants"""
    id: int
    created_at: Optional[datetime] = None


# ===============================
# Product Image Models
# ===============================

class ProductImageBase(SQLModel):
    """Shared product image fields"""
    product_id: int = Field(foreign_key="product.id")
    url: str = Field(max_length=500, description="Image URL")
    order: int = Field(default=0, description="Display order")
    is_primary: bool = Field(default=False, description="Primary/main image")


class ProductImage(ProductImageBase, table=True):
    """Product image table model"""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now())
    )


class ProductImageCreate(ProductImageBase):
    """Schema for creating product images"""
    pass


class ProductImageRead(ProductImageBase):
    """Schema for reading product images"""
    id: int
    created_at: Optional[datetime] = None


# ===============================
# Order Models
# ===============================

class OrderBase(SQLModel):
    """Shared order fields"""
    tracking_id: str = Field(unique=True, index=True, max_length=9, description="Public 9-digit tracking ID")
    orderNumber: str = Field(unique=True, max_length=20, description="Order number like #12345")
    customerName: str = Field(max_length=100)
    phone: str = Field(max_length=20)
    customer_email: Optional[str] = Field(default=None, max_length=255)
    delivery_address: Optional[str] = Field(default=None, max_length=500)
    delivery_date: Optional[datetime] = Field(default=None)
    delivery_notes: Optional[str] = Field(default=None, max_length=500)
    subtotal: int = Field(description="Subtotal in tenge")
    delivery_cost: int = Field(default=0, description="Delivery cost in tenge")
    total: int = Field(description="Total amount in tenge")
    status: OrderStatus = Field(default=OrderStatus.NEW)
    notes: Optional[str] = Field(default=None, max_length=1000)

    # Phase 3: Checkout flow fields
    recipient_name: Optional[str] = Field(default=None, max_length=100, description="Recipient name (may differ from customer)")
    recipient_phone: Optional[str] = Field(default=None, max_length=20, description="Recipient contact")
    sender_phone: Optional[str] = Field(default=None, max_length=20, description="Sender/orderer contact")
    pickup_address: Optional[str] = Field(default=None, max_length=500, description="Store pickup location")
    delivery_type: Optional[str] = Field(default=None, max_length=50, description="express, scheduled, pickup")
    scheduled_time: Optional[str] = Field(default=None, max_length=100, description="Scheduled delivery time")
    payment_method: Optional[str] = Field(default=None, max_length=50, description="kaspi, card, cash")
    order_comment: Optional[str] = Field(default=None, max_length=1000, description="Customer wishes/comments")
    bonus_points: Optional[int] = Field(default=0, description="Loyalty points earned")


class Order(OrderBase, table=True):
    """Order table model"""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now())
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now(), onupdate=func.now())
    )

    # Relationships
    items: List["OrderItem"] = Relationship(back_populates="order")
    reservations: List["OrderReservation"] = Relationship(back_populates="order")
    photos: List["OrderPhoto"] = Relationship()


class OrderCreate(SQLModel):
    """Schema for creating orders"""
    customerName: str = Field(max_length=100)
    phone: str = Field(max_length=20)
    customer_email: Optional[str] = Field(default=None, max_length=255)
    delivery_address: Optional[str] = Field(default=None, max_length=500)
    delivery_date: Optional[datetime] = Field(default=None)
    delivery_notes: Optional[str] = Field(default=None, max_length=500)
    delivery_cost: int = Field(default=0, description="Delivery cost in tenge")
    notes: Optional[str] = Field(default=None, max_length=1000)

    # Phase 3: Checkout flow fields
    recipient_name: Optional[str] = Field(default=None, max_length=100)
    recipient_phone: Optional[str] = Field(default=None, max_length=20)
    sender_phone: Optional[str] = Field(default=None, max_length=20)
    pickup_address: Optional[str] = Field(default=None, max_length=500)
    delivery_type: Optional[str] = Field(default=None, max_length=50)
    scheduled_time: Optional[str] = Field(default=None, max_length=100)
    payment_method: Optional[str] = Field(default=None, max_length=50)
    order_comment: Optional[str] = Field(default=None, max_length=1000)
    bonus_points: Optional[int] = Field(default=0)


class OrderItemRequest(SQLModel):
    """Schema for order item availability request"""
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0, description="Requested quantity")
    special_requests: Optional[str] = Field(default=None, max_length=500)


class OrderCreateWithItems(SQLModel):
    """Schema for creating orders with items"""
    customerName: str = Field(max_length=100)
    phone: str = Field(max_length=20)
    customer_email: Optional[str] = Field(default=None, max_length=255)
    delivery_address: Optional[str] = Field(default=None, max_length=500)
    delivery_date: Optional[datetime] = Field(default=None)
    delivery_notes: Optional[str] = Field(default=None, max_length=500)
    delivery_cost: int = Field(default=0, description="Delivery cost in tenge")
    notes: Optional[str] = Field(default=None, max_length=1000)
    items: List[OrderItemRequest] = Field(description="Items to include in the order")
    check_availability: bool = Field(default=True, description="Whether to check availability before creating")

    # Phase 3: Checkout flow fields
    recipient_name: Optional[str] = Field(default=None, max_length=100)
    recipient_phone: Optional[str] = Field(default=None, max_length=20)
    sender_phone: Optional[str] = Field(default=None, max_length=20)
    pickup_address: Optional[str] = Field(default=None, max_length=500)
    delivery_type: Optional[str] = Field(default=None, max_length=50)
    scheduled_time: Optional[str] = Field(default=None, max_length=100)
    payment_method: Optional[str] = Field(default=None, max_length=50)
    order_comment: Optional[str] = Field(default=None, max_length=1000)
    bonus_points: Optional[int] = Field(default=0)


class OrderUpdate(SQLModel):
    """Schema for updating orders"""
    customerName: Optional[str] = Field(default=None, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=20)
    customer_email: Optional[str] = Field(default=None, max_length=255)
    delivery_address: Optional[str] = Field(default=None, max_length=500)
    delivery_date: Optional[datetime] = None
    delivery_notes: Optional[str] = Field(default=None, max_length=500)
    status: Optional[OrderStatus] = None
    notes: Optional[str] = Field(default=None, max_length=1000)

    # Phase 3: Checkout flow fields
    recipient_name: Optional[str] = Field(default=None, max_length=100)
    recipient_phone: Optional[str] = Field(default=None, max_length=20)
    sender_phone: Optional[str] = Field(default=None, max_length=20)
    pickup_address: Optional[str] = Field(default=None, max_length=500)
    delivery_type: Optional[str] = Field(default=None, max_length=50)
    scheduled_time: Optional[str] = Field(default=None, max_length=100)
    payment_method: Optional[str] = Field(default=None, max_length=50)
    order_comment: Optional[str] = Field(default=None, max_length=1000)
    bonus_points: Optional[int] = Field(default=None)


class OrderRead(OrderBase):
    """Schema for reading orders"""
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    items: List["OrderItemRead"] = []
    photos: List["OrderPhotoRead"] = []


# ===============================
# Order Item Models
# ===============================

class OrderItemBase(SQLModel):
    """Shared order item fields"""
    order_id: int = Field(foreign_key="order.id")
    product_id: int = Field(foreign_key="product.id")
    product_name: str = Field(max_length=200)
    product_price: int = Field(description="Product price at time of order")
    quantity: int = Field(default=1, ge=1)
    item_total: int = Field(description="Total for this line item")
    special_requests: Optional[str] = Field(default=None, max_length=500)


class OrderItem(OrderItemBase, table=True):
    """Order item table model"""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now())
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now(), onupdate=func.now())
    )

    # Relationships
    order: Optional[Order] = Relationship(back_populates="items")
    product: Optional[Product] = Relationship(back_populates="order_items")


class OrderItemCreate(OrderItemBase):
    """Schema for creating order items"""
    pass


class OrderItemRead(OrderItemBase):
    """Schema for reading order items"""
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ===============================
# Order Photo Models
# ===============================

class OrderPhotoBase(SQLModel):
    """Shared order photo fields"""
    order_id: int = Field(foreign_key="order.id")
    photo_url: str = Field(max_length=500, description="URL to photo")
    photo_type: str = Field(max_length=50, description="assembly, delivery, etc.")
    label: Optional[str] = Field(default=None, max_length=200, description="Photo caption")
    client_feedback: Optional[str] = Field(default=None, max_length=20, description="like or dislike")
    client_comment: Optional[str] = Field(default=None, max_length=1000, description="Client feedback comment")
    feedback_at: Optional[datetime] = Field(default=None, description="When feedback was given")


class OrderPhoto(OrderPhotoBase, table=True):
    """Order photo table model"""
    id: Optional[int] = Field(default=None, primary_key=True)
    uploaded_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now())
    )
    feedback_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime)
    )

    # Relationships
    order: Optional[Order] = Relationship()


class OrderPhotoCreate(SQLModel):
    """Schema for creating order photos"""
    order_id: int
    photo_url: str = Field(max_length=500)
    photo_type: str = Field(max_length=50)
    label: Optional[str] = Field(default=None, max_length=200)


class OrderPhotoRead(OrderPhotoBase):
    """Schema for reading order photos"""
    id: int
    uploaded_at: Optional[datetime] = None


# ===============================
# Order History Models
# ===============================

class OrderHistoryBase(SQLModel):
    """Shared order history fields"""
    order_id: int = Field(foreign_key="order.id")
    changed_by: str = Field(max_length=20, description="'customer' or 'admin'")
    field_name: str = Field(max_length=100, description="Name of changed field")
    old_value: Optional[str] = Field(default=None, max_length=1000)
    new_value: Optional[str] = Field(default=None, max_length=1000)


class OrderHistory(OrderHistoryBase, table=True):
    """Order change history for audit trail"""
    id: Optional[int] = Field(default=None, primary_key=True)
    changed_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )


class OrderHistoryRead(OrderHistoryBase):
    """Schema for reading order history"""
    id: int
    changed_at: datetime


# ===============================
# Warehouse Models
# ===============================

class WarehouseOperationType(str, Enum):
    DELIVERY = "delivery"
    SALE = "sale"
    WRITEOFF = "writeoff"
    PRICE_CHANGE = "price_change"
    INVENTORY = "inventory"


class WarehouseItemBase(SQLModel):
    """Shared warehouse item fields"""
    name: str = Field(max_length=200)
    quantity: int = Field(default=0, ge=0)
    cost_price: int = Field(description="Cost price in kopecks")
    retail_price: int = Field(description="Retail price in kopecks")
    image: Optional[str] = Field(default=None, max_length=500)
    last_delivery_date: Optional[datetime] = Field(default=None)
    min_quantity: Optional[int] = Field(default=10, ge=0)


class WarehouseItem(WarehouseItemBase, table=True):
    """Warehouse item table model"""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now())
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now(), onupdate=func.now())
    )

    # Relationships
    operations: List["WarehouseOperation"] = Relationship(back_populates="warehouse_item")
    used_in_products: List["ProductRecipe"] = Relationship(back_populates="warehouse_item")
    reservations: List["OrderReservation"] = Relationship(back_populates="warehouse_item")


class WarehouseItemCreate(SQLModel):
    """Schema for creating warehouse items - accepts tenge values from frontend"""
    name: str = Field(max_length=200)
    quantity: int = Field(default=0, ge=0)
    cost_price_tenge: int = Field(description="Cost price in tenge")
    retail_price_tenge: int = Field(description="Retail price in tenge")
    image: Optional[str] = Field(default=None, max_length=500)
    min_quantity: Optional[int] = Field(default=10, ge=0)

    @property
    def cost_price(self) -> int:
        """Convert tenge to kopecks for internal storage"""
        return tenge_to_kopecks(self.cost_price_tenge)

    @property
    def retail_price(self) -> int:
        """Convert tenge to kopecks for internal storage"""
        return tenge_to_kopecks(self.retail_price_tenge)


class WarehouseItemUpdate(SQLModel):
    """Schema for updating warehouse items - accepts tenge values"""
    name: Optional[str] = Field(default=None, max_length=200)
    quantity: Optional[int] = Field(default=None, ge=0)
    cost_price_tenge: Optional[int] = Field(default=None, description="Cost price in tenge")
    retail_price_tenge: Optional[int] = Field(default=None, description="Retail price in tenge")
    image: Optional[str] = None
    min_quantity: Optional[int] = Field(default=None, ge=0)

    @property
    def cost_price(self) -> Optional[int]:
        """Convert tenge to kopecks for internal storage"""
        return tenge_to_kopecks(self.cost_price_tenge) if self.cost_price_tenge is not None else None

    @property
    def retail_price(self) -> Optional[int]:
        """Convert tenge to kopecks for internal storage"""
        return tenge_to_kopecks(self.retail_price_tenge) if self.retail_price_tenge is not None else None


class WarehouseItemRead(WarehouseItemBase):
    """Schema for reading warehouse items with both kopeck and tenge values"""
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @property
    def cost_price_tenge(self) -> int:
        """Cost price in tenge for display"""
        return kopecks_to_tenge(self.cost_price)

    @property
    def retail_price_tenge(self) -> int:
        """Retail price in tenge for display"""
        return kopecks_to_tenge(self.retail_price)

    def model_dump(self, **kwargs):
        """Include tenge values in serialization"""
        data = super().model_dump(**kwargs)
        data['cost_price_tenge'] = self.cost_price_tenge
        data['retail_price_tenge'] = self.retail_price_tenge
        return data


class WarehouseOperationBase(SQLModel):
    """Shared warehouse operation fields"""
    warehouse_item_id: int = Field(foreign_key="warehouseitem.id")
    operation_type: WarehouseOperationType
    quantity_change: int = Field(description="Positive for additions, negative for removals")
    balance_after: int = Field(ge=0, description="Balance after operation")
    description: str = Field(max_length=500)
    old_value: Optional[int] = Field(default=None, description="Old price for price changes")
    new_value: Optional[int] = Field(default=None, description="New price for price changes")
    order_id: Optional[int] = Field(default=None, foreign_key="order.id")


class WarehouseOperation(WarehouseOperationBase, table=True):
    """Warehouse operation table model"""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now())
    )

    # Relationships
    warehouse_item: Optional[WarehouseItem] = Relationship(back_populates="operations")
    order: Optional[Order] = Relationship()


class WarehouseOperationCreate(SQLModel):
    """Schema for creating warehouse operations"""
    warehouse_item_id: int
    operation_type: WarehouseOperationType
    quantity_change: Optional[int] = Field(default=0)
    description: str = Field(max_length=500)
    old_value: Optional[int] = None
    new_value: Optional[int] = None
    order_id: Optional[int] = None
    reason: Optional[str] = Field(default=None, max_length=200, description="Reason for writeoff")


class WarehouseOperationRead(WarehouseOperationBase):
    """Schema for reading warehouse operations"""
    id: int
    created_at: Optional[datetime] = None


class WarehouseItemDetail(WarehouseItemRead):
    """Schema for reading warehouse item with operations - includes tenge values"""
    operations: List[WarehouseOperationRead] = []


# ===============================
# Product Recipe Models
# ===============================

class ProductRecipeBase(SQLModel):
    """Shared product recipe fields"""
    product_id: int = Field(foreign_key="product.id")
    warehouse_item_id: int = Field(foreign_key="warehouseitem.id")
    quantity: int = Field(gt=0, description="Quantity of warehouse item needed")
    is_optional: bool = Field(default=False, description="Whether this component is optional")


class ProductRecipe(ProductRecipeBase, table=True):
    """Product recipe table model - links products to warehouse items"""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now())
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now(), onupdate=func.now())
    )

    # Relationships
    product: Optional[Product] = Relationship(back_populates="recipes")
    warehouse_item: Optional[WarehouseItem] = Relationship(back_populates="used_in_products")


class ProductRecipeCreate(SQLModel):
    """Schema for creating product recipes - product_id comes from URL"""
    warehouse_item_id: int = Field(foreign_key="warehouseitem.id")
    quantity: int = Field(gt=0, description="Quantity of warehouse item needed")
    is_optional: bool = Field(default=False, description="Whether this component is optional")


class ProductRecipeUpdate(SQLModel):
    """Schema for updating product recipes"""
    quantity: Optional[int] = Field(default=None, gt=0)
    is_optional: Optional[bool] = None


class ProductRecipeRead(ProductRecipeBase):
    """Schema for reading product recipes"""
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    warehouse_item: Optional[WarehouseItemRead] = None


class ProductWithRecipe(ProductRead):
    """Schema for reading product with its recipe"""
    recipes: List[ProductRecipeRead] = []
    total_cost: Optional[int] = Field(default=None, description="Calculated cost based on recipe")
    can_produce: Optional[bool] = Field(default=None, description="Whether we have enough stock")
    max_quantity: Optional[int] = Field(default=None, description="Maximum quantity we can produce")


# ===============================
# Order Reservation Models
# ===============================

class OrderReservationBase(SQLModel):
    """Shared order reservation fields"""
    order_id: int = Field(foreign_key="order.id")
    warehouse_item_id: int = Field(foreign_key="warehouseitem.id")
    reserved_quantity: int = Field(gt=0, description="Quantity of warehouse item reserved")


class OrderReservation(OrderReservationBase, table=True):
    """Order reservation table model - reserves warehouse items for orders"""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now())
    )

    # Relationships
    order: Optional[Order] = Relationship(back_populates="reservations")
    warehouse_item: Optional[WarehouseItem] = Relationship(back_populates="reservations")


class OrderReservationCreate(OrderReservationBase):
    """Schema for creating order reservations"""
    pass


class OrderReservationRead(OrderReservationBase):
    """Schema for reading order reservations"""
    id: int
    created_at: Optional[datetime] = None
    warehouse_item: Optional[WarehouseItemRead] = None


# ===============================
# Availability Models
# ===============================

class IngredientAvailability(SQLModel):
    """Schema for ingredient availability details"""
    warehouse_item_id: int
    name: str
    required: int = Field(description="Required quantity for this product")
    available: int = Field(description="Available quantity in warehouse")
    reserved: int = Field(default=0, description="Currently reserved quantity")
    sufficient: bool = Field(description="Whether we have enough stock")


class ProductAvailability(SQLModel):
    """Schema for product availability details"""
    product_id: int
    product_name: str
    quantity_requested: int
    available: bool = Field(description="Whether the product is available in requested quantity")
    max_quantity: int = Field(description="Maximum quantity we can produce")
    ingredients: List[IngredientAvailability] = []


class AvailabilityResponse(SQLModel):
    """Schema for order availability check response"""
    available: bool = Field(description="Whether all items in order are available")
    items: List[ProductAvailability] = []
    warnings: List[str] = []


# ===============================
# Inventory Models
# ===============================

class InventoryCheckBase(SQLModel):
    """Shared inventory check fields"""
    conducted_by: str = Field(max_length=100, description="Person who conducted inventory")
    comment: Optional[str] = Field(default=None, max_length=500)
    status: str = Field(default="pending", description="Status: pending, applied")
    applied_at: Optional[datetime] = Field(default=None)


class InventoryCheck(InventoryCheckBase, table=True):
    """Inventory check table model"""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now())
    )

    # Relationships
    items: List["InventoryCheckItem"] = Relationship(back_populates="inventory_check")


class InventoryCheckItemBase(SQLModel):
    """Shared inventory check item fields"""
    inventory_check_id: int = Field(foreign_key="inventorycheck.id")
    warehouse_item_id: int = Field(foreign_key="warehouseitem.id")
    warehouse_item_name: str = Field(max_length=200)
    current_quantity: int = Field(ge=0, description="Current quantity in system")
    actual_quantity: int = Field(ge=0, description="Actual counted quantity")
    difference: int = Field(description="Difference (actual - current)")


class InventoryCheckItem(InventoryCheckItemBase, table=True):
    """Inventory check item table model"""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now())
    )

    # Relationships
    inventory_check: Optional[InventoryCheck] = Relationship(back_populates="items")
    warehouse_item: Optional[WarehouseItem] = Relationship()


class InventoryCheckCreate(SQLModel):
    """Schema for creating inventory check"""
    conducted_by: str = Field(max_length=100)
    comment: Optional[str] = Field(default=None, max_length=500)
    items: List[dict] = Field(description="List of items with warehouse_item_id and actual_quantity")


class InventoryCheckItemCreate(SQLModel):
    """Schema for creating inventory check items"""
    warehouse_item_id: int
    actual_quantity: int = Field(ge=0)


class InventoryCheckRead(InventoryCheckBase):
    """Schema for reading inventory check"""
    id: int
    created_at: Optional[datetime] = None
    items: List["InventoryCheckItemRead"] = []


class InventoryCheckItemRead(InventoryCheckItemBase):
    """Schema for reading inventory check items"""
    id: int
    created_at: Optional[datetime] = None


# ===============================
# Client Models
# ===============================

class ClientBase(SQLModel):
    """Shared client fields"""
    phone: str = Field(
        unique=True,
        max_length=20,
        description="Client phone number (normalized format +7XXXXXXXXXX)",
        index=True  # Add explicit index for fast lookups
    )
    customerName: Optional[str] = Field(default=None, max_length=200, description="Client name")
    notes: Optional[str] = Field(default=None, max_length=2000, description="Notes about the client")


class Client(ClientBase, table=True):
    """Client table model for storing client-specific data like notes"""
    __tablename__ = "client"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now())
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now(), onupdate=func.now())
    )

    # Add composite index for common query patterns (phone + customerName search)
    __table_args__ = (
        Index('idx_client_phone_name', 'phone', 'customerName'),
        Index('idx_client_created_at', 'created_at'),
    )


class ClientCreate(SQLModel):
    """Schema for creating a new client"""
    phone: str = Field(max_length=20, description="Client phone number")
    customerName: str = Field(min_length=1, max_length=200, description="Client name")
    notes: Optional[str] = Field(default="", max_length=2000, description="Notes about the client")


class ClientUpdate(SQLModel):
    """Schema for updating client information"""
    notes: Optional[str] = Field(default=None, max_length=2000)


class ClientRead(ClientBase):
    """Schema for reading client information"""
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ===============================
# User Authentication Models
# ===============================

class UserRole(str, Enum):
    DIRECTOR = "director"
    MANAGER = "manager"
    FLORIST = "florist"
    COURIER = "courier"


class UserBase(SQLModel):
    """Shared user fields"""
    name: str = Field(max_length=100)
    phone: str = Field(unique=True, max_length=20, description="Phone number in Kazakhstan format")
    role: UserRole = Field(default=UserRole.FLORIST)
    is_active: bool = Field(default=True)
    invited_by: Optional[int] = Field(default=None, foreign_key="user.id")


class User(UserBase, table=True):
    """User table model"""
    id: Optional[int] = Field(default=None, primary_key=True)
    password_hash: str = Field(max_length=255)
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now())
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now(), onupdate=func.now())
    )

    # Relationships
    inviter: Optional["User"] = Relationship(back_populates="invited_users", sa_relationship_kwargs={"remote_side": "User.id"})
    invited_users: List["User"] = Relationship(back_populates="inviter")
    invitations_sent: List["TeamInvitation"] = Relationship(back_populates="invited_by_user")


class UserCreate(SQLModel):
    """Schema for creating users"""
    name: str = Field(max_length=100)
    phone: str = Field(max_length=20)
    role: UserRole = Field(default=UserRole.FLORIST)
    password: str = Field(min_length=6, description="Plain text password to be hashed")
    invited_by: Optional[int] = None


class UserUpdate(SQLModel):
    """Schema for updating users"""
    name: Optional[str] = Field(default=None, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=20)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    password: Optional[str] = Field(default=None, min_length=6, description="New password to be hashed")


class UserRead(UserBase):
    """Schema for reading users"""
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class UserResponse(SQLModel):
    """Schema for API responses with uppercase role"""
    id: int
    name: str
    phone: str
    role: str  # Will be uppercase enum name
    is_active: bool
    invited_by: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_user(cls, user):
        """Create UserResponse from User object with uppercase role"""
        return cls(
            id=user.id,
            name=user.name,
            phone=user.phone,
            role=user.role.name,  # Convert to uppercase enum name
            is_active=user.is_active,
            invited_by=user.invited_by,
            created_at=user.created_at,
            updated_at=user.updated_at
        )


# ===============================
# Shop Settings Models
# ===============================

class City(str, Enum):
    ALMATY = "Almaty"
    ASTANA = "Astana"


class ShopSettingsBase(SQLModel):
    """Shared shop settings fields"""
    shop_name: str = Field(max_length=200)
    address: str = Field(max_length=500)
    city: City = Field(default=City.ALMATY)

    # Working hours
    weekday_start: str = Field(default="09:00", description="Weekday opening time (HH:MM)")
    weekday_end: str = Field(default="18:00", description="Weekday closing time (HH:MM)")
    weekday_closed: bool = Field(default=False, description="Whether closed on weekdays")

    weekend_start: str = Field(default="10:00", description="Weekend opening time (HH:MM)")
    weekend_end: str = Field(default="17:00", description="Weekend closing time (HH:MM)")
    weekend_closed: bool = Field(default=False, description="Whether closed on weekends")

    # Delivery settings (prices in kopecks)
    delivery_cost: int = Field(default=150000, description="Delivery cost in kopecks (1500 tenge)")
    free_delivery_amount: int = Field(default=1000000, description="Free delivery threshold in kopecks (10000 tenge)")
    pickup_available: bool = Field(default=True)
    delivery_available: bool = Field(default=True)


class ShopSettings(ShopSettingsBase, table=True):
    """Shop settings table model - singleton table"""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now())
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now(), onupdate=func.now())
    )


class ShopSettingsUpdate(SQLModel):
    """Schema for updating shop settings"""
    shop_name: Optional[str] = Field(default=None, max_length=200)
    address: Optional[str] = Field(default=None, max_length=500)
    city: Optional[City] = None

    weekday_start: Optional[str] = None
    weekday_end: Optional[str] = None
    weekday_closed: Optional[bool] = None

    weekend_start: Optional[str] = None
    weekend_end: Optional[str] = None
    weekend_closed: Optional[bool] = None

    delivery_cost_tenge: Optional[int] = Field(default=None, description="Delivery cost in tenge")
    free_delivery_amount_tenge: Optional[int] = Field(default=None, description="Free delivery threshold in tenge")
    pickup_available: Optional[bool] = None
    delivery_available: Optional[bool] = None

    @property
    def delivery_cost(self) -> Optional[int]:
        """Convert tenge to kopecks for internal storage"""
        return tenge_to_kopecks(self.delivery_cost_tenge) if self.delivery_cost_tenge is not None else None

    @property
    def free_delivery_amount(self) -> Optional[int]:
        """Convert tenge to kopecks for internal storage"""
        return tenge_to_kopecks(self.free_delivery_amount_tenge) if self.free_delivery_amount_tenge is not None else None


class ShopSettingsRead(ShopSettingsBase):
    """Schema for reading shop settings with tenge values"""
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @property
    def delivery_cost_tenge(self) -> int:
        """Delivery cost in tenge for display"""
        return kopecks_to_tenge(self.delivery_cost)

    @property
    def free_delivery_amount_tenge(self) -> int:
        """Free delivery threshold in tenge for display"""
        return kopecks_to_tenge(self.free_delivery_amount)

    def model_dump(self, **kwargs):
        """Include tenge values in serialization"""
        data = super().model_dump(**kwargs)
        data['delivery_cost_tenge'] = self.delivery_cost_tenge
        data['free_delivery_amount_tenge'] = self.free_delivery_amount_tenge
        return data


# ===============================
# Team Invitation Models
# ===============================

class InvitationStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    EXPIRED = "expired"


class TeamInvitationBase(SQLModel):
    """Shared team invitation fields"""
    phone: str = Field(max_length=20, description="Phone number to invite")
    name: str = Field(max_length=100, description="Name of person being invited")
    role: UserRole = Field(description="Role to assign to invited user")
    invited_by: int = Field(foreign_key="user.id", description="User ID who sent invitation")
    status: InvitationStatus = Field(default=InvitationStatus.PENDING)
    invitation_code: str = Field(max_length=6, description="6-digit invitation code")
    expires_at: datetime = Field(description="When invitation expires")


class TeamInvitation(TeamInvitationBase, table=True):
    """Team invitation table model"""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now())
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now(), onupdate=func.now())
    )

    # Relationships
    invited_by_user: Optional[User] = Relationship(back_populates="invitations_sent")


class TeamInvitationCreate(SQLModel):
    """Schema for creating team invitations"""
    phone: str = Field(max_length=20)
    name: str = Field(max_length=100)
    role: UserRole


class TeamInvitationRead(TeamInvitationBase):
    """Schema for reading team invitations"""
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    invited_by_user: Optional[UserRead] = None


# ===============================
# Authentication Models
# ===============================

class LoginRequest(SQLModel):
    """Schema for login request"""
    phone: str = Field(max_length=20, description="Phone number")
    password: str = Field(description="User password")


class LoginResponse(SQLModel):
    """Schema for login response"""
    access_token: str = Field(description="JWT access token")
    token_type: str = Field(default="bearer")
    user: UserResponse = Field(description="User information")


class TokenData(SQLModel):
    """Schema for JWT token data"""
    user_id: int = Field(description="User ID")
    phone: Optional[str] = Field(default=None, description="User phone")
    role: Optional[str] = Field(default=None, description="User role")


# ===============================
# Order Counter Model for Atomic Number Generation
# ===============================

class OrderCounter(SQLModel, table=True):
    """Counter table for atomic order number generation"""
    id: int = Field(default=1, primary_key=True)
    counter: int = Field(default=0, description="Current order counter value")
    last_updated: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now(), onupdate=func.now())
    )


# ===============================
# Product Addon Models (Additional Options)
# ===============================

class ProductAddonBase(SQLModel):
    """Shared product addon fields"""
    product_id: int = Field(foreign_key="product.id")
    name: str = Field(max_length=200, description="Addon name (e.g., 'Упаковочная лента и бумага')")
    description: Optional[str] = Field(default=None, max_length=500)
    price: int = Field(default=0, description="Price in kopecks (0 for free options)")
    is_default: bool = Field(default=False, description="Whether this option is checked by default")
    enabled: bool = Field(default=True)


class ProductAddon(ProductAddonBase, table=True):
    """Product addon table model - additional options like packaging, greeting cards"""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now())
    )


class ProductAddonCreate(ProductAddonBase):
    """Schema for creating product addons"""
    pass


class ProductAddonRead(ProductAddonBase):
    """Schema for reading product addons"""
    id: int
    created_at: Optional[datetime] = None


# ===============================
# Product Bundle Models (Frequently Bought Together)
# ===============================

class ProductBundleBase(SQLModel):
    """Shared product bundle fields"""
    main_product_id: int = Field(foreign_key="product.id", description="Main product ID")
    bundled_product_id: int = Field(foreign_key="product.id", description="Related product ID")
    display_order: int = Field(default=0, description="Display order in list")
    enabled: bool = Field(default=True)


class ProductBundle(ProductBundleBase, table=True):
    """Product bundle table model - frequently bought together suggestions"""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now())
    )


class ProductBundleCreate(ProductBundleBase):
    """Schema for creating product bundles"""
    pass


class ProductBundleRead(ProductBundleBase):
    """Schema for reading product bundles"""
    id: int
    created_at: Optional[datetime] = None


# ===============================
# Pickup Location Models
# ===============================

class PickupLocationBase(SQLModel):
    """Shared pickup location fields"""
    city: City = Field(description="City (Almaty/Astana)")
    address: str = Field(max_length=300, description="Full address")
    landmark: Optional[str] = Field(default=None, max_length=200, description="Landmark (e.g., 'ТЦ Dostyk Plaza')")
    enabled: bool = Field(default=True)
    display_order: int = Field(default=0, description="Display order in list")


class PickupLocation(PickupLocationBase, table=True):
    """Pickup location table model - shop pickup addresses"""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now())
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now(), onupdate=func.now())
    )


class PickupLocationCreate(PickupLocationBase):
    """Schema for creating pickup locations"""
    pass


class PickupLocationUpdate(SQLModel):
    """Schema for updating pickup locations"""
    city: Optional[City] = None
    address: Optional[str] = Field(default=None, max_length=300)
    landmark: Optional[str] = Field(default=None, max_length=200)
    enabled: Optional[bool] = None
    display_order: Optional[int] = None


class PickupLocationRead(PickupLocationBase):
    """Schema for reading pickup locations"""
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ===============================
# Product Review Models
# ===============================

class ProductReviewBase(SQLModel):
    """Shared product review fields"""
    product_id: int = Field(foreign_key="product.id")
    author_name: str = Field(max_length=100, description="Review author name")
    rating: int = Field(ge=1, le=5, description="Rating from 1 to 5")
    text: str = Field(max_length=2000, description="Review text")
    likes: int = Field(default=0, ge=0, description="Number of likes")
    dislikes: int = Field(default=0, ge=0, description="Number of dislikes")


class ProductReview(ProductReviewBase, table=True):
    """Product review table model - reviews for individual products"""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now())
    )

    # Relationships
    photos: List["ReviewPhoto"] = Relationship(back_populates="review")


class ProductReviewCreate(ProductReviewBase):
    """Schema for creating product reviews"""
    pass


class ProductReviewRead(ProductReviewBase):
    """Schema for reading product reviews"""
    id: int
    created_at: Optional[datetime] = None
    photos: List["ReviewPhotoRead"] = []


# ===============================
# Review Photo Models
# ===============================

class ReviewPhotoBase(SQLModel):
    """Shared review photo fields"""
    review_id: int = Field(foreign_key="productreview.id")
    url: str = Field(max_length=500, description="Photo URL")
    order: int = Field(default=0, description="Display order")


class ReviewPhoto(ReviewPhotoBase, table=True):
    """Review photo table model - photos attached to reviews"""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now())
    )

    # Relationships
    review: Optional[ProductReview] = Relationship(back_populates="photos")


class ReviewPhotoCreate(ReviewPhotoBase):
    """Schema for creating review photos"""
    pass


class ReviewPhotoRead(ReviewPhotoBase):
    """Schema for reading review photos"""
    id: int
    created_at: Optional[datetime] = None


# ===============================
# Company Review Models
# ===============================

class CompanyReviewBase(SQLModel):
    """Shared company review fields"""
    author_name: str = Field(max_length=100, description="Review author name")
    rating: int = Field(ge=1, le=5, description="Rating from 1 to 5")
    text: str = Field(max_length=2000, description="Review text")
    likes: int = Field(default=0, ge=0, description="Number of likes")
    dislikes: int = Field(default=0, ge=0, description="Number of dislikes")


class CompanyReview(CompanyReviewBase, table=True):
    """Company review table model - reviews for the entire shop/company"""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now())
    )


class CompanyReviewCreate(CompanyReviewBase):
    """Schema for creating company reviews"""
    pass


class CompanyReviewRead(CompanyReviewBase):
    """Schema for reading company reviews"""
    id: int
    created_at: Optional[datetime] = None


# ===============================
# FAQ Models
# ===============================

class FAQBase(SQLModel):
    """Shared FAQ fields"""
    question: str = Field(max_length=500, description="FAQ question")
    answer: str = Field(max_length=2000, description="FAQ answer")
    category: Optional[str] = Field(default="general", max_length=50, description="FAQ category")
    display_order: int = Field(default=0, description="Display order for sorting")
    enabled: bool = Field(default=True, description="Whether FAQ is visible")


class FAQ(FAQBase, table=True):
    """FAQ table model"""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now())
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now(), onupdate=func.now())
    )


class FAQCreate(FAQBase):
    """Schema for creating FAQs"""
    pass


class FAQUpdate(SQLModel):
    """Schema for updating FAQs"""
    question: Optional[str] = Field(default=None, max_length=500)
    answer: Optional[str] = Field(default=None, max_length=2000)
    category: Optional[str] = Field(default=None, max_length=50)
    display_order: Optional[int] = None
    enabled: Optional[bool] = None


class FAQRead(FAQBase):
    """Schema for reading FAQs"""
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ===============================
# Static Page Models
# ===============================

class StaticPageBase(SQLModel):
    """Shared static page fields"""
    slug: str = Field(unique=True, max_length=100, description="URL slug")
    title: str = Field(max_length=200, description="Page title")
    content: str = Field(description="HTML or Markdown content")
    meta_description: Optional[str] = Field(default=None, max_length=300, description="SEO meta description")
    enabled: bool = Field(default=True, description="Whether page is published")


class StaticPage(StaticPageBase, table=True):
    """Static page table model"""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now())
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now(), onupdate=func.now())
    )


class StaticPageCreate(StaticPageBase):
    """Schema for creating static pages"""
    pass


class StaticPageUpdate(SQLModel):
    """Schema for updating static pages"""
    slug: Optional[str] = Field(default=None, max_length=100)
    title: Optional[str] = Field(default=None, max_length=200)
    content: Optional[str] = None
    meta_description: Optional[str] = Field(default=None, max_length=300)
    enabled: Optional[bool] = None


class StaticPageRead(StaticPageBase):
    """Schema for reading static pages"""
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ===============================
# Product Detail Response Models
# ===============================

class CompositionItemRead(SQLModel):
    """Schema for composition item in detail response"""
    id: int = Field(description="Warehouse item ID")
    name: str = Field(description="Ingredient name")
    quantity: int = Field(description="Quantity needed")


class ProductBundleItemRead(SQLModel):
    """Schema for frequently bought product in bundle"""
    id: int = Field(description="Product ID")
    name: str = Field(description="Product name")
    price: int = Field(description="Price in kopecks")
    image: Optional[str] = Field(default=None, description="Product image URL")


class ReviewsBreakdownRead(SQLModel):
    """Schema for rating breakdown"""
    five: int = Field(alias="5")
    four: int = Field(alias="4")
    three: int = Field(alias="3")
    two: int = Field(alias="2")
    one: int = Field(alias="1")

    class Config:
        populate_by_name = True


class ReviewsAggregateRead(SQLModel):
    """Schema for reviews aggregate data"""
    count: int = Field(description="Total number of reviews")
    average_rating: float = Field(description="Average rating")
    breakdown: ReviewsBreakdownRead = Field(description="Rating breakdown by stars")
    photos: List[str] = Field(default_factory=list, description="Review photo URLs")
    items: List[ProductReviewRead] = Field(default_factory=list, description="Review items")


class ProductDetailRead(SQLModel):
    """Schema for complete product detail response"""
    # Basic product info
    id: int
    name: str
    price: int = Field(description="Base price in kopecks")
    type: ProductType
    description: Optional[str] = None
    image: Optional[str] = None
    enabled: bool
    is_featured: bool

    # Product attributes
    colors: Optional[List[str]] = None
    occasions: Optional[List[str]] = None
    cities: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    manufacturingTime: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    shelfLife: Optional[int] = None

    # Metadata
    rating: Optional[float] = Field(default=None, description="Average rating from product reviews")
    review_count: int = Field(default=0, description="Number of product reviews")
    rating_count: int = Field(default=0, description="Total ratings given (from review_count + additional ratings)")

    # Images
    images: List[ProductImageRead] = Field(default_factory=list)

    # Variants (sizes)
    variants: List[ProductVariantRead] = Field(default_factory=list)

    # Composition (ingredients)
    composition: List[CompositionItemRead] = Field(default_factory=list)

    # Additional options
    addons: List[ProductAddonRead] = Field(default_factory=list)

    # Frequently bought together
    frequently_bought: List[ProductBundleItemRead] = Field(default_factory=list)

    # Pickup locations
    pickup_locations: List[str] = Field(default_factory=list, description="Formatted pickup address strings")

    # Reviews
    reviews: dict = Field(default_factory=dict, description="Product and company reviews")


# ===============================
# Update forward references
ProductReviewRead.model_rebuild()
ReviewPhotoRead.model_rebuild()
OrderRead.model_rebuild()
OrderCreateWithItems.model_rebuild()
OrderItemRead.model_rebuild()
WarehouseItemDetail.model_rebuild()
ProductRecipeRead.model_rebuild()
ProductWithRecipe.model_rebuild()
OrderReservationRead.model_rebuild()
InventoryCheckRead.model_rebuild()
InventoryCheckItemRead.model_rebuild()
UserRead.model_rebuild()
TeamInvitationRead.model_rebuild()