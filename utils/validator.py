'''
    This python file contains functions to validate 
    entries in multiple sections of the system, from user authentication to
    assignment submissions.
'''
import re # Regex module to ensure patterns in id, password and file extensions (for submissions) are valid

# Function to validate user ID
def validate_id(user_id):
    # Initial check for if the user ID (no matter what role) is eight digits
    if not re.fullmatch(r"\d{8}", user_id):
        return 'A valid ID must have 8 digits'
    # (For faculty), checks if the user id ends with '0000'
    if user_id.endswith("0000"):
        return True
    # (For student), checks if the user id has its 4 digits
    # which describe his/ her class group is in the valid range
    # ie. from 2022 to 2028
    try:
        year = int(user_id[-4:])
        if 2022 <= year <= 2028:
            return True
        return 'Student ID year must be between 2022 and 2028.'
    except ValueError:
        return 'Invalid student ID format.'


# Function to validate if password meets requirements (to ensure password strength);
# 1. Minimum 8 characters.
# 2. At least one uppercase letter
# 3. At least one lowercase letter
# 4. At least one digit
# 5. At least one special character (e.g., !@#$%^&*).
def validate_password(password):
    # Checks the password from beginning (^) to end ($)
    if not re.fullmatch(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$',password):
        return "Password must include upper, lower, digit, special character, and be at least 8 characters."
    return True

    
# Function to ensure submissions are Python or txt files only
def is_valid_file(filename):
    return filename.endswith(".py") or filename.endswith(".txt")

'''
Extra Documentation for regex pattern in validate password
1. (?=.*[a-z])
    ?= is a positive lookahead that checks for the existence without moving the match pointer in the given string
    .* checks if there are zero or more characters before the main match
    [a-z] ensures there are one or more lower case letters in the given string
2. (?=.*[A-Z])
    [A-Z] matches any uppercase letter
3. (?=.*\d)
    \d matches any digit from 0 to 9 (can also be done using [0-9])
4. (?=.*[@$!%*?&])
    [@$!%*?&] checks if at least one of these special characters exists in the string
    
NB:// the first 4 check for existence only but the 5th defines the set of the actual 
      characters allowed as well as the minimum length

5. [A-Za-z\d@$!%*?&]{8,}
    [A-Za-z\d@$!%*?&] set of allowed characters
    {8,} minimum of 8 characters
    
# Extra tips for regex patterns for easy understanding
    The order of components of the pattern (aside ^ and $) doesn't matter and 
    must just be there.
'''