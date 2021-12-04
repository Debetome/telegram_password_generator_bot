TABLES = {
    "passwords": """
        CREATE TABLE IF NOT EXISTS Passwords(
            \"Id\" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
            \"Title\" TEXT NOT NULL,
            \"Password\" TEXT NOT NULL,
            \"Chat_id\" TEXT NOT NULL
        )
    """
}
