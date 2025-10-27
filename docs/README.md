# OSPF - Open Source Personal Financial
## The goal of this project is to develop a professional-grade personal finance application that is both free and open-source, designed to empower individuals with the tools they need to manage their finances effectively. The application will provide robust features comparable to commercial software, such as budgeting, expense tracking, financial planning, and investment analysis, while prioritizing user privacy and data security.

## As an open-source project, it will be community-driven, encouraging contributions from developers and users worldwide to continually improve and expand its capabilities. By offering a cost-free solution, the application aims to make high-quality financial management accessible to everyone, regardless of their financial circumstances. The ultimate objective is to help users gain better control over their financial lives, achieve their financial goals, and make informed decisions through a user-friendly, transparent, and secure platform.


### Versions

### Links

### Requirements
- Python 3.11
- Flask
- 

## Installation
```bash
pipenv shell
pipenv install
flask run
```
### Updating

### Plugins

## Roadmap and releases
### Required Models
- Users
    - Email
    - Password
    - Username
    - First Name
    - Last Name
- Institution
    - User ID
    - Name
    - Location
- Account
    - Institution ID
    - User ID
    - Name
    - Number
    - Status
    - Balance
- Categories Group
    - User ID
    - Name
- Categories Type
    - User ID
    - Name (Income, Expense, Transfer)
- Categories
    - User ID
    - Categories Group ID
    - Categories Type ID
    - Name
- Transactions
    - User ID
    - Categories ID
    - Account ID
    - Amount
    - Transaction Type
    - External ID 
    - Description

### Nice to haves
- Items (thought here is to be able to track the items that make up the transaction)
- Merchant
- Tags

## Contributing

### Credits
- Velzon
- Firefly - https://www.firefly-iii.org/
- Maybe - https://github.com/maybe-finance/maybe