#!/usr/bin/env python3
"""
Script to create a user in the OSPF database.
Usage: python scripts/create_user.py
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from api.user.models import User
from werkzeug.security import generate_password_hash

def create_user():
    """Create a user with specified details."""
    
    # Create the Flask app and push context
    app = create_app()
    
    with app.app_context():
        # User details
        email = "me@user.com"
        username = "username"
        first_name = "first_name"
        last_name = "last_name"
        password = "password"
        
        # Check if user already exists
        existing_user = User.query.filter(
            (User.email == email) | (User.username == username)
        ).first()
        
        if existing_user:
            print(f"User already exists!")
            print(f"   Email: {existing_user.email}")
            print(f"   Username: {existing_user.username}")
            print(f"   User ID: {existing_user.id}")
            return
        
        # Hash the password
        hashed_password = generate_password_hash(password, method='scrypt')
        
        # Create the user
        user = User(
            email=email,
            username=username,
            password=hashed_password,
            first_name=first_name,
            last_name=last_name
        )
        
        try:
            # Save to database
            user.save()
            
            print(f"User created successfully!")
            print(f"   Email: {user.email}")
            print(f"   Username: {user.username}")
            print(f"   Name: {user.first_name} {user.last_name}")
            print(f"   User ID: {user.id}")
            print(f"   Created: {user.created_at}")
            
        except Exception as e:
            print(f"Error creating user: {e}")
            db.session.rollback()

if __name__ == "__main__":
    create_user()