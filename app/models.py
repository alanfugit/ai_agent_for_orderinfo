from sqlalchemy import Column, Integer, String, Decimal, DateTime, Boolean, Text, Date
from .database import Base

class Order(Base):
    __tablename__ = "order"

    order_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, default=0)
    customer_group_id = Column(Integer, default=0)
    firstname = Column(String(32))
    lastname = Column(String(32))
    email = Column(String(96))
    telephone = Column(String(32))
    fax = Column(String(32))
    total = Column(Decimal(15, 4), default=0.0000)
    order_status_id = Column(Integer, default=0)
    date_added = Column(DateTime)
    date_modified = Column(DateTime)

class OrderProduct(Base):
    __tablename__ = "order_product"

    order_product_id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer)
    product_id = Column(Integer)
    name = Column(String(255))
    model = Column(String(64))
    quantity = Column(Integer)
    price = Column(Decimal(15, 4), default=0.0000)
    total = Column(Decimal(15, 4), default=0.0000)
    tax = Column(Decimal(15, 4), default=0.0000)
    reward = Column(Integer)

class Customer(Base):
    __tablename__ = "customer"

    customer_id = Column(Integer, primary_key=True, index=True)
    firstname = Column(String(50))
    lastname = Column(String(50))
    email = Column(String(96))
    telephone = Column(String(32))
    fax = Column(String(32))
    cart = Column(Text)
    wishlist = Column(Text)
    newsletter = Column(Boolean, default=False)
    address_id = Column(Integer, default=0)
    custom_field = Column(Text)
    ip = Column(String(40))
    status = Column(Boolean)
    lastEmpDate = Column(Date)
    approved = Column(Boolean)
    safe = Column(Boolean)
    token = Column(String(255))
    date_added = Column(DateTime)
