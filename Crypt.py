import re
import base64
import hashlib
import hmac


PBKDF2_ITERATIONS = 600_000
class Crypt:

    #Function to convert master password and salt to cryptographic key
    @staticmethod
    def derive_key(master_password, salt):
        raw_key = hashlib.pbkdf2_hmac(
            "sha256", #hashing method
            master_password.encode(), #Encode master password into bytes
            salt,
            PBKDF2_ITERATIONS, #Amount of times the function will scramble the hash
            dklen=32 #Length of derived key in bytes
        )
        return base64.urlsafe_b64encode(raw_key) #Return the key encoded in base64

    #Function to create verifiers by encoding message with key
    @staticmethod
    def create_verifier(key):
        return hmac.new(
            key,
            b"Aegis_Master_Verifier", #string to be hashed
            hashlib.sha256 #hashing method
        ).digest()

    #Function to verify master password by using stored verifier
    @staticmethod
    def verify_master(key, stored_verifier):
        new_verifier = Crypt.create_verifier(key)
        return hmac.compare_digest(
            new_verifier,
            stored_verifier
        )

    #Function to check the strength of passwords
    @staticmethod
    def password_strength(password):

        score = 0

        if len(password) >= 8:
            score += 1

        if len(password) >= 12:
            score += 1

        if re.search(r"[A-Z]", password):
            score += 1

        if re.search(r"[a-z]", password):
            score += 1

        if re.search(r"\d", password):
            score += 1

        if re.search(
            r"""[!@#$%^&*()_+\-=\[\]{};:'",.<>/?\\|`]""",
            password
        ):
            score += 1

        if score <= 2:

            return "WEAK", 0.25

        elif score <= 4:

            return "MEDIUM", 0.60

        return "STRONG", 1.0


