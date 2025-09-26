from datetime import datetime
from typing import Optional, List
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship, JSON, Column
from sqlalchemy import DateTime, func
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
# Order Models
# ===============================

class OrderBase(SQLModel):
    """Shared order fields"""
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


class OrderRead(OrderBase):
    """Schema for reading orders"""
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    items: List["OrderItemRead"] = []


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


class ProductRecipeCreate(ProductRecipeBase):
    """Schema for creating product recipes"""
    pass


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
    phone: str = Field(unique=True, max_length=20, description="Client phone number")
    notes: Optional[str] = Field(default=None, max_length=2000, description="Notes about the client")


class Client(ClientBase, table=True):
    """Client table model for storing client-specific data like notes"""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now())
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now(), onupdate=func.now())
    )


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
    user: UserRead = Field(description="User information")


class TokenData(SQLModel):
    """Schema for JWT token data"""
    user_id: int = Field(description="User ID")
    phone: Optional[str] = Field(default=None, description="User phone")
    role: Optional[str] = Field(default=None, description="User role")


# Update forward references
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