# Admin Bot - Telegram Bot for Flower Shop Staff

Telegram bot for florists and managers to manage orders, publish products, and control inventory.

## 🎯 Purpose

This bot serves **staff members** (florists, managers, directors). Staff can:
- 📦 View and manage all orders
- ✏️ Change order statuses (NEW → DELIVERED)
- ➕ Add new products with photos
- 📊 Monitor warehouse inventory
- 🔍 Search orders and products

For **customers** (ordering flowers), see `/customer-bot`.

---

## 🏗️ Architecture

Supports two environments with separate databases:

### Production Environment
- **Shop ID**: 17008
- **Database**: Bitrix (185.125.90.141)
- **Mode**: Webhook (Railway deployment)
- **Users**: Real cvety.kz staff

### Development Environment
- **Shop ID**: 8
- **Database**: Railway PostgreSQL
- **Mode**: Polling (local testing)
- **Users**: Development/testing staff accounts

---

## 🚀 Quick Start

### Production Deployment (Railway)

1. **Create Telegram Bot in @BotFather:**
   ```
   /newbot
   Name: Cvety.kz Admin Bot
   Username: cvety_admin_bot
   ```
   Copy the token.

2. **Configure Environment Variables in Railway UI:**
   ```bash
   ENVIRONMENT=production
   TELEGRAM_TOKEN=<token_from_botfather>
   DEFAULT_SHOP_ID=17008
   MCP_SERVER_URL=https://mcp-server-production-00cd.up.railway.app
   BACKEND_API_URL=https://figma-product-catalog-production.up.railway.app/api/v1
   WEBHOOK_URL=${{RAILWAY_PUBLIC_DOMAIN}}
   LOG_LEVEL=INFO
   ```

3. **Deploy:**
   ```bash
   git push origin main  # Auto-deploys to Railway
   ```

4. **Add Staff Members:**
   - Staff opens bot in Telegram
   - Clicks "Start"
   - Shares contact for authorization
   - Admin approves (future: role assignment)

### Local Development

1. **Create Development Bot in @BotFather:**
   ```
   /newbot
   Name: Cvety.kz Admin Bot (Dev)
   Username: cvety_admin_dev_bot
   ```

2. **Copy environment file:**
   ```bash
   cd admin-bot
   cp .env.example .env.development
   ```

3. **Edit `.env.development`:**
   - Paste dev bot token into `TELEGRAM_TOKEN`

4. **Start local backend services:**
   ```bash
   # Terminal 1: Backend API
   cd ../backend
   python main.py  # Runs on port 8014

   # Terminal 2: MCP Server
   cd ../mcp-server
   python server.py --transport streamable-http --port 8000
   ```

5. **Run admin bot:**
   ```bash
   cd admin-bot
   ENVIRONMENT=development python bot.py
   ```

---

## 🤖 Bot Commands

### Basic Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message and authorization |
| `/help` | Show all available commands |

### Order Management

| Command | Description | Example |
|---------|-------------|---------|
| `/orders` | List recent orders (NEW/PAID) | `/orders` |
| `/order <id>` | Show order details | `/order 156` |
| `/status <id> <status>` | Change order status | `/status 156 IN_PRODUCTION` |

**Available Statuses:**
```
NEW → PAID → ACCEPTED → IN_PRODUCTION → READY → IN_DELIVERY → DELIVERED
```

### Product Management

| Command | Description | Example |
|---------|-------------|---------|
| `/add_product` | Start product creation flow | `/add_product` |
| `/products` | List all products | `/products` |

### Warehouse Management

| Command | Description | Example |
|---------|-------------|---------|
| `/warehouse` | View inventory levels | `/warehouse` |

---

## 📝 Usage Examples

### Managing Orders

**View Recent Orders:**
```
Staff: /orders
Bot: 📦 Новые заказы (3):
     #156 - Букет роз, 12,000₸
     #157 - Композиция, 25,000₸
     #158 - Букет лилий, 18,000₸
```

**View Order Details:**
```
Staff: /order 156
Bot: 📦 Заказ #156
     Статус: NEW
     Клиент: +77011234567
     Товар: Букет роз (12,000₸)
     Доставка: Алматы, ул. Абая 150
     Время: 2025-10-24 15:00

     [Buttons: ACCEPTED | IN_PRODUCTION | READY | IN_DELIVERY | DELIVERED]
```

**Change Order Status:**
```
Staff: /status 156 IN_PRODUCTION
Bot: ✅ Статус заказа #156 изменен на IN_PRODUCTION
     Клиент получит уведомление
```

### Adding Products

```
Staff: /add_product
Bot: ➕ Добавить товар

     1️⃣ Отправьте фото букета
     2️⃣ Введите данные:
        • Название
        • Тип (bouquet/composition/box)
        • Цена (в копейках)

Staff: [sends photo]
Staff: Букет "Романтика", bouquet, 1500000
Bot: ✅ Товар #234 добавлен!
     Фото загружено в Cloudflare
     Товар опубликован
```

### Warehouse Operations

```
Staff: /warehouse
Bot: 📦 Склад - Остатки

     🌹 Цветы:
     • Розы красные: 50 шт ✅
     • Розы белые: 30 шт ⚠️ Мало
     • Лилии: 5 шт ❌ Критично

     🎀 Материалы:
     • Лента атласная: 100 м ✅
     • Коробки большие: 15 шт ✅
```

---

## 📁 Project Structure

