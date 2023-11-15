from faker import Faker
from datetime import datetime
import random
import string

def get_birthdate():
    # Generate fake date
    # Initiate Faker and get a random date between 1960 and 2000
    fake = Faker()

    fake_date = fake.date_time_between(start_date=datetime(1970, 1, 1),
                                        end_date=datetime(2003, 12, 31))

    # Extract the parts of the date separately
    month = fake_date.strftime('%b')  # First 3 letters of the month
    day = fake_date.strftime('%d')    # Day
    year = fake_date.strftime('%Y')   # Year

    print(month, day, year)
    return month, day, year


def generate_username():
    while True:
        # Read the names from the file
        with open('forenames.txt', 'r') as f:
            first_names = f.readlines()
        
        with open('surnames.txt', 'r') as f:
            last_names = f.readlines()

        first_name = random.choice(first_names).strip()
        last_name = random.choice(last_names).strip()
        number = random.randint(100, 999)
        username = f"{first_name.lower()}{last_name.lower()}{number}"
        print(username)
        if username.isalnum() and len(username) >= 13:
            return username

def generate_random_password():
    password_length = 10
    # Define the characters we want to use in the password
    lower = string.ascii_lowercase
    upper = string.ascii_uppercase
    num = string.digits
    
    # Ensure the password contains at least one lowercase, one uppercase, and one number
    password_characters = random.choice(lower) + random.choice(upper) + random.choice(num)
    
    # Fill the rest of the password length with a mix of the character sets
    for _ in range(password_length - len(password_characters)):
        password_characters += random.choice(lower + upper + num)
    
    # Convert the string to a list and shuffle it to ensure a random order
    password_list = list(password_characters)
    random.SystemRandom().shuffle(password_list)
    
    # Convert the list back to a string and return
    return ''.join(password_list)