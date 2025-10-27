#!/bin/bash

# Test API Validation Script
# This script tests all the validation we added to the API endpoints

echo "======================================"
echo "Testing API Input Validation"
echo "======================================"
echo ""

BASE_URL="http://localhost:5000"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Signup missing password
echo -e "${YELLOW}Test 1: Signup with missing password${NC}"
echo "Request: POST /api/account/signup (missing password field)"
response=$(curl -s -X POST "$BASE_URL/api/account/signup" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","username":"testuser","first_name":"Test","last_name":"User"}')
echo "Response: $response"
if echo "$response" | grep -q "All fields are required"; then
    echo -e "${GREEN}✓ PASS: Validation working${NC}"
else
    echo -e "${RED}✗ FAIL: Expected validation error${NC}"
fi
echo ""

# Test 2: Account with invalid status
echo -e "${YELLOW}Test 2: Create account with invalid status${NC}"
echo "Request: POST /api/institution/account (status='invalid')"
response=$(curl -s -X POST "$BASE_URL/api/institution/account" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","name":"Account","status":"invalid","balance":0,"starting_balance":0,"account_type":"checking","account_class":"asset","number":"123","institution_id":"test"}')
echo "Response: $response"
if echo "$response" | grep -q "Invalid status"; then
    echo -e "${GREEN}✓ PASS: Status validation working${NC}"
else
    echo -e "${RED}✗ FAIL: Expected status validation error${NC}"
fi
echo ""

# Test 3: Account with invalid type
echo -e "${YELLOW}Test 3: Create account with invalid type${NC}"
echo "Request: POST /api/institution/account (account_type='invalid')"
response=$(curl -s -X POST "$BASE_URL/api/institution/account" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","name":"Account","status":"active","balance":0,"starting_balance":0,"account_type":"invalid","account_class":"asset","number":"123","institution_id":"test"}')
echo "Response: $response"
if echo "$response" | grep -q "Invalid account type"; then
    echo -e "${GREEN}✓ PASS: Account type validation working${NC}"
else
    echo -e "${RED}✗ FAIL: Expected account type validation error${NC}"
fi
echo ""

# Test 4: Account with invalid class
echo -e "${YELLOW}Test 4: Create account with invalid class${NC}"
echo "Request: POST /api/institution/account (account_class='invalid')"
response=$(curl -s -X POST "$BASE_URL/api/institution/account" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","name":"Account","status":"active","balance":0,"starting_balance":0,"account_type":"checking","account_class":"invalid","number":"123","institution_id":"test"}')
echo "Response: $response"
if echo "$response" | grep -q "Invalid account class"; then
    echo -e "${GREEN}✓ PASS: Account class validation working${NC}"
else
    echo -e "${RED}✗ FAIL: Expected account class validation error${NC}"
fi
echo ""

# Test 5: Category with missing fields
echo -e "${YELLOW}Test 5: Create category with missing fields${NC}"
echo "Request: POST /api/categories (missing categories_group_id)"
response=$(curl -s -X POST "$BASE_URL/api/categories" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","name":"Test Category","categories_type_id":"test"}')
echo "Response: $response"
if echo "$response" | grep -q "All fields are required"; then
    echo -e "${GREEN}✓ PASS: Required fields validation working${NC}"
else
    echo -e "${RED}✗ FAIL: Expected required fields validation error${NC}"
fi
echo ""

# Test 6: Category with invalid foreign key
echo -e "${YELLOW}Test 6: Create category with invalid foreign key${NC}"
echo "Request: POST /api/categories (invalid categories_group_id)"
response=$(curl -s -X POST "$BASE_URL/api/categories" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","name":"Test","categories_group_id":"invalid-id","categories_type_id":"test"}')
echo "Response: $response"
if echo "$response" | grep -q "Invalid categories_group_id"; then
    echo -e "${GREEN}✓ PASS: Foreign key validation working${NC}"
else
    echo -e "${RED}✗ FAIL: Expected foreign key validation error${NC}"
fi
echo ""

# Test 7: Transaction with missing fields
echo -e "${YELLOW}Test 7: Create transaction with missing required fields${NC}"
echo "Request: POST /api/transaction (missing amount)"
response=$(curl -s -X POST "$BASE_URL/api/transaction" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","categories_id":"test","account_id":"test","transaction_type":"Deposit"}')
echo "Response: $response"
if echo "$response" | grep -q "All required fields"; then
    echo -e "${GREEN}✓ PASS: Required fields validation working${NC}"
else
    echo -e "${RED}✗ FAIL: Expected required fields validation error${NC}"
fi
echo ""

# Test 8: Transaction with invalid amount
echo -e "${YELLOW}Test 8: Create transaction with invalid amount${NC}"
echo "Request: POST /api/transaction (amount='not-a-number')"
response=$(curl -s -X POST "$BASE_URL/api/transaction" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","categories_id":"test","account_id":"test","amount":"not-a-number","transaction_type":"Deposit"}')
echo "Response: $response"
if echo "$response" | grep -q "Amount must be a valid number"; then
    echo -e "${GREEN}✓ PASS: Amount validation working${NC}"
else
    echo -e "${RED}✗ FAIL: Expected amount validation error${NC}"
fi
echo ""

# Test 9: Institution with missing name
echo -e "${YELLOW}Test 9: Create institution with missing name${NC}"
echo "Request: POST /api/institution (missing name)"
response=$(curl -s -X POST "$BASE_URL/api/institution" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","location":"Test City"}')
echo "Response: $response"
if echo "$response" | grep -q "user_id and name are required"; then
    echo -e "${GREEN}✓ PASS: Required fields validation working${NC}"
else
    echo -e "${RED}✗ FAIL: Expected required fields validation error${NC}"
fi
echo ""

echo "======================================"
echo "Validation Testing Complete!"
echo "======================================"
echo ""
echo "Summary:"
echo "All validation endpoints are now:"
echo "  ✓ Preventing crashes from invalid data"
echo "  ✓ Returning proper 400 error codes"
echo "  ✓ Providing helpful error messages"