```
admin-bot/
├── bot.py                  # Main bot application with admin commands
├── admin_handlers.py       # Admin operation handlers
├── mcp_client.py          # MCP server HTTP client
├── formatters.py          # Formatting utilities
├── logging_config.py      # Structured logging
├── requirements.txt       # Python dependencies
├── railway.json           # Railway deployment config
├── .env.production        # Production environment vars
├── .env.development       # Development environment vars
├── .env.example           # Template for new setup
└── README.md              # This file
```

---

## 🔧 Technical Stack

- **Framework**: python-telegram-bot 22.5
- **Tools**: MCP tools (direct integration, no AI Agent needed)
- **Database**: Bitrix (prod) / PostgreSQL (dev)
- **Deployment**: Railway (Nixpacks)
- **Image Upload**: Cloudflare R2 (via workers)

---

## 📊 Environment Variables

| Variable | Production | Development | Description |
|----------|-----------|-------------|-------------|
| `ENVIRONMENT` | `production` | `development` | Determines which .env file to load |
| `TELEGRAM_TOKEN` | New admin bot token | New dev bot token | Bot token from @BotFather |
| `DEFAULT_SHOP_ID` | `17008` | `8` | Multi-tenancy shop ID |
| `MCP_SERVER_URL` | Railway URL | `http://localhost:8000` | MCP server endpoint |
| `BACKEND_API_URL` | Railway URL | `http://localhost:8014/api/v1` | Backend API |
| `WEBHOOK_URL` | `${{RAILWAY_PUBLIC_DOMAIN}}` | (empty) | Webhook URL (empty = polling mode) |
| `LOG_LEVEL` | `INFO` | `DEBUG` | Logging verbosity |

**Note**: Admin bot doesn't use AI Agent Service - all operations go directly to MCP/Backend.

---

## 🔐 Security & Authorization

### Current (MVP)
- **Authorization**: Contact sharing required
- **Access Control**: Anyone who shares contact can access
- **Multi-tenancy**: shop_id isolation enforced by backend

### Future (when roles are implemented)
- **Role-based access**:
  - `DIRECTOR`: Full access (all commands)
  - `MANAGER`: Orders + inventory (no staff management)
  - `WORKER`: View orders only (no status changes)
- **Permission checks** before each operation
- **Audit logging** for all admin actions

---

## 🐛 Troubleshooting

### Bot doesn't respond

1. **Check Telegram token:**
   ```bash
   curl "https://api.telegram.org/bot<TOKEN>/getMe"
   ```

2. **Check webhook status (production):**
   ```bash
   curl "https://api.telegram.org/bot<TOKEN>/getWebhookInfo"
   ```

3. **Check MCP server is running:**
   ```bash
   curl http://localhost:8000/health  # dev
   # or
   curl https://mcp-server-production-00cd.up.railway.app/health  # prod
   ```

### "Not authorized" error

**Symptom**: Bot says "Для доступа необходимо авторизоваться"

**Solution**: Staff member needs to:
1. Open bot in Telegram
2. Click `/start`
3. Click "Поделиться контактом" button
4. Confirm contact sharing

### Environment not loading

**Solution**: Always set `ENVIRONMENT` before running:
```bash
# Correct
ENVIRONMENT=development python bot.py

# Wrong
python bot.py  # Uses default .env, may fail
```

---

## 📈 Development Roadmap

### MVP (Current)
- ✅ Basic authorization (contact sharing)
- ✅ Command structure
- ✅ Placeholder handlers
- ✅ Multi-environment support

### Phase 1 (Next)
- 🔲 Real MCP integration for orders
- 🔲 Order status changes with notifications
- 🔲 Product image upload to Cloudflare R2
- 🔲 Warehouse inventory display

### Phase 2 (Future)
- 🔲 Role-based access control (DIRECTOR/MANAGER/WORKER)
- 🔲 Product editing and disabling
- 🔲 Statistics and reports
- 🔲 Staff management commands
- 🔲 Automated notifications for low stock

---

## 🔗 Related Services

- **Customer Bot**: `/customer-bot` (for customers ordering flowers)
- **Backend API**: `/backend` (shared API)
- **MCP Server**: `/mcp-server` (tool integration)
- **Admin Panel**: `/frontend` (web interface on port 5176)

---

## 💡 Development Tips

### Testing Locally

1. Always use `ENVIRONMENT=development` to avoid affecting production
2. Create test staff accounts with different roles (when roles are added)
3. Test order status transitions: NEW → PAID → DELIVERED

### Adding New Commands

1. Add command handler in `bot.py`:
   ```python
   self.app.add_handler(CommandHandler("mycommand", self.mycommand_handler))
   ```

2. Create handler function in `admin_handlers.py`:
   ```python
   async def handle_mycommand(update, context, mcp_client, shop_id):
       # Implementation
   ```

3. Add authorization check:
   ```python
   is_authorized, _ = await self.check_admin_authorization(user_id)
   if not is_authorized:
       await self._request_authorization(update)
       return
   ```

### MCP Tool Integration

When implementing real MCP calls (replacing placeholders):
```python
# Instead of placeholder text:
response_text = "MVP placeholder..."

# Use actual MCP call:
orders = await mcp_client.list_orders(shop_id=shop_id, status="NEW")
response_text = format_orders_list(orders)
```

---

## 📞 Support

For issues or questions:
- Backend API: See `/backend/README.md`
- MCP Server: See `/mcp-server/README.md`
- Customer Bot: See `/customer-bot/README.md`
- Project docs: See `/CLAUDE.md`
