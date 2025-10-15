"""
Modular models package for the flower shop application.

This package organizes models into logical groups while maintaining backward compatibility
with the original monolithic models.py file through re-exports.
"""

# Enums
from .enums import (
    ProductType,
    OrderStatus,
    UserRole,
    WarehouseOperationType,
    City,
    InvitationStatus
)

# Product models
from .products import (
    ProductBase,
    Product,
    ProductCreate,
    ProductUpdate,
    ProductRead,
    ProductVariantBase,
    ProductVariant,
    ProductVariantCreate,
    ProductVariantRead,
    ProductImageBase,
    ProductImage,
    ProductImageCreate,
    ProductImageRead,
    ProductAddonBase,
    ProductAddon,
    ProductAddonCreate,
    ProductAddonRead,
    ProductBundleBase,
    ProductBundle,
    ProductBundleCreate,
    ProductBundleRead
)

# Order models
from .orders import (
    OrderBase,
    Order,
    OrderCreate,
    OrderItemRequest,
    OrderCreateWithItems,
    OrderUpdate,
    OrderRead,
    OrderItemBase,
    OrderItem,
    OrderItemCreate,
    OrderItemRead,
    OrderPhotoBase,
    OrderPhoto,
    OrderPhotoCreate,
    OrderPhotoRead,
    OrderHistoryBase,
    OrderHistory,
    OrderHistoryRead
)

# Warehouse models
from .warehouse import (
    WarehouseItemBase,
    WarehouseItem,
    WarehouseItemCreate,
    WarehouseItemUpdate,
    WarehouseItemRead,
    WarehouseOperationBase,
    WarehouseOperation,
    WarehouseOperationCreate,
    WarehouseOperationRead,
    WarehouseItemDetail,
    ProductRecipeBase,
    ProductRecipe,
    ProductRecipeCreate,
    ProductRecipeUpdate,
    ProductRecipeRead,
    ProductWithRecipe,
    OrderReservationBase,
    OrderReservation,
    OrderReservationCreate,
    OrderReservationRead,
    IngredientAvailability,
    ProductAvailability,
    AvailabilityResponse,
    InventoryCheckBase,
    InventoryCheck,
    InventoryCheckItemBase,
    InventoryCheckItem,
    InventoryCheckCreate,
    InventoryCheckItemCreate,
    InventoryCheckRead,
    InventoryCheckItemRead
)

# User models
from .users import (
    ClientBase,
    Client,
    ClientCreate,
    ClientUpdate,
    ClientRead,
    UserBase,
    User,
    UserCreate,
    UserUpdate,
    UserRead,
    UserResponse,
    TeamInvitationBase,
    TeamInvitation,
    TeamInvitationCreate,
    TeamInvitationRead,
    LoginRequest,
    LoginResponse,
    TokenData
)

# Shop models
from .shop import (
    Shop,
    ShopCreate,
    ShopUpdate,
    WorkingHoursUpdate,
    DeliverySettingsUpdate,
    ShopRead,
    ShopSettingsBase,
    ShopSettings,
    ShopSettingsUpdate,
    ShopSettingsRead,
    PickupLocationBase,
    PickupLocation,
    PickupLocationCreate,
    PickupLocationUpdate,
    PickupLocationRead,
    OrderCounter,
    ShopPublicListItem,
    ShopPublicDetail
)

# Review models
from .reviews import (
    ProductReviewBase,
    ProductReview,
    ProductReviewCreate,
    ProductReviewRead,
    ReviewPhotoBase,
    ReviewPhoto,
    ReviewPhotoCreate,
    ReviewPhotoRead,
    CompanyReviewBase,
    CompanyReview,
    CompanyReviewCreate,
    CompanyReviewRead,
    FAQBase,
    FAQ,
    FAQCreate,
    FAQUpdate,
    FAQRead,
    StaticPageBase,
    StaticPage,
    StaticPageCreate,
    StaticPageUpdate,
    StaticPageRead
)

# Response schemas
from .schemas import (
    CompositionItemRead,
    ProductBundleItemRead,
    ReviewsBreakdownRead,
    ReviewsAggregateRead,
    ProductDetailRead
)

# Chat models
from .chats import (
    ChatSession,
    ChatSessionBase,
    ChatSessionRead,
    ChatSessionCreate,
    ChatMessage,
    ChatMessageBase,
    ChatMessageRead,
    ChatMessageCreate,
    ChatSessionWithMessages,
    ChatStatsRead
)

# Analytics models
from .analytics import (
    ShopMilestone
)

