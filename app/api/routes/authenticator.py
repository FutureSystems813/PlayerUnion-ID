import bcrypt

def hash_player_password(password: str) -> str:
    """Hasht ein Passwort mit einem zufälligen Salt."""
    # Bcrypt braucht Bytes, keine Strings
    pwd_bytes = password.encode('utf-8')
    # Salt generieren und hashen (Kürzung auf 72 Bytes geschieht intern sicher)
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')

def verify_player_password(plain_password: str, hashed_password: str) -> bool:
    """Vergleicht ein Klartext-Passwort mit einem gespeicherten Hash."""
    try:
        password_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False