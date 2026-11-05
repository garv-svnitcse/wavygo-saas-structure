#!/usr/bin/env python3
"""
Database Seeder Script for WavyGo Vendor Platform.
Inserts fresh initial data (vendors, vehicles, customers, bookings, payments,
maintenance, documents) into MongoDB that are completely distinct from the
in-memory fallback/demo records.
"""

from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict

from bson import ObjectId
from pymongo import ASCENDING
from pymongo.collection import Collection

# Ensure backend root is in sys.path
backend_root = os.path.dirname(os.path.abspath(__file__))
if backend_root not in sys.path:
    sys.path.insert(0, backend_root)

from app.core.config import settings
from app.db.mongodb import create_mongo_client, get_database, ensure_vehicle_indexes
from app.modules.auth.security import hash_password, normalize_email


def normalize_phone(phone: str) -> str:
    """Strip formatting from phone number to match backend customer uniqueness rule."""
    import re
    return re.sub(r"\D", "", phone)


def run_seeder() -> int:
    print("==================================================")
    print("🌱 WavyGo Database Seeder")
    print("==================================================")

    client = create_mongo_client()
    if client is None:
        print("❌ Error: Could not connect to MongoDB.")
        print(f"   Check your MONGODB_URI in backend/.env: {settings.effective_mongo_uri}")
        return 1

    db = get_database(client)
    if db is None:
        print("❌ Error: Could not obtain database reference.")
        return 1

    print(f" Connected to database: {settings.mongodb_database}")

    # Ensure necessary indexes exist
    try:
        ensure_vehicle_indexes()
        db["vendors"].create_index([("email_normalized", ASCENDING)], unique=True, name="vendor_email_normalized_unique")
    except Exception as exc:
        print(f"ℹ️ Index notice: {exc}")

    now = datetime.now(timezone.utc)
    now_str = now.isoformat()

    # -------------------------------------------------------------------------
    # 1. Seed Vendor Account (for login & tenant scoping)
    # -------------------------------------------------------------------------
    vendor_email = "vendor@wavygo.com"
    vendor_password = "VendorPassword123!"
    normalized_email = normalize_email(vendor_email)

    vendor_col: Collection[Dict[str, Any]] = db["vendors"]
    existing_vendor = vendor_col.find_one({"email_normalized": normalized_email})

    if existing_vendor:
        vendor_id = existing_vendor["_id"]
        vendor_col.update_one(
            {"_id": vendor_id},
            {
                "$set": {
                    "password_hash": hash_password(vendor_password),
                    "is_active": True,
                    "business_name": "GoRides Bangalore Fleet Hub",
                    "updated_at": now,
                }
            },
        )
        print(f" Updated existing vendor account: {vendor_email} (ID: {vendor_id})")
    else:
        vendor_id = ObjectId()
        vendor_doc = {
            "_id": vendor_id,
            "email": vendor_email,
            "email_normalized": normalized_email,
            "password_hash": hash_password(vendor_password),
            "business_name": "GoRides Bangalore Fleet Hub",
            "is_active": True,
            "created_at": now,
            "updated_at": now,
        }
        vendor_col.insert_one(vendor_doc)
        print(f" Created new vendor account: {vendor_email} (ID: {vendor_id})")

    tenant_id_str = str(vendor_id)

    # -------------------------------------------------------------------------
    # 2. Seed Customers (Distinct from fallbacks: Aarav, Isha, Rohan, Ananya, Kabir)
    # -------------------------------------------------------------------------
    customers_data = [
        {
            "name": "Vikramaditya Rathore",
            "phone": "+91 91234 56789",
            "email": "vikram.rathore@example.com",
            "status": "Verified",
            "bookings": 18,
            "active": 1,
            "paid": 38400,
            "pending": 0,
        },
        {
            "name": "Pooja Singhania",
            "phone": "+91 92345 67890",
            "email": "pooja.s@example.com",
            "status": "Verified",
            "bookings": 11,
            "active": 1,
            "paid": 24200,
            "pending": 1500,
        },
        {
            "name": "Aditya Kashyap",
            "phone": "+91 93456 78901",
            "email": "aditya.kashyap@example.com",
            "status": "Verified",
            "bookings": 8,
            "active": 0,
            "paid": 16900,
            "pending": 0,
        },
        {
            "name": "Meera Nambiar",
            "phone": "+91 94567 89012",
            "email": "meera.nambiar@example.com",
            "status": "Review",
            "bookings": 4,
            "active": 1,
            "paid": 8400,
            "pending": 950,
        },
        {
            "name": "Siddharth Verma",
            "phone": "+91 95678 90123",
            "email": "sid.verma@example.com",
            "status": "Verified",
            "bookings": 5,
            "active": 0,
            "paid": 11200,
            "pending": 0,
        },
        {
            "name": "Tanvi Kulkarni",
            "phone": "+91 96789 01234",
            "email": "tanvi.k@example.com",
            "status": "Review",
            "bookings": 1,
            "active": 0,
            "paid": 1800,
            "pending": 0,
        },
    ]

    cust_col = db["customers"]
    cust_col.delete_many({"tenant_id": tenant_id_str})
    for c in customers_data:
        norm_phone = normalize_phone(c["phone"])
        norm_email = c["email"].lower()
        cust_doc = {
            "tenant_id": vendor_id,
            "name": c["name"],
            "phone": c["phone"],
            "phone_normalized": norm_phone,
            "email": c["email"],
            "email_normalized": norm_email,
            "status": c["status"],
            "bookings": c["bookings"],
            "active": c["active"],
            "paid": c["paid"],
            "pending": c["pending"],
            "created_at": now,
            "updated_at": now,
        }
        cust_col.update_one(
            {"tenant_id": vendor_id, "phone_normalized": norm_phone},
            {"$set": cust_doc},
            upsert=True,
        )

    print(f" Seeded {len(customers_data)} customer profiles")

    # -------------------------------------------------------------------------
    # 3. Seed Vehicles (Distinct from fallbacks: Activa 6G, Classic 350, Ather 450X, TVS Jupiter, Yamaha FZ-S, Pulsar N160)
    # -------------------------------------------------------------------------
    vehicles_data = [
        {
            "id": "VH-2001",
            "_id": "VH-2001",
            "name": "KTM 390 Duke",
            "makeModel": "KTM 390 Duke",
            "trim": "Gen 3 Electronic Orange",
            "registration": "KA 01 EK 8812",
            "registrationNumber": "KA01EK8812",
            "type": "Motorcycle",
            "fuel": "Petrol",
            "transmission": "Manual",
            "year": 2024,
            "color": "Electronic Orange",
            "engineCapacity": 399,
            "seats": 2,
            "rcStatus": "Verified",
            "dailyRate": 2200.0,
            "price": 2200.0,
            "minimumDays": 1,
            "securityDeposit": 2000.0,
            "pickupAddress": "Koramangala 5th Block, Bengaluru",
            "showOnWavygo": True,
            "status": "Online",
            "fleetAvailability": "Available",
            "availability": "Available",
            "photos": [
                {"url": "https://images.unsplash.com/photo-1558981403-c5f9899a28bc?auto=format&fit=crop&w=800&q=80"}
            ],
            "tenant_id": tenant_id_str,
            "createdAt": now_str,
            "updatedAt": now_str,
        },
        {
            "id": "VH-2002",
            "_id": "VH-2002",
            "name": "Suzuki Access 125",
            "makeModel": "Suzuki Access 125",
            "trim": "Special Edition Bluetooth",
            "registration": "KA 03 MD 4519",
            "registrationNumber": "KA03MD4519",
            "type": "Scooter",
            "fuel": "Petrol",
            "transmission": "Automatic",
            "year": 2024,
            "color": "Metallic Matte Black",
            "engineCapacity": 124,
            "seats": 2,
            "rcStatus": "Verified",
            "dailyRate": 699.0,
            "price": 699.0,
            "minimumDays": 1,
            "securityDeposit": 500.0,
            "pickupAddress": "Indiranagar 100ft Road, Bengaluru",
            "showOnWavygo": True,
            "status": "Online",
            "fleetAvailability": "Rented",
            "availability": "Rented",
            "photos": [
                {"url": "https://images.unsplash.com/photo-1568772585407-9361f9bf3a87?auto=format&fit=crop&w=800&q=80"}
            ],
            "tenant_id": tenant_id_str,
            "createdAt": now_str,
            "updatedAt": now_str,
        },
        {
            "id": "VH-2003",
            "_id": "VH-2003",
            "name": "Ola S1 Pro Gen 2",
            "makeModel": "Ola S1 Pro Gen 2",
            "trim": "Performance Edition 4kWh",
            "registration": "KA 05 EV 9031",
            "registrationNumber": "KA05EV9031",
            "type": "Electric",
            "fuel": "Electric",
            "transmission": "Automatic",
            "year": 2025,
            "color": "Stellar Blue",
            "engineCapacity": 0,
            "seats": 2,
            "rcStatus": "Verified",
            "dailyRate": 1299.0,
            "price": 1299.0,
            "minimumDays": 1,
            "securityDeposit": 1000.0,
            "pickupAddress": "HSR Layout Sector 2, Bengaluru",
            "showOnWavygo": True,
            "status": "Online",
            "fleetAvailability": "Available",
            "availability": "Available",
            "photos": [
                {"url": "https://images.unsplash.com/photo-1571188654248-7a89213915f7?auto=format&fit=crop&w=800&q=80"}
            ],
            "tenant_id": tenant_id_str,
            "createdAt": now_str,
            "updatedAt": now_str,
        },
        {
            "id": "VH-2004",
            "_id": "VH-2004",
            "name": "Hero Xpulse 200 4V",
            "makeModel": "Hero Xpulse 200 4V",
            "trim": "Pro Rally Edition",
            "registration": "KA 04 NX 7720",
            "registrationNumber": "KA04NX7720",
            "type": "Motorcycle",
            "fuel": "Petrol",
            "transmission": "Manual",
            "year": 2023,
            "color": "White & Red Rally",
            "engineCapacity": 199,
            "seats": 2,
            "rcStatus": "Verified",
            "dailyRate": 1499.0,
            "price": 1499.0,
            "minimumDays": 2,
            "securityDeposit": 1500.0,
            "pickupAddress": "Whitefield ITPL Main Road, Bengaluru",
            "showOnWavygo": True,
            "status": "Online",
            "fleetAvailability": "Under Review",
            "availability": "Under Review",
            "photos": [
                {"url": "https://images.unsplash.com/photo-1609630875171-b1321377ee65?auto=format&fit=crop&w=800&q=80"}
            ],
            "tenant_id": tenant_id_str,
            "createdAt": now_str,
            "updatedAt": now_str,
        },
        {
            "id": "VH-2005",
            "_id": "VH-2005",
            "name": "Harley-Davidson X440",
            "makeModel": "Harley-Davidson X440",
            "trim": "S Variant Top Model",
            "registration": "KA 51 HD 1903",
            "registrationNumber": "KA51HD1903",
            "type": "Motorcycle",
            "fuel": "Petrol",
            "transmission": "Manual",
            "year": 2024,
            "color": "Matte Denim Black",
            "engineCapacity": 440,
            "seats": 2,
            "rcStatus": "Verified",
            "dailyRate": 2699.0,
            "price": 2699.0,
            "minimumDays": 1,
            "securityDeposit": 3000.0,
            "pickupAddress": "MG Road, Bengaluru",
            "showOnWavygo": True,
            "status": "Online",
            "fleetAvailability": "Available",
            "availability": "Available",
            "photos": [
                {"url": "https://images.unsplash.com/photo-1558980664-3a031cf67ea8?auto=format&fit=crop&w=800&q=80"}
            ],
            "tenant_id": tenant_id_str,
            "createdAt": now_str,
            "updatedAt": now_str,
        },
        {
            "id": "VH-2006",
            "_id": "VH-2006",
            "name": "TVS Apache RTR 160 4V",
            "makeModel": "TVS Apache RTR 160 4V",
            "trim": "Special Edition Dual Channel ABS",
            "registration": "KA 02 TV 3418",
            "registrationNumber": "KA02TV3418",
            "type": "Motorcycle",
            "fuel": "Petrol",
            "transmission": "Manual",
            "year": 2023,
            "color": "Pearl White",
            "engineCapacity": 159,
            "seats": 2,
            "rcStatus": "Verified",
            "dailyRate": 999.0,
            "price": 999.0,
            "minimumDays": 1,
            "securityDeposit": 500.0,
            "pickupAddress": "Jayanagar 4th Block, Bengaluru",
            "showOnWavygo": True,
            "status": "Online",
            "fleetAvailability": "Maintenance",
            "availability": "Maintenance",
            "photos": [
                {"url": "https://images.unsplash.com/photo-1568772585407-9361f9bf3a87?auto=format&fit=crop&w=800&q=80"}
            ],
            "tenant_id": tenant_id_str,
            "createdAt": now_str,
            "updatedAt": now_str,
        },
    ]

    veh_col = db["vehicles"]
    for v in vehicles_data:
        veh_col.replace_one({"id": v["id"]}, v, upsert=True)

    print(f" Seeded {len(vehicles_data)} fleet vehicles")

    # -------------------------------------------------------------------------
    # 4. Seed Bookings (Distinct from fallbacks: BK-3984...BK-3979)
    # -------------------------------------------------------------------------
    bookings_data = [
        {
            "id": "BK-5001",
            "_id": "BK-5001",
            "customer": "Vikramaditya Rathore",
            "vehicle": "KTM 390 Duke",
            "dates": "Nov 01 – Nov 04",
            "type": "Offline",
            "status": "Active",
            "paid": 6600.0,
            "pending": 0.0,
            "base_amount": 6600.0,
            "add_on_amount": 0.0,
            "service_fee": 0.0,
            "discount_amount": 0.0,
            "deposit_amount": 2000.0,
            "total_amount": 6600.0,
            "rental_days": 3,
            "vehicle_details": {"name": "KTM 390 Duke", "id": "VH-2001", "daily_rate": 2200},
            "customer_details": {"name": "Vikramaditya Rathore", "phone": "+91 91234 56789"},
            "rental_details": {"start_date": "2026-11-01", "end_date": "2026-11-04", "pickup_location": "Koramangala 5th Block, Bengaluru"},
            "payment_details": {"method": "UPI", "status": "Paid", "paid_amount": 6600.0},
            "pickup_location": "Koramangala 5th Block, Bengaluru",
            "notes": "Helmet requested",
            "tenant_id": tenant_id_str,
            "created_at": now_str,
            "updated_at": now_str,
        },
        {
            "id": "BK-5002",
            "_id": "BK-5002",
            "customer": "Pooja Singhania",
            "vehicle": "Suzuki Access 125",
            "dates": "Oct 30 – Nov 02",
            "type": "Offline",
            "status": "Active",
            "paid": 1398.0,
            "pending": 699.0,
            "base_amount": 2097.0,
            "add_on_amount": 0.0,
            "service_fee": 0.0,
            "discount_amount": 0.0,
            "deposit_amount": 500.0,
            "total_amount": 2097.0,
            "rental_days": 3,
            "vehicle_details": {"name": "Suzuki Access 125", "id": "VH-2002", "daily_rate": 699},
            "customer_details": {"name": "Pooja Singhania", "phone": "+91 92345 67890"},
            "rental_details": {"start_date": "2026-10-30", "end_date": "2026-11-02", "pickup_location": "Indiranagar 100ft Road, Bengaluru"},
            "payment_details": {"method": "Cash", "status": "Partial", "paid_amount": 1398.0},
            "pickup_location": "Indiranagar 100ft Road, Bengaluru",
            "notes": "Balance due on return",
            "tenant_id": tenant_id_str,
            "created_at": now_str,
            "updated_at": now_str,
        },
        {
            "id": "BK-5003",
            "_id": "BK-5003",
            "customer": "Aditya Kashyap",
            "vehicle": "Ola S1 Pro Gen 2",
            "dates": "Oct 28 – Oct 30",
            "type": "Offline",
            "status": "Completed",
            "paid": 2598.0,
            "pending": 0.0,
            "base_amount": 2598.0,
            "add_on_amount": 0.0,
            "service_fee": 0.0,
            "discount_amount": 0.0,
            "deposit_amount": 1000.0,
            "total_amount": 2598.0,
            "rental_days": 2,
            "vehicle_details": {"name": "Ola S1 Pro Gen 2", "id": "VH-2003", "daily_rate": 1299},
            "customer_details": {"name": "Aditya Kashyap", "phone": "+91 93456 78901"},
            "rental_details": {"start_date": "2026-10-28", "end_date": "2026-10-30", "pickup_location": "HSR Layout Sector 2, Bengaluru"},
            "payment_details": {"method": "Card", "status": "Paid", "paid_amount": 2598.0},
            "pickup_location": "HSR Layout Sector 2, Bengaluru",
            "notes": "Returned with 92% battery",
            "tenant_id": tenant_id_str,
            "created_at": now_str,
            "updated_at": now_str,
        },
        {
            "id": "BK-5004",
            "_id": "BK-5004",
            "customer": "Meera Nambiar",
            "vehicle": "Hero Xpulse 200 4V",
            "dates": "Oct 26 – Oct 29",
            "type": "Offline",
            "status": "Completed",
            "paid": 4497.0,
            "pending": 0.0,
            "base_amount": 4497.0,
            "add_on_amount": 0.0,
            "service_fee": 0.0,
            "discount_amount": 0.0,
            "deposit_amount": 1500.0,
            "total_amount": 4497.0,
            "rental_days": 3,
            "vehicle_details": {"name": "Hero Xpulse 200 4V", "id": "VH-2004", "daily_rate": 1499},
            "customer_details": {"name": "Meera Nambiar", "phone": "+91 94567 89012"},
            "rental_details": {"start_date": "2026-10-26", "end_date": "2026-10-29", "pickup_location": "Whitefield ITPL Main Road, Bengaluru"},
            "payment_details": {"method": "UPI", "status": "Paid", "paid_amount": 4497.0},
            "pickup_location": "Whitefield ITPL Main Road, Bengaluru",
            "notes": "Rally kit included",
            "tenant_id": tenant_id_str,
            "created_at": now_str,
            "updated_at": now_str,
        },
    ]

    bk_col = db["bookings"]
    for b in bookings_data:
        bk_col.replace_one({"id": b["id"]}, b, upsert=True)

    print(f" Seeded {len(bookings_data)} rental bookings")

    # -------------------------------------------------------------------------
    # 5. Seed Payments (Distinct from fallbacks: TX-7082...TX-7078)
    # -------------------------------------------------------------------------
    payments_data = [
        {
            "id": "TX-8001",
            "_id": "TX-8001",
            "booking": "BK-5001",
            "customer": "Vikramaditya Rathore",
            "method": "UPI",
            "date": "Nov 01, 2026",
            "amount": 6600,
            "status": "Paid",
            "notes": "UPI Ref #4891028391 - GooglePay",
            "tenant_id": tenant_id_str,
            "created_at": now_str,
            "updated_at": now_str,
        },
        {
            "id": "TX-8002",
            "_id": "TX-8002",
            "booking": "BK-5002",
            "customer": "Pooja Singhania",
            "method": "Cash",
            "date": "Oct 30, 2026",
            "amount": 1398,
            "status": "Partial",
            "notes": "Advance token cash received at counter receipt #402",
            "tenant_id": tenant_id_str,
            "created_at": now_str,
            "updated_at": now_str,
        },
        {
            "id": "TX-8003",
            "_id": "TX-8003",
            "booking": "BK-5003",
            "customer": "Aditya Kashyap",
            "method": "Card",
            "date": "Oct 28, 2026",
            "amount": 2598,
            "status": "Paid",
            "notes": "HDFC POS Swiped Transaction #9019",
            "tenant_id": tenant_id_str,
            "created_at": now_str,
            "updated_at": now_str,
        },
        {
            "id": "TX-8004",
            "_id": "TX-8004",
            "booking": "BK-5004",
            "customer": "Meera Nambiar",
            "method": "UPI",
            "date": "Oct 26, 2026",
            "amount": 4497,
            "status": "Paid",
            "notes": "PayTM QR Scan payment verified",
            "tenant_id": tenant_id_str,
            "created_at": now_str,
            "updated_at": now_str,
        },
    ]

    pay_col = db["payments"]
    for p in payments_data:
        pay_col.replace_one({"id": p["id"]}, p, upsert=True)

    print(f" Seeded {len(payments_data)} payment transactions")

    # -------------------------------------------------------------------------
    # 6. Seed Maintenance (Distinct from fallbacks: MT-081...MT-078)
    # -------------------------------------------------------------------------
    maintenance_data = [
        {
            "id": "MT-301",
            "_id": "MT-301",
            "vehicle": "TVS Apache RTR 160 4V",
            "vehicle_name": "TVS Apache RTR 160 4V",
            "type": "Drive chain & brake pad replacement",
            "maintenance_type": "Drive chain & brake pad replacement",
            "damage_flaw_details": "Rear brake pads worn down below 2mm, chain slack exceeds 35mm",
            "start": "Oct 29, 2026",
            "expected": "Nov 02, 2026",
            "start_date": "2026-10-29",
            "expected_date": "2026-11-02",
            "cost": 3150,
            "estimated_cost": 3150,
            "payment": "Paid",
            "payment_status": "Paid",
            "status": "Ongoing",
            "tenant_id": tenant_id_str,
            "created_at": now_str,
            "updated_at": now_str,
        },
        {
            "id": "MT-302",
            "_id": "MT-302",
            "vehicle": "Hero Xpulse 200 4V",
            "vehicle_name": "Hero Xpulse 200 4V",
            "type": "Front fork seal & shock fluid replacement",
            "maintenance_type": "Front fork seal & shock fluid replacement",
            "damage_flaw_details": "Right fork leg oil leaking observed post offroad rental",
            "start": "Oct 27, 2026",
            "expected": "Oct 29, 2026",
            "start_date": "2026-10-27",
            "expected_date": "2026-10-29",
            "cost": 1850,
            "estimated_cost": 1850,
            "payment": "Paid",
            "payment_status": "Paid",
            "status": "Completed",
            "tenant_id": tenant_id_str,
            "created_at": now_str,
            "updated_at": now_str,
        },
        {
            "id": "MT-303",
            "_id": "MT-303",
            "vehicle": "Ola S1 Pro Gen 2",
            "vehicle_name": "Ola S1 Pro Gen 2",
            "type": "Software firmware update & tyre pressure calibration",
            "maintenance_type": "Software firmware update & tyre pressure calibration",
            "damage_flaw_details": "MoveOS 4.1 upgrade and belt tension adjustment",
            "start": "Oct 24, 2026",
            "expected": "Oct 24, 2026",
            "start_date": "2026-10-24",
            "expected_date": "2026-10-24",
            "cost": 500,
            "estimated_cost": 500,
            "payment": "Paid",
            "payment_status": "Paid",
            "status": "Completed",
            "tenant_id": tenant_id_str,
            "created_at": now_str,
            "updated_at": now_str,
        },
    ]

    maint_col = db["maintenance"]
    for m in maintenance_data:
        maint_col.replace_one({"id": m["id"]}, m, upsert=True)

    print(f" Seeded {len(maintenance_data)} maintenance records")

    # -------------------------------------------------------------------------
    # 7. Seed Documents (Distinct from fallbacks: DC-104...DC-100)
    # -------------------------------------------------------------------------
    documents_data = [
        {
            "id": "DC-301",
            "_id": "DC-301",
            "name": "Karnataka Commercial Bike Rental Permit",
            "category": "Commercial Permit",
            "scope": "Business",
            "status": "Verified",
            "date": "Oct 15, 2026",
            "file_url": "https://res.cloudinary.com/demo/image/upload/sample.pdf",
            "tenant_id": tenant_id_str,
            "created_at": now_str,
            "updated_at": now_str,
        },
        {
            "id": "DC-302",
            "_id": "DC-302",
            "name": "KTM 390 Duke Comprehensive Insurance 2026-27",
            "category": "Insurance",
            "scope": "Vehicle",
            "status": "Verified",
            "date": "Oct 10, 2026",
            "file_url": "https://res.cloudinary.com/demo/image/upload/sample.pdf",
            "tenant_id": tenant_id_str,
            "created_at": now_str,
            "updated_at": now_str,
        },
        {
            "id": "DC-303",
            "_id": "DC-303",
            "name": "Harley X440 Fitness & Pollution Under Control Certificate",
            "category": "PUC",
            "scope": "Vehicle",
            "status": "Verified",
            "date": "Oct 05, 2026",
            "file_url": "https://res.cloudinary.com/demo/image/upload/sample.pdf",
            "tenant_id": tenant_id_str,
            "created_at": now_str,
            "updated_at": now_str,
        },
    ]

    doc_col = db["documents"]
    for d in documents_data:
        doc_col.replace_one({"id": d["id"]}, d, upsert=True)

    print(f" Seeded {len(documents_data)} document records")

    # -------------------------------------------------------------------------
    # 8. Seed Expenses (Distinct from fallbacks: EXP-301...EXP-307)
    # -------------------------------------------------------------------------
    expenses_data = [
        {
            "id": "EXP-301",
            "_id": "EXP-301",
            "category": "Rent & Operations",
            "title": "Indiranagar Hub Main Facility Monthly Rent",
            "amount": 42000.0,
            "date": "Oct 01, 2026",
            "payment_method": "Bank Transfer",
            "payee": "Brigade Commercial Properties",
            "reference": "RTGS/SBIN004829103",
            "status": "Paid",
            "notes": "Main operational fleet hub lease installment",
            "tenant_id": tenant_id_str,
            "created_at": now_str,
            "updated_at": now_str,
        },
        {
            "id": "EXP-302",
            "_id": "EXP-302",
            "category": "Staff Salaries",
            "title": "Hub Operations & Fleet Mechanics Monthly Payroll",
            "amount": 55000.0,
            "date": "Oct 01, 2026",
            "payment_method": "Bank Transfer",
            "payee": "GoRides Hub Team",
            "reference": "NEFT/HDFC0019284",
            "status": "Paid",
            "notes": "Operations associate, 2 technicians and detailer",
            "tenant_id": tenant_id_str,
            "created_at": now_str,
            "updated_at": now_str,
        },
        {
            "id": "EXP-303",
            "_id": "EXP-303",
            "category": "Maintenance",
            "title": "Bulk OEM Spare Parts & Motul Synthetic Lubricants",
            "amount": 14500.0,
            "date": "Oct 08, 2026",
            "payment_method": "UPI",
            "payee": "Metro Auto Spares & Fluids",
            "reference": "UPI/428610928172",
            "status": "Paid",
            "notes": "Ceramic brake pads, Motul 7100 10W50, clutch cables",
            "tenant_id": tenant_id_str,
            "created_at": now_str,
            "updated_at": now_str,
        },
        {
            "id": "EXP-304",
            "_id": "EXP-304",
            "category": "Insurance & Taxes",
            "title": "Fleet Commercial Policy Q3 Premium",
            "amount": 9200.0,
            "date": "Sep 28, 2026",
            "payment_method": "Card",
            "payee": "ICICI Lombard General Insurance",
            "reference": "POL/491028471/RNW",
            "status": "Paid",
            "notes": "Comprehensive commercial fleet insurance renewal",
            "tenant_id": tenant_id_str,
            "created_at": now_str,
            "updated_at": now_str,
        },
        {
            "id": "EXP-305",
            "_id": "EXP-305",
            "category": "Fuel",
            "title": "Fleet Testing Petrol & Fast Charging Credits",
            "amount": 5600.0,
            "date": "Oct 12, 2026",
            "payment_method": "UPI",
            "payee": "Shell & Ather Grid Charging",
            "reference": "UPI/428901847192",
            "status": "Paid",
            "notes": "Pre-delivery fuel top-ups and Ather grid credits",
            "tenant_id": tenant_id_str,
            "created_at": now_str,
            "updated_at": now_str,
        },
        {
            "id": "EXP-306",
            "_id": "EXP-306",
            "category": "Utilities",
            "title": "Hub Commercial Electricity & Gigabit Fiber",
            "amount": 4200.0,
            "date": "Oct 10, 2026",
            "payment_method": "UPI",
            "payee": "BESCOM & Airtel Business",
            "reference": "BILL/OCT/491029",
            "status": "Paid",
            "notes": "Commercial EV power load and office fiber",
            "tenant_id": tenant_id_str,
            "created_at": now_str,
            "updated_at": now_str,
        },
        {
            "id": "EXP-307",
            "_id": "EXP-307",
            "category": "Marketing",
            "title": "Local Google Search Ads & College Campus Promo",
            "amount": 3500.0,
            "date": "Oct 14, 2026",
            "payment_method": "Card",
            "payee": "Google Ads India",
            "reference": "GADS-984-182",
            "status": "Paid",
            "notes": "Koramangala and Indiranagar student rental campaign",
            "tenant_id": tenant_id_str,
            "created_at": now_str,
            "updated_at": now_str,
        },
    ]

    exp_col = db["expenses"]
    for e in expenses_data:
        exp_col.replace_one({"id": e["id"]}, e, upsert=True)

    print(f" Seeded {len(expenses_data)} expense records")

    # -------------------------------------------------------------------------
    # 9. Seed Staff Members
    # -------------------------------------------------------------------------
    staff_data = [
        {
            "name": "Priya Nair",
            "role": "Fleet manager",
            "phone": "+91 98201 23456",
            "salary": 28000.0,
            "attendance": "24 / 26 days",
            "nextSalary": "Oct 31, 2026",
            "status": "Active",
            "tenant_id": vendor_id,
            "created_at": now,
            "updated_at": now,
        },
        {
            "name": "Dev Patel",
            "role": "Operations associate",
            "phone": "+91 98202 34567",
            "salary": 22000.0,
            "attendance": "23 / 26 days",
            "nextSalary": "Oct 31, 2026",
            "status": "Active",
            "tenant_id": vendor_id,
            "created_at": now,
            "updated_at": now,
        },
        {
            "name": "Sara Khan",
            "role": "Customer support",
            "phone": "+91 98203 45678",
            "salary": 24000.0,
            "attendance": "26 / 26 days",
            "nextSalary": "Oct 31, 2026",
            "status": "Active",
            "tenant_id": vendor_id,
            "created_at": now,
            "updated_at": now,
        },
        {
            "name": "Nikhil Rao",
            "role": "Delivery associate",
            "phone": "+91 98204 56789",
            "salary": 19500.0,
            "attendance": "Not recorded",
            "nextSalary": "Oct 31, 2026",
            "status": "Inactive",
            "tenant_id": vendor_id,
            "created_at": now,
            "updated_at": now,
        },
    ]

    staff_col = db["staff_members"]
    for s in staff_data:
        staff_col.replace_one({"phone": s["phone"], "tenant_id": vendor_id}, s, upsert=True)

    print(f" Seeded {len(staff_data)} staff members")

    print("\n==================================================")
    print("✅ Database seeding completed successfully!")
    print("==================================================")
    print("🔑 Vendor Login Credentials:")
    print(f"   Email:     {vendor_email}")
    print(f"   Password:  {vendor_password}")
    print(f"   Tenant ID: {tenant_id_str}")
    print("==================================================")
    return 0


if __name__ == "__main__":
    sys.exit(run_seeder())
