from sqlalchemy import ForeignKey
from sqlalchemy import  String, Integer, Float
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

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
    buying_price : Mapped[float] = mapped_column(Float)
    selling_price : Mapped[float] = mapped_column(Float)

class Purchase(Base):
    __tablename__ = "purchase"
    id : Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id : Mapped[int] = mapped_column(ForeignKey("products.id"))
    buying_price : Mapped[float] = mapped_column(Float)
    selling_price : Mapped[float] = mapped_column(Float)


class Payments(Base):
    __tablename__ = "payments"
    id : Mapped[int] = mapped_column(Integer, primary_key=True)
    sale_id : Mapped[int] = mapped_column(ForeignKey("sales.id"))
    buying_price : Mapped[float] = mapped_column(Float)
    selling_price : Mapped[float] = mapped_column(Float)


class Sales(Base):
    __tablename__ = "sales"
    id : Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id : Mapped[int] = mapped_column(ForeignKey("users.id"))
    buying_price : Mapped[float] = mapped_column(Float)
    selling_price : Mapped[float] = mapped_column(Float)


class SalesDetails(Base):
    __tablename__ = "sales_details"
    id : Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id : Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    sale_id : Mapped[int] = mapped_column(ForeignKey("sales.id"))
    buying_price : Mapped[float] = mapped_column(Float, nullable=False)
    selling_price : Mapped[float] = mapped_column(Float, nullable=False) 

    product: Mapped["Product"] = relationship()
    sales: Mapped["Sales"] = relationship()   

   