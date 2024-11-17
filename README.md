# OSPF - Open Source Personal Financial
## The goal of this will be to be  a professional grade personal finaince application, free and open-source.


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
### Models
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

- Items (thought here is to be able to track the items that make up the transaction)
- Merchant
- Tags

## Contributing

### Credits
- Velzon
- Firefly - https://www.firefly-iii.org/
- Maybe - https://github.com/maybe-finance/maybe