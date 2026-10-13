from sqlalchemy import ForeignKey
from sqlalchemy import  String, Integer, Float, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


# =====================================================
# USER
# =====================================================

class User(Base):

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    full_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True
    )

    password: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )


# =====================================================
# PRODUCT
# =====================================================

class Product(Base):

    __tablename__ = "products"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id")
           
        )

    product_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    buying_price: Mapped[float] = mapped_column(
        Float,
        default=0
    )

    selling_price: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )



# =====================================================
# PURCHASE
# =====================================================

class Purchase(Base):

    __tablename__ = "purchases"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"),
        nullable=False
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    buying_price: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    total_price: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )


# =====================================================
# SALES
# =====================================================

class Sales(Base):

    __tablename__ = "sales"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )


# =====================================================
# PAYMENTS
# =====================================================

class Payments(Base):

    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    sale_id: Mapped[int] = mapped_column(
        ForeignKey("sales.id"),
        nullable=False
    )

    paid_amount: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    trans_code: Mapped[str] = mapped_column(
        String(100)
    )
    mrid: Mapped[str] = mapped_column(String)
    crid: Mapped[str] = mapped_column(String)
    status:Mapped[str] = mapped_column(String, default="pending")
    phone_number:Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(
            DateTime,
            default=datetime.utcnow
    )    




# =====================================================
# SALES DETAILS
# =====================================================

class SalesDetails(Base):

    __tablename__ = "sales_details"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"),
        nullable=False
    )

    sale_id: Mapped[int] = mapped_column(
        ForeignKey("sales.id"),
        nullable=False
    )

    product: Mapped["Product"] = relationship()

    sales: Mapped["Sales"] = relationship()