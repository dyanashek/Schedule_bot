import re


def validate_weight(weight):
    try:
        weight = int(weight)
        if 35 <= weight <= 150:
            return weight
    except:
        return False
    
    return False


def validate_height(height):
    try:
        height = int(height)
        if 130 <= height <= 250:
            return height
    except:
        return False
    
    return False


def validate_age(age):
    try:
        age = int(age)
        if 10 <= age <= 100:
            return age
    except:
        return False
    
    return False


def extract_digits(input_string):
    return re.sub(r'\D', '', input_string)


def validate_phone(phone):
    phone = extract_digits(phone)
    if len(phone) == 11 and (phone.startswith('7') or phone.startswith('8')):
        return phone
    else:
        return False


def escape_markdown(text):
    characters_to_escape = ['_', '*', '[', ']', '`']
    for char in characters_to_escape:
        text = text.replace(char, '\\' + char)

    return text