def normalize_phone(phone_number):
    """
    Normalize the phone number by converting them to
    international format and deleting spaces
    """
    if '+' not in phone_number:
        prefix = phone_number[0:2]
        body = phone_number[2:10]
        phone_number = f"+33{prefix[-1]}{body}"
    phone_number = phone_number.replace(
        ' ', '').replace('-', '').replace('.', '')
    return phone_number


def normalize_email(email):
    """
    Normalize the email address by lowercasing the domain part of it.
    """
    email = email or ""
    try:
        email_name, domain_part = email.strip().rsplit("@", 1)
    except ValueError:
        pass
    else:
        email = email_name + "@" + domain_part.lower()
    return email
