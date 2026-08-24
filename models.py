from sqlalchemy import ForeignKey
from sqlalchemy import  String, Integer, Float, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from datetime import datetime

Base =declarative_base()

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_name : Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(100))
    password: Mapped[str] = mapped_column(String(200))


class Product(Base):
    __tablename__ = "products"
    id : Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id : Mapped[int] = mapped_column(ForeignKey("users.id"))
    product_name : Mapped[str] = mapped_column(ForeignKey("products.id"))
    buying_price : Mapped[float] = mapped_column(Float)
    selling_price : Mapped[float] = mapped_column(Float)

class Purchase(Base):
    __tablename__ = "purchases"
    id : Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id : Mapped[int] = mapped_column(ForeignKey("products.id"))
    paid_amount : Mapped[float] = mapped_column(Float)
    created_at : Mapped[datetime] = mapped_column(DateTime)


class Payments(Base):
    __tablename__ = "payments"
    id : Mapped[int] = mapped_column(Integer, primary_key=True)
    sale_id : Mapped[int] = mapped_column(ForeignKey("sales.id"))
    paid_amount : Mapped[float] = mapped_column(Float)
    trans_code : Mapped[str] = mapped_column(String)
   

class Sales(Base):
    __tablename__ = "sales"
    id : Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id : Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at : Mapped[datetime] = mapped_column(DateTime)

class SalesDetails(Base):
    __tablename__ = "sales_details"
    id : Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id : Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    sale_id : Mapped[int] = mapped_column(ForeignKey("sales.id"))

    product: Mapped["Product"] = relationship()
    sales: Mapped["Sales"] = relationship()   

   