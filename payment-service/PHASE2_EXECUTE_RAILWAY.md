# 🚀 PHASE 2 Execution: Railway PaymentConfig Migration

**Status**: Ready to execute
**Date**: 2025-11-03
**Phase 3**: ✅ DONE (deployed to production)

---

## What's Happening

Phase 2 updates Railway PostgreSQL paymentconfig table with **7 production seller shop_ids**.

**Before**: Empty or test data (shop_ids 8-15)
**After**: Production shop_ids (121038, 576631, 75509, 69292, 49237, 56195, 71691)

---

## 🚀 Execution Options

### Option 1: Railway Dashboard (Easiest - 2 minutes)

1. Go to: https://railway.app
2. Select project: **"positive-exploration"**
3. Select service: **"Postgres"** (the database)
4. Click **"Data"** tab
5. Paste this SQL:

```sql
BEGIN;

DELETE FROM paymentconfig WHERE shop_id IN (8,9,10,11,12,13,14,15);

INSERT INTO paymentconfig (shop_id, organization_bin, device_token, is_active, provider)
VALUES
    (121038, '920317450731', NULL, true, 'kaspi'),      -- Eileen flowers (Костанай)
    (576631, '210440028324', NULL, true, 'kaspi'),      -- VLVT Flowers Almaty (Алматы)
    (75509,  '860214400107', NULL, true, 'kaspi'),      -- Santini (Алматы)
    (69292,  '960514451575', NULL, true, 'kaspi'),      -- Gerim Flowers (Астана)
    (49237,  '930201350766', NULL, true, 'kaspi'),      -- Rosalie (Алматы)
    (56195,  '590915402028', NULL, true, 'kaspi'),      -- Royal Flowers Almaty (Алматы)
    (71691,  '991011000048', NULL, true, 'kaspi');      -- Flowers.Almaty (Алматы)

SELECT COUNT(*) as total_configs FROM paymentconfig;
SELECT shop_id, organization_bin FROM paymentconfig ORDER BY shop_id;

COMMIT;
```

6. Click **"Execute"**
7. Verify: Should see 7 rows returned

---

### Option 2: Railway CLI (If you have authentication)

```bash
# 1. Make sure you're authenticated
railway login

# 2. Navigate to project
railway link positive-exploration

# 3. Run the migration SQL directly
railway connect postgres -c "$(cat payment-service/phase2_migration.sql)"

# 4. Verify
railway connect postgres -c "SELECT COUNT(*) FROM paymentconfig;"
```

---

### Option 3: psql (If you have DATABASE_URL)

```bash
# 1. Get DATABASE_URL from Railway dashboard:
#    - Go to Postgres service
#    - Copy connection string (starts with postgresql://)

# 2. Execute migration
psql "postgresql://user:password@host:port/dbname" < phase2_migration.sql

# 3. Verify
psql "postgresql://user:password@host:port/dbname" -c "SELECT COUNT(*) FROM paymentconfig;"
```

---

## ✅ Verification After Migration

### Check 1: Table Exists
```sql
SELECT COUNT(*) as total_configs FROM paymentconfig;
-- Expected: 7
```

### Check 2: All 7 Sellers Present
```sql
SELECT shop_id, organization_bin, is_active FROM paymentconfig ORDER BY shop_id;
-- Expected: 7 rows with shop_ids 121038, 576631, 75509, 69292, 49237, 56195, 71691
```

### Check 3: Verify БINs
```sql
SELECT shop_id, organization_bin FROM paymentconfig WHERE shop_id = 121038;
-- Expected: 121038 | 920317450731
```

### Check 4: No test data
```sql
SELECT COUNT(*) FROM paymentconfig WHERE shop_id BETWEEN 8 AND 15;
-- Expected: 0
```

---

## 🧪 Test Payment-Service After Migration

Once migration is complete, test the payment-service:

```bash
# Test 1: Check health
curl https://payment-service.up.railway.app/api/health
# Expected: 200 OK

# Test 2: Get config for Eileen (shop_id=121038)
curl "https://payment-service.up.railway.app/api/payment/config?shop_id=121038"
# Expected:
# {
#   "shop_id": 121038,
#   "organization_bin": "920317450731",
#   "device_token": null,
#   "is_active": true,
#   "provider": "kaspi"
# }

# Test 3: Get config for VLVT (shop_id=576631)
curl "https://payment-service.up.railway.app/api/payment/config?shop_id=576631"
# Expected: organization_bin = "210440028324"

# Test 4: Get all configs
curl "https://payment-service.up.railway.app/api/payment/config"
# Expected: Array with 7 items
```

---

## 🔄 Complete Flow After Migration

```
1. Customer order from shop_id=121038 (Eileen)
   ↓
2. Production ApiClient calls payment-service
   ↓
3. payment-service queries paymentconfig table:
   SELECT organization_bin FROM paymentconfig WHERE shop_id=121038
   ↓
4. Returns: 920317450731 (Eileen's БИН)
   ↓
5. ApiClient sends to Kaspi API with Eileen's БИН
   ↓
6. Payment created → Money to Eileen's account ✅
```

---

## 🚨 Troubleshooting

### Error: "Table does not exist"
**Solution**: The table should be auto-created by SQLModel. Make sure payment-service was deployed to Railway.

### Error: "Duplicate key value violates constraint"
**Solution**: Run the DELETE statement first, or skip the DELETE if starting fresh.

### Error: "Connection refused"
**Solution**: Check that Postgres service is running in Railway dashboard.

---

## 📋 Timeline

✅ Phase 1: Find production shop_ids (DONE)
✅ Phase 3: Deploy ApiClient to production (DONE)
⏳ Phase 2: Execute migration on Railway (THIS PHASE)
⏳ Phase 4: Payment status polling
⏳ Phase 5: CRM webhooks
⏳ Phase 6: End-to-end testing

---

## ✨ After Phase 2 is Complete

1. The payment-service on Railway has all 7 sellers' configs
2. Production ApiClient can query payment-service
3. Each seller's payments route to their own БИН
4. System is ready for end-to-end testing

**Next Step**: Phase 4 - Payment status polling via cron

---

Last Updated: 2025-11-03
