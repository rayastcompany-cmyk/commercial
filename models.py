import hashlib
import os
from datetime import datetime
from sqlalchemy import (Column, Integer, Float, String, Text, Boolean, ForeignKey, DateTime,
                        UniqueConstraint)
from sqlalchemy.orm import relationship
from database import Base

ROLES = ["Buyer", "Seller", "Consignee", "Supplier", "Trader", "End User", "Importer",
         "Exporter", "Distributor", "Agent", "Broker", "Manufacturer", "Producer", "Customer"]
POSITIONS = ["مدیرعامل", "مدیر بازرگانی", "مدیر خرید", "مدیر فروش", "مدیر واردات", "مدیر صادرات",
             "مدیر لجستیک", "مدیر مالی", "کارشناس تدارکات", "سایر"]
LEAD_STATUS = ["New", "Contacted", "Negotiating", "Quotation", "PI", "Contract", "Won", "Lost"]
PI_STATUS = ["Draft", "Sent", "Confirmed", "Shipped", "Closed", "Cancelled"]
IMAGE_KINDS = ["محصول", "بسته‌بندی", "بشکه", "کیسه", "کارخانه", "سایر"]


def hash_pw(raw):
    salt = os.environ.get("CS_SALT", "commercial-system-v1")
    return hashlib.sha256((salt + raw).encode("utf-8")).hexdigest()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    password = Column(String(200), nullable=False)
    full_name = Column(String(200))
    role = Column(String(50), default="User")  # Admin / Sales / Viewer
    active = Column(Boolean, default=True)


class MyCompany(Base):
    __tablename__ = "my_company"
    id = Column(Integer, primary_key=True)
    name = Column(String(250))
    name_fa = Column(String(250))
    tagline = Column(String(250))
    address = Column(Text)
    phone = Column(String(100))
    email = Column(String(200))
    website = Column(String(200))
    whatsapp = Column(String(100))
    linkedin = Column(String(200))
    about = Column(Text)
    markets = Column(Text)
    logo = Column(String(300))
    bank_name = Column(String(200))
    beneficiary = Column(String(200))
    account_no = Column(String(150))
    iban = Column(String(100))
    swift = Column(String(50))
    bank_address = Column(Text)


class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True)
    company_name_fa = Column(String(250), nullable=False)
    company_name_en = Column(String(250))
    country = Column(String(100))
    city = Column(String(100))
    address = Column(Text)
    phone = Column(String(100))
    mobile = Column(String(100))
    email = Column(String(200))
    website = Column(String(300))
    whatsapp = Column(String(100))
    linkedin = Column(String(300))
    company_type = Column(String(200))
    tax_id = Column(String(100))
    registration_no = Column(String(100))
    products_text = Column(Text)
    public_relation = Column(Text)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    contacts = relationship("Contact", back_populates="company", cascade="all, delete-orphan")
    roles = relationship("CompanyRole", back_populates="company", cascade="all, delete-orphan")
    products = relationship("CompanyProduct", back_populates="company", cascade="all, delete-orphan")

    @property
    def role_list(self):
        return [r.role for r in self.roles]


class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    position = Column(String(150))
    department = Column(String(150))
    phone = Column(String(100))
    mobile = Column(String(100))
    email = Column(String(200))
    whatsapp = Column(String(100))
    linkedin = Column(String(300))
    is_decision_maker = Column(Boolean, default=False)
    notes = Column(Text)
    company = relationship("Company", back_populates="contacts")

    @property
    def full_name(self):
        return f"{self.first_name or ''} {self.last_name or ''}".strip()


class CompanyRole(Base):
    __tablename__ = "company_roles"
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    role = Column(String(80), nullable=False)
    company = relationship("Company", back_populates="roles")
    __table_args__ = (UniqueConstraint("company_id", "role", name="uq_company_role"),)


class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name_fa = Column(String(250), nullable=False)
    name_en = Column(String(250))
    product_code = Column(String(100))
    hs_code = Column(String(50))
    category = Column(String(150))
    subcategory = Column(String(150))
    description = Column(Text)
    origin = Column(String(150))
    packaging = Column(String(150))
    moq = Column(String(100))
    available_qty = Column(Float)
    unit = Column(String(50))
    price = Column(Float)
    currency = Column(String(20))
    incoterm = Column(String(20))
    loading_port = Column(String(150))
    destination = Column(String(150))
    status = Column(String(50), default="Active")
    specifications = relationship("ProductSpecification", back_populates="product",
                                  cascade="all, delete-orphan", order_by="ProductSpecification.sort")
    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")


class ProductSpecification(Base):
    __tablename__ = "product_specifications"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    parameter = Column(String(150), nullable=False)
    value = Column(String(250))
    method = Column(String(150))
    sort = Column(Integer, default=0)
    product = relationship("Product", back_populates="specifications")


class ProductImage(Base):
    __tablename__ = "product_images"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    path = Column(String(400))
    kind = Column(String(50))
    product = relationship("Product", back_populates="images")


class CompanyProduct(Base):
    __tablename__ = "company_products"
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    relation = Column(String(50))  # Supplies / Buys / Produces / Interested
    company = relationship("Company", back_populates="products")
    product = relationship("Product")


class Lead(Base):
    __tablename__ = "leads"
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    company_name = Column(String(250))
    country = Column(String(100))
    contact = Column(String(200))
    product = Column(String(250))
    source = Column(String(150))
    date_added = Column(String(20))
    sales_person = Column(String(150))
    status = Column(String(30), default="New")
    priority = Column(String(20), default="Medium")
    next_followup = Column(String(20))
    notes = Column(Text)


class PI(Base):
    __tablename__ = "pis"
    id = Column(Integer, primary_key=True)
    pi_no = Column(String(80), unique=True, nullable=False)
    pi_date = Column(String(20))
    validity_days = Column(Integer, default=30)
    buyer_id = Column(Integer, ForeignKey("companies.id"))
    consignee_id = Column(Integer, ForeignKey("companies.id"))
    currency = Column(String(20), default="USD")
    incoterm = Column(String(20))
    payment_terms = Column(String(250))
    delivery = Column(String(250))
    packing = Column(String(250))
    origin = Column(String(150))
    loading_port = Column(String(150))
    discharge_port = Column(String(150))
    remark = Column(Text)
    status = Column(String(30), default="Draft")
    total = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.now)
    buyer = relationship("Company", foreign_keys=[buyer_id])
    consignee = relationship("Company", foreign_keys=[consignee_id])
    items = relationship("PIItem", back_populates="pi", cascade="all, delete-orphan",
                         order_by="PIItem.sort")
    payments = relationship("Payment", back_populates="pi", cascade="all, delete-orphan")


class PIItem(Base):
    __tablename__ = "pi_items"
    id = Column(Integer, primary_key=True)
    pi_id = Column(Integer, ForeignKey("pis.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"))
    description = Column(String(300))
    spec = Column(Text)
    qty = Column(Float, default=0)
    unit = Column(String(50))
    unit_price = Column(Float, default=0)
    amount = Column(Float, default=0)
    sort = Column(Integer, default=0)
    pi = relationship("PI", back_populates="items")


class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True)
    pi_id = Column(Integer, ForeignKey("pis.id"), nullable=False)
    pay_date = Column(String(20))
    amount = Column(Float, default=0)
    currency = Column(String(20))
    method = Column(String(100))
    reference = Column(String(200))
    notes = Column(Text)
    pi = relationship("PI", back_populates="payments")
