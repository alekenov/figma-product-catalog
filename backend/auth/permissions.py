"""
Role-based permission system for Kazakhstan flower shop.

Defines permissions for different user roles:
- Director: all permissions + team management
- Manager: orders, clients, products management
- Florist: orders view/update, warehouse access
- Courier: orders delivery status only
"""

from enum import Enum
from typing import Set, Dict, List
from functools import wraps
from fastapi import HTTPException, status, Depends
from models import UserRole


class Permission(str, Enum):
    """Available permissions in the system"""

    # Order permissions
    VIEW_ORDERS = "view_orders"
    CREATE_ORDERS = "create_orders"
    UPDATE_ORDERS = "update_orders"
    DELETE_ORDERS = "delete_orders"
    MANAGE_ORDER_STATUS = "manage_order_status"
    VIEW_ORDER_DETAILS = "view_order_details"
    UPDATE_DELIVERY_STATUS = "update_delivery_status"

    # Product permissions
    VIEW_PRODUCTS = "view_products"
    CREATE_PRODUCTS = "create_products"
    UPDATE_PRODUCTS = "update_products"
    DELETE_PRODUCTS = "delete_products"
    MANAGE_PRODUCT_RECIPES = "manage_product_recipes"

    # Warehouse/Inventory permissions
    VIEW_WAREHOUSE = "view_warehouse"
    UPDATE_WAREHOUSE = "update_warehouse"
    CREATE_WAREHOUSE_ITEMS = "create_warehouse_items"
    DELETE_WAREHOUSE_ITEMS = "delete_warehouse_items"
    CONDUCT_INVENTORY_CHECKS = "conduct_inventory_checks"

    # Client permissions
    VIEW_CLIENTS = "view_clients"
    CREATE_CLIENTS = "create_clients"
    UPDATE_CLIENTS = "update_clients"
    DELETE_CLIENTS = "delete_clients"

    # Team management permissions
    VIEW_TEAM_MEMBERS = "view_team_members"
    INVITE_TEAM_MEMBERS = "invite_team_members"
    REMOVE_TEAM_MEMBERS = "remove_team_members"
    UPDATE_TEAM_ROLES = "update_team_roles"

    # Shop settings permissions
    VIEW_SHOP_SETTINGS = "view_shop_settings"
    UPDATE_SHOP_SETTINGS = "update_shop_settings"

    # Analytics permissions
    VIEW_ANALYTICS = "view_analytics"
    EXPORT_REPORTS = "export_reports"


# Role-based permission mapping
ROLE_PERMISSIONS: Dict[UserRole, Set[Permission]] = {
    UserRole.DIRECTOR: {
        # All permissions - director has full access
        Permission.VIEW_ORDERS,
        Permission.CREATE_ORDERS,
        Permission.UPDATE_ORDERS,
        Permission.DELETE_ORDERS,
        Permission.MANAGE_ORDER_STATUS,
        Permission.VIEW_ORDER_DETAILS,
        Permission.UPDATE_DELIVERY_STATUS,

        Permission.VIEW_PRODUCTS,
        Permission.CREATE_PRODUCTS,
        Permission.UPDATE_PRODUCTS,
        Permission.DELETE_PRODUCTS,
        Permission.MANAGE_PRODUCT_RECIPES,

        Permission.VIEW_WAREHOUSE,
        Permission.UPDATE_WAREHOUSE,
        Permission.CREATE_WAREHOUSE_ITEMS,
        Permission.DELETE_WAREHOUSE_ITEMS,
        Permission.CONDUCT_INVENTORY_CHECKS,

        Permission.VIEW_CLIENTS,
        Permission.CREATE_CLIENTS,
        Permission.UPDATE_CLIENTS,
        Permission.DELETE_CLIENTS,

        Permission.VIEW_TEAM_MEMBERS,
        Permission.INVITE_TEAM_MEMBERS,
        Permission.REMOVE_TEAM_MEMBERS,
        Permission.UPDATE_TEAM_ROLES,

        Permission.VIEW_SHOP_SETTINGS,
        Permission.UPDATE_SHOP_SETTINGS,

        Permission.VIEW_ANALYTICS,
        Permission.EXPORT_REPORTS,
    },

    UserRole.MANAGER: {
        # Manager: orders, clients, products management
        Permission.VIEW_ORDERS,
        Permission.CREATE_ORDERS,
        Permission.UPDATE_ORDERS,
        Permission.MANAGE_ORDER_STATUS,
        Permission.VIEW_ORDER_DETAILS,

        Permission.VIEW_PRODUCTS,
        Permission.CREATE_PRODUCTS,
        Permission.UPDATE_PRODUCTS,
        Permission.MANAGE_PRODUCT_RECIPES,

        Permission.VIEW_WAREHOUSE,
        Permission.UPDATE_WAREHOUSE,
        Permission.CONDUCT_INVENTORY_CHECKS,

        Permission.VIEW_CLIENTS,
        Permission.CREATE_CLIENTS,
        Permission.UPDATE_CLIENTS,

        Permission.VIEW_TEAM_MEMBERS,

        Permission.VIEW_SHOP_SETTINGS,

        Permission.VIEW_ANALYTICS,
    },

    UserRole.FLORIST: {
        # Florist: orders view/update, warehouse access
        Permission.VIEW_ORDERS,
        Permission.UPDATE_ORDERS,
        Permission.MANAGE_ORDER_STATUS,
        Permission.VIEW_ORDER_DETAILS,

        Permission.VIEW_PRODUCTS,
        Permission.MANAGE_PRODUCT_RECIPES,

        Permission.VIEW_WAREHOUSE,
        Permission.UPDATE_WAREHOUSE,
        Permission.CONDUCT_INVENTORY_CHECKS,

        Permission.VIEW_CLIENTS,
    },

    UserRole.COURIER: {
        # Courier: orders delivery status only
        Permission.VIEW_ORDERS,
        Permission.VIEW_ORDER_DETAILS,
        Permission.UPDATE_DELIVERY_STATUS,

        Permission.VIEW_CLIENTS,  # Need to see delivery info
    }
}


