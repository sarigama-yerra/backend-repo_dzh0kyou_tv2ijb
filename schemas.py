"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal

# Example schemas (you can keep these for reference):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Crypto dashboard schemas

class Wallet(BaseModel):
    """
    Wallet collection schema
    Collection name: "wallet"
    """
    owner: str = Field("default", description="Wallet owner identifier")
    balance: float = Field(0, ge=0, description="Current wallet balance in USD-equivalent")
    currency: str = Field("USD", description="Display currency")

class Transaction(BaseModel):
    """
    Transactions collection schema
    Collection name: "transaction"
    """
    owner: str = Field("default", description="Wallet owner identifier")
    type: Literal["deposit", "withdrawal"] = Field(..., description="Transaction type")
    amount: float = Field(..., gt=0, description="Transaction amount")
    balance_after: Optional[float] = Field(None, ge=0, description="Balance after this transaction")
    note: Optional[str] = Field(None, description="Optional note")

# Note: The Flames database viewer will automatically:
# 1. Read these schemas from GET /schema endpoint
# 2. Use them for document validation when creating/editing
# 3. Handle all database operations (CRUD) directly
# 4. You don't need to create any database endpoints!
