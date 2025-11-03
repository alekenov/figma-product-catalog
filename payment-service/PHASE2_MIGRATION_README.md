# 🚀 Phase 2 Migration: Production Shop IDs Update

**Status**: ✅ Ready for execution
**Date**: 2025-11-03
**Source**: Research from Bitrix production database

---

## What's Being Updated

**FROM** (Test shop_ids):
```
shop_id 8-15 with test БINs
```

**TO** (Production shop_ids):
```
121038 → Eileen flowers (920317450731) - Костанай
576631 → VLVT Flowers Almaty (210440028324) - Алматы
75509  → Santini (860214400107) - Алматы
69292  → Gerim Flowers (960514451575) - Астана
49237  → Rosalie (930201350766) - Алматы
56195  → Royal Flowers Almaty (590915402028) - Алматы
71691  → Flowers.Almaty (991011000048) - Алматы
```

---

## Execution Options

### Option 1: Using Railway Dashboard (Easiest)

1. Go to Railway Dashboard → Select Payment Service
2. Click on "PostgreSQL" service
3. Click on the "Data" tab
4. Paste the SQL from `phase2_migration.sql`
5. Execute the SQL

**File to use**: `phase2_migration.sql`

---

### Option 2: Using Railway CLI (Recommended for Automation)

```bash
# 1. Make sure you're in payment-service directory
cd payment-service

# 2. Link to Railway project (if not linked)
railway link  # Or specify project ID: railway link <project-id>

# 3. Execute migration using Python script
railway run python migrate_production_shop_ids.py

# Or execute raw SQL using psql
railway connect postgres -c "$(cat phase2_migration.sql)"
```

---

### Option 3: Using Docker PostgreSQL Client

```bash
# Get Railway DATABASE_URL from environment
export DATABASE_URL=$(railway variables --kv | grep DATABASE_URL | cut -d'=' -f2)

# Connect and execute
docker run --rm -e PGPASSWORD=... \
  postgres:15 \
  psql -h <host> -U <user> -d <dbname> -f phase2_migration.sql
```

---

### Option 4: Deploy Updated Seed Script

The `seed_data.py` has been updated with production shop_ids. To apply:

```bash
# 1. Deploy to Railway
git add seed_data.py
git commit -m "Phase 2: Update seed_data with production shop_ids"
git push origin main

# 2. Railway automatically deploys and runs migrations
# 3. Verify in Railway dashboard → Deployments
```

**Note**: This approach requires clearing old data first.

---

## Migration Scripts Provided

### 1. SQL Migration (`phase2_migration.sql`)
- Pure SQL, can run on any PostgreSQL client
- Includes transaction handling
- Includes verification queries
- Best for: Railway Dashboard, direct psql execution

### 2. Python Migration (`migrate_production_shop_ids.py`)
- Python 3.9+ required
- Uses SQLModel/SQLAlchemy
- Provides detailed output/logging
- Best for: Railway CLI, local development, CI/CD

### 3. Updated Seed Data (`seed_data.py`)
- Production shop_ids instead of test ones
- Matches actual Bitrix production
- Can be reseeded if needed
- Best for: Fresh deployment, testing

---

## Verification Steps

After executing the migration, verify:

### 1. Check Total Configurations
```sql
SELECT COUNT(*) as total_configs FROM paymentconfig;
-- Should return: 7
```

### 2. Verify Production Shop IDs
```sql
SELECT shop_id, organization_bin, is_active
FROM paymentconfig
ORDER BY shop_id;
-- Should show all 7 production shop_ids
```

### 3. Check for Test IDs (should be empty)
```sql
SELECT * FROM paymentconfig WHERE shop_id BETWEEN 8 AND 15;
-- Should return: 0 rows
```

### 4. Verify БINs are Correct
```sql
SELECT shop_id, organization_bin FROM paymentconfig WHERE organization_bin = '920317450731';
-- Should return: shop_id = 121038 (Eileen)
```

---

## Rollback Plan

If something goes wrong, rollback to test data:

```sql
DELETE FROM paymentconfig WHERE shop_id > 100;
INSERT INTO paymentconfig (shop_id, organization_bin, is_active, provider)
VALUES
    (8, '891027350515', true, 'kaspi'),    -- Default Cvety.kz
    (9, '991011000048', true, 'kaspi'),    -- Flowers Almaty
    (10, '210440028324', true, 'kaspi'),   -- VLVT
    (11, '590915402028', true, 'kaspi'),   -- Royal Flowers
    (12, '960514451575', true, 'kaspi'),   -- Gerim
    (13, '860214400107', true, 'kaspi'),   -- Santini
    (14, '920317450731', true, 'kaspi'),   -- Eileen
    (15, '930201350766', true, 'kaspi');   -- Rosalie
```

---

## What Happens Next

After Phase 2 is complete:

### Phase 3: Update ApiClient.php
- Modify `/local/classes/Integration/Kaspi/ApiClient.php`
- Add call to payment-service with shop_id
- Payment service will automatically lookup БIN

### Phase 4: Payment Status Polling
- Add cron job for payment status checks
- Update order status in CRM based on Kaspi response

### Phase 5: CRM Webhooks
- Setup webhooks for payment completion
- Notify CRM when payment is successful

### Phase 6: Testing
- Test payment routing for all 7 sellers
- Verify money goes to correct accounts
- Monitor Kaspi integration

---

## Timeline

| Phase | Task | Status |
|-------|------|--------|
| 1 | Find production shop_ids | ✅ DONE |
| 2 | Update Railway paymentconfig | 🔄 IN PROGRESS |
| 3 | Update ApiClient.php | ⏳ PENDING |
| 4 | Add payment status polling | ⏳ PENDING |
| 5 | Setup CRM webhooks | ⏳ PENDING |
| 6 | Test all 7 sellers | ⏳ PENDING |

---

## Support

If you encounter issues:

1. **Connection Error**: Check Railway is logged in: `railway login`
2. **Permission Denied**: Verify you own the Railway project
3. **SQL Error**: Check syntax in `phase2_migration.sql`
4. **Data Loss**: Use rollback plan above

---

## Key Contacts

- **Payment Service**: `/figma-product-catalog/payment-service`
- **Database**: Railway PostgreSQL (production)
- **Integration**: `/home/bitrix/www/local/classes/Integration/Kaspi/ApiClient.php`

---

Last Updated: 2025-11-03
