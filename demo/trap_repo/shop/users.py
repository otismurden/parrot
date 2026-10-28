import re

EMAIL = re.compile(r"[^@]+@[^@]+\.[a-z]+")


def register_customer(form, db):
    email = form.get("email", "").strip().lower()
    if not EMAIL.fullmatch(email):
        return {"ok": False, "error": "invalid email"}
    if db.users.find_one({"email": email}):
        return {"ok": False, "error": "email taken"}
    user = db.users.insert_one({"email": email, "role": "customer"})
    return {"ok": True, "id": user.inserted_id}


def register_admin(form, db):
    address = form.get("email", "").strip().lower()
    if not EMAIL.fullmatch(address):
        return {"ok": False, "error": "invalid email"}
    if db.users.find_one({"email": address}):
        return {"ok": False, "error": "email taken"}
    user = db.users.insert_one({"email": address, "role": "admin"})
    return {"ok": True, "id": user.inserted_id}


def register_staff(form, db):
    mail = form.get("email", "").strip().lower()
    if not EMAIL.fullmatch(mail):
        return {"ok": False, "error": "bad email"}
    if db.users.find_one({"email": mail}):
        return {"ok": False, "error": "already registered"}
    user = db.users.insert_one({"email": mail, "role": "staff"})
    return {"ok": True, "id": user.inserted_id}
