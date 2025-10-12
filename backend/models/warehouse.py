"""
Warehouse models including items, operations, recipes, and reservations.

Includes WarehouseItem, WarehouseOperation, ProductRecipe, and OrderReservation models with their schemas.
"""
from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import DateTime, func, Column

from .enums import WarehouseOperationType
from utils import kopecks_to_tenge, tenge_to_kopecks


# ===============================
# Warehouse Item Models
# ===============================

class WarehouseItemBase(SQLModel):
    """Shared warehouse item fields"""
    name: str = Field(max_length=200)
    quantity: int = Field(default=0, ge=0)
    cost_price: int = Field(description="Cost price in kopecks")
    retail_price: int = Field(description="Retail price in kopecks")
    image: Optional[str] = Field(default=None, max_length=500)
    last_delivery_date: Optional[datetime] = Field(default=None)
    min_quantity: Optional[int] = Field(default=10, ge=0)
    shop_id: int = Field(foreign_key="shop.id", description="Shop that owns this warehouse item")


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
    shop: Optional["Shop"] = Relationship()


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


# ===============================
# Warehouse Operation Models
# ===============================

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
    user_id: Optional[int] = Field(default=None, foreign_key="user.id", description="User who performed the operation")


class WarehouseOperation(WarehouseOperationBase, table=True):
    """Warehouse operation table model"""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now())
    )

    # Relationships
    warehouse_item: Optional["WarehouseItem"] = Relationship(back_populates="operations")
    order: Optional["Order"] = Relationship()
    user: Optional["User"] = Relationship()


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
    user_name: Optional[str] = Field(default=None, description="Name of user who performed the operation")


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
    product: Optional["Product"] = Relationship(back_populates="recipes")
    warehouse_item: Optional["WarehouseItem"] = Relationship(back_populates="used_in_products")


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


class ProductWithRecipe(SQLModel):
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
    order: Optional["Order"] = Relationship(back_populates="reservations")
    warehouse_item: Optional["WarehouseItem"] = Relationship(back_populates="reservations")


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
    """Schema for ingredient availability in warehouse"""
    warehouse_item_id: int = Field(description="Warehouse item ID")
    name: str = Field(description="Ingredient name")
    required: int = Field(description="Required quantity per product")
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
    shop_id: int = Field(foreign_key="shop.id", description="Shop that owns this inventory check")


class InventoryCheck(InventoryCheckBase, table=True):
    """Inventory check table model"""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now())
    )

    # Relationships
    items: List["InventoryCheckItem"] = Relationship(back_populates="inventory_check")
    shop: Optional["Shop"] = Relationship()


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
    inventory_check: Optional["InventoryCheck"] = Relationship(back_populates="items")
    warehouse_item: Optional["WarehouseItem"] = Relationship()


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
