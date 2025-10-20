"""
Kaspi Pay Configuration Service - Multi-BIN Device Management

Handles device registration and BIN selection for r3 API.
Each BIN requires its own DeviceToken bound to (OrganizationBin, TradePointId).
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from models import KaspiPayConfig, KaspiPayLog
from core.logging import get_logger

logger = get_logger(__name__)


class KaspiConfigService:
    """Service for managing Kaspi Pay BIN configurations"""

    @staticmethod
    def get_bin_config(db: Session, shop_id: int, organization_bin: str) -> Optional[KaspiPayConfig]:
        """
        Get configuration for specific BIN

        Args:
            db: Database session
            shop_id: Shop ID
            organization_bin: 12-digit organization BIN

        Returns:
            KaspiPayConfig if found and active, None otherwise
        """
        config = db.query(KaspiPayConfig).filter(
            KaspiPayConfig.shop_id == shop_id,
            KaspiPayConfig.organization_bin == organization_bin,
            KaspiPayConfig.is_active == True
        ).first()

        if not config:
            logger.warning(
                "kaspi_config_not_found",
                shop_id=shop_id,
                organization_bin=organization_bin
            )

        return config

    @staticmethod
    def get_default_bin_config(db: Session, shop_id: int) -> Optional[KaspiPayConfig]:
        """
        Get default BIN configuration for shop

        Args:
            db: Database session
            shop_id: Shop ID

        Returns:
            Default KaspiPayConfig if set, None otherwise
        """
        config = db.query(KaspiPayConfig).filter(
            KaspiPayConfig.shop_id == shop_id,
            KaspiPayConfig.is_default == True,
            KaspiPayConfig.is_active == True
        ).first()

        if not config:
            logger.info(
                "kaspi_no_default_bin",
                shop_id=shop_id
            )

        return config

    @staticmethod
    def get_all_active_bins(db: Session, shop_id: int) -> List[KaspiPayConfig]:
        """
        Get all active BIN configurations for shop

        Args:
            db: Database session
            shop_id: Shop ID

        Returns:
            List of active KaspiPayConfig objects
        """
        configs = db.query(KaspiPayConfig).filter(
            KaspiPayConfig.shop_id == shop_id,
            KaspiPayConfig.is_active == True
        ).order_by(KaspiPayConfig.is_default.desc()).all()

        return configs

    @staticmethod
    def select_bin(
        db: Session,
        shop_id: int,
        organization_bin: Optional[str] = None
    ) -> Optional[KaspiPayConfig]:
        """
        Select BIN for payment operation

        Logic:
        1. If organization_bin specified, use it (if active)
        2. Otherwise use default BIN for shop
        3. Otherwise use first active BIN

        Args:
            db: Database session
            shop_id: Shop ID
            organization_bin: Explicit BIN to use (optional)

        Returns:
            KaspiPayConfig to use, None if no active BIN available
        """
        # Explicit BIN specified
        if organization_bin:
            config = KaspiConfigService.get_bin_config(db, shop_id, organization_bin)
            if config:
                logger.info(
                    "kaspi_bin_selected_explicit",
                    shop_id=shop_id,
                    bin=organization_bin
                )
                return config

            logger.warning(
                "kaspi_bin_not_found_or_inactive",
                shop_id=shop_id,
                bin=organization_bin
            )
            return None

        # Use default BIN
        config = KaspiConfigService.get_default_bin_config(db, shop_id)
        if config:
            logger.info(
                "kaspi_bin_selected_default",
                shop_id=shop_id,
                bin=config.organization_bin
            )
            return config

        # Use first active BIN
        all_bins = KaspiConfigService.get_all_active_bins(db, shop_id)
        if all_bins:
            config = all_bins[0]
            logger.info(
                "kaspi_bin_selected_first",
                shop_id=shop_id,
                bin=config.organization_bin
            )
            return config

        logger.error("kaspi_no_active_bins", shop_id=shop_id)
        return None

    @staticmethod
    def create_bin_config(
        db: Session,
        shop_id: int,
        organization_bin: str,
        trade_point_id: str,
        device_token: str,
        is_default: bool = False,
        description: Optional[str] = None
    ) -> KaspiPayConfig:
        """
        Create new BIN configuration

        If is_default=True and another default exists, unset the other default

        Args:
            db: Database session
            shop_id: Shop ID
            organization_bin: 12-digit BIN
            trade_point_id: TradePoint ID from r3 API
            device_token: Device token from device registration
            is_default: Whether this should be default BIN
            description: Optional description

        Returns:
            Created KaspiPayConfig
        """
        # If setting as default, unset other defaults for this shop
        if is_default:
            db.query(KaspiPayConfig).filter(
                KaspiPayConfig.shop_id == shop_id,
                KaspiPayConfig.is_default == True
            ).update({KaspiPayConfig.is_default: False})

        config = KaspiPayConfig(
            shop_id=shop_id,
            organization_bin=organization_bin,
            trade_point_id=trade_point_id,
            device_token=device_token,
            is_default=is_default,
            description=description
        )

        db.add(config)
        db.commit()
        db.refresh(config)

        logger.info(
            "kaspi_config_created",
            shop_id=shop_id,
            bin=organization_bin,
            is_default=is_default
        )

        return config

    @staticmethod
    def log_payment_operation(
        db: Session,
        shop_id: int,
        kaspi_config_id: int,
        operation_type: str,
        external_id: str,
        organization_bin: str,
        amount: int,
        status: str,
        error_message: Optional[str] = None
    ) -> KaspiPayLog:
        """
        Log Kaspi Pay operation for audit trail

        Args:
            db: Database session
            shop_id: Shop ID
            kaspi_config_id: Reference to KaspiPayConfig (can be null)
            operation_type: create, status, refund, cancel
            external_id: QrPaymentId from Kaspi
            organization_bin: BIN used for operation
            amount: Amount in kopecks
            status: success, failed, pending
            error_message: Error details if failed

        Returns:
            Created KaspiPayLog
        """
        log = KaspiPayLog(
            shop_id=shop_id,
            kaspi_config_id=kaspi_config_id,
            operation_type=operation_type,
            external_id=external_id,
            organization_bin=organization_bin,
            amount=amount,
            status=status,
            error_message=error_message
        )

        db.add(log)
        db.commit()

        logger.info(
            "kaspi_operation_logged",
            shop_id=shop_id,
            operation=operation_type,
            external_id=external_id,
            bin=organization_bin,
            status=status
        )

        return log


# ===============================
# Schema Models for API
# ===============================

from pydantic import BaseModel
from datetime import datetime


class KaspiPayConfigRead(BaseModel):
    """Kaspi Pay Config response schema"""
    id: int
    shop_id: int
    organization_bin: str
    trade_point_id: str
    is_active: bool
    is_default: bool
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class KaspiPayConfigCreate(BaseModel):
    """Kaspi Pay Config creation schema"""
    organization_bin: str
    trade_point_id: str
    device_token: str
    is_default: bool = False
    description: Optional[str] = None


class BinSelectionGuard:
    """
    Guard to prevent accidental use of wrong BIN

    Validates that organization_bin matches configured shop BINs
    """

    @staticmethod
    def validate_bin_for_shop(
        db: Session,
        shop_id: int,
        organization_bin: Optional[str]
    ) -> bool:
        """
        Validate that organization_bin is allowed for shop

        Args:
            db: Database session
            shop_id: Shop ID
            organization_bin: BIN to validate (None = use default)

        Returns:
            True if valid, False otherwise
        """
        if not organization_bin:
            # Using default is OK
            return True

        config = db.query(KaspiPayConfig).filter(
            KaspiPayConfig.shop_id == shop_id,
            KaspiPayConfig.organization_bin == organization_bin,
            KaspiPayConfig.is_active == True
        ).first()

        is_valid = config is not None

        if not is_valid:
            logger.warning(
                "bin_validation_failed",
                shop_id=shop_id,
                requested_bin=organization_bin
            )

        return is_valid
