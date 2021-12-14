TABLES = {
    "users": """
        CREATE TABLE IF NOT EXISTS Users(
            \"Id\" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
            \"Firstname\" TEXT NOT NULL,
            \"Lastname\" TEXT NOT NULL,
            \"Chat_id\" INTEGER NOT NULL UNIQUE
        )
    """,
    "passwords": """
        CREATE TABLE IF NOT EXISTS Passwords(
            \"Id\" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
            \"Title\" TEXT NOT NULL,
            \"Password\" TEXT NOT NULL,
            \"User_id\" INTEGER NOT NULL
        )
    """
}
