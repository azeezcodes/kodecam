from fastapi import Cookie, FastAPI, Form, Header, Path, Query, Depends, UploadFile, Response, status, HTTPException, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ValidationError, EmailStr
from typing import Annotated, List, Optional
from fastapi.encoders import jsonable_encoder
from passlib.context import CryptContext


app = FastAPI()

pwd_hash_config = CryptContext(schemes=["bcrypt"])

fake_db = {
    "user1" : {
        "name" : "John",
        "hashedPassword" : "th4tevbeurgnu5"
    },
    "user2" : {
        "name" : "Mary",
        "hashedPassword" : "th4tevbeurgnu5"
    }
}

# -------------------------------QUESTION ONE
class BlogPostRequest(BaseModel):
    title: str
    content: str
    author: Optional[str] = None

class BlogPostResponse(BaseModel):
    id: int
    title: str
    content: str
    author: Optional[str]

class ErrorResponse(BaseModel):
    detail: str    

blog_posts = []

unique_blog_id = 1

@app.post("/blog",  response_model=BlogPostResponse, status_code=201, responses={400: {"model": ErrorResponse}})
def blogPostCreate(blog: BlogPostRequest):
   global unique_blog_id  
   newBlog = {
       "id" : unique_blog_id,
       "title" : blog.title,
       "content" : blog.content,
       "author" : blog.author
   }
   blog_posts.append(newBlog)
   unique_blog_id += 1
   return newBlog
   
  
@app.get("/getBlog")
def getBlog():
    return blog_posts

# --------------END-----------------QUESTION ONE

# -------------------------------QUESTION TWO
all_profile = []

@app.post("/profile")
def createProfile(name:Annotated[str, Form(min_length=5)], email:Annotated[EmailStr, Form(max_length=50)], image: Annotated[UploadFile, File()]):
   
    # max size of file is 10 MB
    if image.size > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File size too large. Max size is 10 MB.")
    
    new_profile = {
        "id": len(all_profile) + 1,
        "name" : name,
        "email" : email,
        "image" : image.filename
    }
    all_profile.append(new_profile)
    return  new_profile

class Profile(BaseModel):
    id: int
    name: Optional[str] = Form()
    email: Optional[EmailStr] = Form()
    image: Optional[UploadFile] = None


@app.post("/update/profile")
def update_profile(updateData: Profile):
    profile = next((profile for profile in all_profile if profile["id"] == updateData.id), None)
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    if updateData.name:
        profile["name"] = updateData.name
    if updateData.email:
        profile["email"] = updateData.email
    if updateData.image:
        # Check file size for the new image
        if updateData.image.size > 10 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="File size too large. Max size is 10 MB.")
        profile["image"] = updateData.image.filename
    
    return JSONResponse(content=jsonable_encoder(profile))

# -----------------END--------------QUESTION TWO

# -------------------------------QUESTION Three
products = [
    {"id": 1, "name": "Laptop", "category": "Electronics", "price": 1000},
    {"id": 2, "name": "Smartphone", "category": "Electronics", "price": 500},
    {"id": 3, "name": "Tablet", "category": "Electronics", "price": 300},
    {"id": 4, "name": "Headphones", "category": "Accessories", "price": 100},
    {"id": 5, "name": "Backpack", "category": "Accessories", "price": 50},
]
class Product(BaseModel):
    id: int
    name: str
    category: str
    price: float

class Pagination(BaseModel):
    total_results: int
    current_page: int
    page_size: int
    total_pages: int

class ProductSearchResponse(BaseModel):
    products: List[Product]
    pagination: Pagination

@app.get("/search/product")
def searchProductWithPagination(search:Annotated[str,  Query()], category:Annotated[str,  Query()], priceRange:Annotated[float,  Query()], pageNumber: Optional[int]= None, pageSize: Optional[int]= None):
    return
# -----------------END--------------QUESTION Three

# -------------------------------QUESTION Four
@app.post("/signup")
def signUpLogic(username:Annotated[str, Form()], password:Annotated[str, Form()]):
   if username in fake_db:
        raise HTTPException(status_code=404, detail="user already exist")
    
    
   hashed_Password = pwd_hash_config.hash(password)
    
   fake_db[username] = {
        "username": username,
        "hashedPassword": hashed_Password
    }
   
   return {"name" : username, "password" : hashed_Password}
# -----------------END--------------QUESTION Four


# -----------------END--------------QUESTION Five
products = [
    {"id": 1, "name": "Laptop", "category": "Electronics", "price": 1000, "stock": 5},
    {"id": 2, "name": "Smartphone", "category": "Electronics", "price": 500, "stock": 10},
    {"id": 3, "name": "Tablet", "category": "Electronics", "price": 300, "stock": 7},
]

# In-memory shopping cart
cart = []

class CartItem(BaseModel):
    product_id: int
    quantity: int

class SuccessResponse(BaseModel):
    message: str

@app.post("/cart", response_model=SuccessResponse)
def add_to_cart(product_id: int = Form(), quantity: int = Form()):

    product = next((p for p in products if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=400, detail="Invalid product ID")
    
    if product["stock"] < quantity:
        raise HTTPException(status_code=400, detail="Not enough stock available")

    # check if product is already in cart
    cart_item = next((item for item in cart if item["product_id"] == product_id), None)
    if cart_item:
        # update quantity
        cart_item["quantity"] += quantity
    else:
        # Add new item to cart
        cart.append({"product_id": product_id, "quantity": quantity})
    
    return SuccessResponse(message="Item added to cart")

@app.delete("/cart", response_model=SuccessResponse)
def remove_from_cart(product_id: int = Query()):
    global cart
    # Validate product ID
    cart_item = next((item for item in cart if item["product_id"] == product_id), None)
    if not cart_item:
        raise HTTPException(status_code=400, detail="Product not in cart")

    cart = [item for item in cart if item["product_id"] != product_id]
    
    return SuccessResponse(message="Item removed from cart")

@app.put("/cart", response_model=SuccessResponse)
def update_cart(product_id: int = Form(), quantity: int = Form()):
    # Validate product ID
    cart_item = next((item for item in cart if item["product_id"] == product_id), None)
    if not cart_item:
        raise HTTPException(status_code=400, detail="Product not in cart")

    if quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be greater than zero")

    product = next((p for p in products if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=400, detail="Invalid product ID")
    if product["stock"] < quantity:
        raise HTTPException(status_code=400, detail="Not enough stock available")
    
    # Update quantity
    cart_item["quantity"] = quantity
    
    return SuccessResponse(message="Cart updated")
# -----------------END--------------QUESTION Five



    
    