def get_user_permissions(role: UserRole) -> Set[Permission]:
    """
    Get all permissions for a given user role.

    Args:
        role: User role from UserRole enum

    Returns:
        Set of Permission enums for the role

    Example:
        permissions = get_user_permissions(UserRole.MANAGER)
        if Permission.CREATE_ORDERS in permissions:
            # User can create orders
    """
    return ROLE_PERMISSIONS.get(role, set())


def has_permission(user_role: UserRole, required_permission: Permission) -> bool:
    """
    Check if a user role has a specific permission.

    Args:
        user_role: The user's role
        required_permission: The permission to check

    Returns:
        True if user has permission, False otherwise

    Example:
        if has_permission(user.role, Permission.DELETE_PRODUCTS):
            # User can delete products
    """
    user_permissions = get_user_permissions(user_role)
    return required_permission in user_permissions


def require_permission(permission: Permission):
    """
    Decorator to check if current user has required permission.

    Args:
        permission: Required permission

    Raises:
        HTTPException: If user lacks permission

    Usage:
        @require_permission(Permission.CREATE_PRODUCTS)
        async def create_product(product: ProductCreate):
            # Only users with CREATE_PRODUCTS permission can access
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract current user from kwargs (injected by dependency)
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )

            if not has_permission(current_user.role, permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required: {permission.value}"
                )

            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_any_permission(*permissions: Permission):
    """
    Decorator to check if current user has any of the required permissions.

    Args:
        permissions: List of acceptable permissions

    Raises:
        HTTPException: If user lacks all permissions

    Usage:
        @require_any_permission(Permission.UPDATE_ORDERS, Permission.MANAGE_ORDER_STATUS)
        async def update_order_status():
            # User needs either permission to access
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )

            user_permissions = get_user_permissions(current_user.role)
            has_any_permission = any(perm in user_permissions for perm in permissions)

            if not has_any_permission:
                required_perms = [perm.value for perm in permissions]
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required one of: {required_perms}"
                )

            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_role(role: UserRole):
    """
    Decorator to check if current user has specific role.

    Args:
        role: Required user role

    Raises:
        HTTPException: If user has different role

    Usage:
        @require_role(UserRole.DIRECTOR)
        async def director_only_function():
            # Only directors can access
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )

            if current_user.role != role:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access restricted to {role.value} role only"
                )

            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_any_role(*roles: UserRole):
    """
    Decorator to check if current user has any of the required roles.

    Args:
        roles: List of acceptable roles

    Raises:
        HTTPException: If user has none of the required roles

    Usage:
        @require_any_role(UserRole.DIRECTOR, UserRole.MANAGER)
        async def management_only_function():
            # Directors or managers can access
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )

            if current_user.role not in roles:
                role_names = [role.value for role in roles]
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access restricted to roles: {role_names}"
                )

            return await func(*args, **kwargs)
        return wrapper
    return decorator


# Permission groups for common use cases
MANAGEMENT_PERMISSIONS = {
    Permission.VIEW_ANALYTICS,
    Permission.EXPORT_REPORTS,
    Permission.VIEW_TEAM_MEMBERS,
    Permission.UPDATE_SHOP_SETTINGS,
}

WAREHOUSE_PERMISSIONS = {
    Permission.VIEW_WAREHOUSE,
    Permission.UPDATE_WAREHOUSE,
    Permission.CONDUCT_INVENTORY_CHECKS,
}

ORDER_MANAGEMENT_PERMISSIONS = {
    Permission.VIEW_ORDERS,
    Permission.CREATE_ORDERS,
    Permission.UPDATE_ORDERS,
    Permission.MANAGE_ORDER_STATUS,
}


def get_permission_summary(role: UserRole) -> Dict[str, List[str]]:
    """
    Get a human-readable summary of permissions for a role.

    Args:
        role: User role

    Returns:
        Dictionary with categorized permission descriptions

    Example:
        summary = get_permission_summary(UserRole.MANAGER)
        print(summary["orders"])  # List of order-related permissions
    """
    permissions = get_user_permissions(role)

    summary = {
        "orders": [],
        "products": [],
        "warehouse": [],
        "clients": [],
        "team": [],
        "settings": [],
        "analytics": []
    }

    for perm in permissions:
        if "order" in perm.value:
            summary["orders"].append(perm.value)
        elif "product" in perm.value:
            summary["products"].append(perm.value)
        elif "warehouse" in perm.value or "inventory" in perm.value:
            summary["warehouse"].append(perm.value)
        elif "client" in perm.value:
            summary["clients"].append(perm.value)
        elif "team" in perm.value:
            summary["team"].append(perm.value)
        elif "settings" in perm.value:
            summary["settings"].append(perm.value)
        elif "analytics" in perm.value or "report" in perm.value:
            summary["analytics"].append(perm.value)

    return summary