__all__ = [
    # Enums
    "ProductType",
    "OrderStatus",
    "UserRole",
    "WarehouseOperationType",
    "City",
    "InvitationStatus",
    # Products
    "ProductBase",
    "Product",
    "ProductCreate",
    "ProductUpdate",
    "ProductRead",
    "ProductVariantBase",
    "ProductVariant",
    "ProductVariantCreate",
    "ProductVariantRead",
    "ProductImageBase",
    "ProductImage",
    "ProductImageCreate",
    "ProductImageRead",
    "ProductAddonBase",
    "ProductAddon",
    "ProductAddonCreate",
    "ProductAddonRead",
    "ProductBundleBase",
    "ProductBundle",
    "ProductBundleCreate",
    "ProductBundleRead",
    # Orders
    "OrderBase",
    "Order",
    "OrderCreate",
    "OrderItemRequest",
    "OrderCreateWithItems",
    "OrderUpdate",
    "OrderRead",
    "OrderItemBase",
    "OrderItem",
    "OrderItemCreate",
    "OrderItemRead",
    "OrderPhotoBase",
    "OrderPhoto",
    "OrderPhotoCreate",
    "OrderPhotoRead",
    "OrderHistoryBase",
    "OrderHistory",
    "OrderHistoryRead",
    # Warehouse
    "WarehouseItemBase",
    "WarehouseItem",
    "WarehouseItemCreate",
    "WarehouseItemUpdate",
    "WarehouseItemRead",
    "WarehouseOperationBase",
    "WarehouseOperation",
    "WarehouseOperationCreate",
    "WarehouseOperationRead",
    "WarehouseItemDetail",
    "ProductRecipeBase",
    "ProductRecipe",
    "ProductRecipeCreate",
    "ProductRecipeUpdate",
    "ProductRecipeRead",
    "ProductWithRecipe",
    "OrderReservationBase",
    "OrderReservation",
    "OrderReservationCreate",
    "OrderReservationRead",
    "IngredientAvailability",
    "ProductAvailability",
    "AvailabilityResponse",
    "InventoryCheckBase",
    "InventoryCheck",
    "InventoryCheckItemBase",
    "InventoryCheckItem",
    "InventoryCheckCreate",
    "InventoryCheckItemCreate",
    "InventoryCheckRead",
    "InventoryCheckItemRead",
    # Users
    "ClientBase",
    "Client",
    "ClientCreate",
    "ClientUpdate",
    "ClientRead",
    "UserBase",
    "User",
    "UserCreate",
    "UserUpdate",
    "UserRead",
    "UserResponse",
    "TeamInvitationBase",
    "TeamInvitation",
    "TeamInvitationCreate",
    "TeamInvitationRead",
    "LoginRequest",
    "LoginResponse",
    "TokenData",
    # Shop
    "Shop",
    "ShopCreate",
    "ShopUpdate",
    "WorkingHoursUpdate",
    "DeliverySettingsUpdate",
    "ShopRead",
    "ShopSettingsBase",
    "ShopSettings",
    "ShopSettingsUpdate",
    "ShopSettingsRead",
    "PickupLocationBase",
    "PickupLocation",
    "PickupLocationCreate",
    "PickupLocationUpdate",
    "PickupLocationRead",
    "OrderCounter",
    # Reviews
    "ProductReviewBase",
    "ProductReview",
    "ProductReviewCreate",
    "ProductReviewRead",
    "ReviewPhotoBase",
    "ReviewPhoto",
    "ReviewPhotoCreate",
    "ReviewPhotoRead",
    "CompanyReviewBase",
    "CompanyReview",
    "CompanyReviewCreate",
    "CompanyReviewRead",
    "FAQBase",
    "FAQ",
    "FAQCreate",
    "FAQUpdate",
    "FAQRead",
    "StaticPageBase",
    "StaticPage",
    "StaticPageCreate",
    "StaticPageUpdate",
    "StaticPageRead",
    # Schemas
    "CompositionItemRead",
    "ProductBundleItemRead",
    "ReviewsBreakdownRead",
    "ReviewsAggregateRead",
    "ProductDetailRead",
    # Chats
    "ChatSession",
    "ChatSessionBase",
    "ChatSessionRead",
    "ChatSessionCreate",
    "ChatMessage",
    "ChatMessageBase",
    "ChatMessageRead",
    "ChatMessageCreate",
    "ChatSessionWithMessages",
    "ChatStatsRead",
    # Analytics
    "ShopMilestone",
]

# ===============================
# Update forward references
# ===============================
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
ChatSessionRead.model_rebuild()
ChatSessionWithMessages.model_rebuild()
ChatMessageRead.model_rebuild()
