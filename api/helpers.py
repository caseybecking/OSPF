from app.config import Config

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def positive_or_negative(amount):
    if amount < 0:
        return "Withdrawal"
    elif amount == 0:
        return "Deposit"
    else:
        return "Deposit"

def clean_dollar_value(amount):
    _amount = amount.replace("$", "")
    __amount = _amount.replace(",", "")
    return float(__amount)
