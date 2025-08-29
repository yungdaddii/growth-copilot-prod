#!/usr/bin/env python3
from urllib.parse import quote_plus

password = "WhiteShark12!?"
encoded_password = quote_plus(password)

print("Original password:", password)
print("URL-encoded password:", encoded_password)
print()
print("Correct DATABASE_URL for Railway:")
print(f"postgresql+asyncpg://postgres:{encoded_password}@db.evfltcejtkodoqrshizs.supabase.co:5432/postgres")