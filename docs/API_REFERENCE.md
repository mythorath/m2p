# Pool API Reference

This document provides detailed information about each supported mining pool's API.

## CPU Pool (cpu-pool.com)

### Endpoint

```
GET http://cpu-pool.com/api/worker_stats?addr={wallet_address}
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| addr | string | Yes | ADVC wallet address |

### Response

```json
{
  "totalHash": 12345.67,
  "totalShares": 98765,
  "immature": 0.5,
  "balance": 1.2,
  "paid": 10.5
}
```

| Field | Type | Description |
|-------|------|-------------|
| totalHash | float | Total hashrate |
| totalShares | float | Total shares submitted |
| immature | float | Immature balance (unconfirmed) |
| balance | float | Current confirmed balance |
| paid | float | **Cumulative payouts (TRACKED)** |

### Example

```bash
curl "http://cpu-pool.com/api/worker_stats?addr=AdvcWalletAddress123"
```

### Rate Limits

- Unknown - implement conservative polling (60s intervals recommended)

### Error Codes

- 404: Wallet not found or no mining activity
- 500: Server error

---

## Rplant (pool.rplant.xyz)

### Endpoint (Option 1)

```
GET https://pool.rplant.xyz/api/wallet/advc/{wallet_address}
```

### Endpoint (Option 2)

```
GET https://pool.rplant.xyz/api/walletEx/advc/{wallet_address}
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| wallet_address | string | Yes | ADVC wallet address (in URL path) |

### Response Format

**Note:** Exact format needs discovery. Parser supports multiple structures:

Option A:
```json
{
  "stats": {
    "paid": 15.5,
    "balance": 0.8,
    "totalHashes": 123456
  }
}
```

Option B:
```json
{
  "paid": 15.5,
  "balance": 0.8
}
```

Option C:
```json
{
  "totalPaid": 15.5,
  "balance": 0.8
}
```

### Tracked Field

The parser looks for `paid`, `totalPaid`, or `stats.paid` (in that order)

### Example

```bash
curl "https://pool.rplant.xyz/api/walletEx/advc/AdvcWalletAddress123"
```

### Rate Limits

- Unknown - implement conservative polling

### Error Codes

- 404: Wallet not found
- 500: Server error

### Notes

- API format requires confirmation
- Parser is flexible to handle multiple response structures
- If you know the exact format, update `parse_rplant()` method

---

## Zpool (zpool.ca)

### Endpoint

```
GET https://zpool.ca/api/walletEx?address={wallet_address}
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| address | string | Yes | BTC wallet address |

### Response

```json
{
  "currency": "BTC",
  "unsold": 0.00001234,
  "balance": 0.00005678,
  "unpaid": 0.00001111,
  "paid": 0.00050000,
  "total": 0.00058023
}
```

| Field | Type | Description |
|-------|------|-------------|
| currency | string | Always "BTC" |
| unsold | float | Unsold balance (BTC) |
| balance | float | Available balance (BTC) |
| unpaid | float | Unpaid earnings (BTC) |
| paid | float | **Cumulative payouts in BTC (TRACKED)** |
| total | float | Total earnings (BTC) |

### Example

```bash
curl "https://zpool.ca/api/walletEx?address=1BtcWalletAddress123"
```

### Rate Limits

- Unknown - implement conservative polling (60s intervals recommended)

### Error Codes

- 404: Wallet not found
- 500: Server error

### Important Notes

1. **Currency Conversion Required**: Zpool pays in BTC, not ADVC
2. **Conversion Rate**: Configured via `BTC_TO_ADVC_RATE` environment variable
3. **Calculation**: `advc_amount = btc_paid * BTC_TO_ADVC_RATE`
4. **Default Rate**: 1,000,000 (1 BTC = 1,000,000 ADVC equivalent)

### Conversion Example

```python
btc_paid = 0.00050000  # From API
btc_to_advc_rate = 1000000  # From config
advc_equivalent = btc_paid * btc_to_advc_rate  # = 500 ADVC
```

---

## Adding a New Pool

When adding support for a new pool, document:

### 1. Basic Information

- Pool name
- Website URL
- API documentation URL
- Supported coins

### 2. API Endpoint

- Full URL with parameters
- HTTP method (GET/POST)
- Authentication requirements (if any)
- Required headers

### 3. Request Format

- Query parameters
- Request body (if POST)
- Example request

### 4. Response Format

- JSON structure
- Field descriptions
- Data types
- Example response

### 5. Key Fields

- **Cumulative Payout Field**: Which field tracks total payouts?
- **Balance Field**: Current unpaid balance
- **Hashrate Field**: Current or total hashrate
- **Shares Field**: Total shares submitted

### 6. Special Considerations

- Currency conversion needed?
- Rate limiting?
- Pagination?
- Authentication required?
- Wallet format requirements?

### 7. Error Handling

- Common error codes
- Error response format
- Retry strategies

### Template

```markdown
## New Pool Name (newpool.com)

### Endpoint
```
GET https://newpool.com/api/stats?wallet={wallet}
```

### Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| wallet | string | Yes | ADVC wallet address |

### Response
```json
{
  "hashrate": 1234.56,
  "paid": 100.5,
  "pending": 2.3
}
```

### Tracked Field
`paid` - Cumulative payouts in ADVC

### Example
```bash
curl "https://newpool.com/api/stats?wallet=AdvcWallet123"
```

### Notes
- [Any special considerations]
```

---

## WebSocket Events

When a mining reward is detected, the service emits the following WebSocket event:

### Event: `mining_reward`

**Room:** `player_{player_id}`

**Payload:**
```json
{
  "player_id": 123,
  "username": "player1",
  "pool": "cpu-pool",
  "advc_amount": 5.5,
  "ap_awarded": 550,
  "total_ap": 12345.5,
  "total_advc_mined": 123.45,
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### Client Example

```javascript
// Connect to SocketIO server
const socket = io('http://localhost:3000');

// Join player's room
socket.emit('join', { room: `player_${playerId}` });

// Listen for mining rewards
socket.on('mining_reward', (data) => {
  console.log('Mining reward detected!', data);
  // Update UI with new AP and ADVC totals
  updatePlayerStats(data.total_ap, data.total_advc_mined);
  // Show notification
  showNotification(`You earned ${data.ap_awarded} AP from ${data.pool}!`);
});
```

---

## Testing APIs

### Test Script

```python
import requests

def test_pool_api(pool_name, url, wallet):
    """Test a pool API endpoint."""
    print(f"\nTesting {pool_name}...")
    print(f"URL: {url}")

    try:
        response = requests.get(url.format(wallet=wallet), timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.json()
    except Exception as e:
        print(f"Error: {e}")
        return None

# Test CPU Pool
test_pool_api(
    "CPU Pool",
    "http://cpu-pool.com/api/worker_stats?addr={wallet}",
    "YOUR_ADVC_WALLET"
)

# Test Rplant
test_pool_api(
    "Rplant",
    "https://pool.rplant.xyz/api/walletEx/advc/{wallet}",
    "YOUR_ADVC_WALLET"
)

# Test Zpool
test_pool_api(
    "Zpool",
    "https://zpool.ca/api/walletEx?address={wallet}",
    "YOUR_BTC_WALLET"
)
```

### Using curl

```bash
# CPU Pool
curl -v "http://cpu-pool.com/api/worker_stats?addr=YOUR_WALLET"

# Rplant
curl -v "https://pool.rplant.xyz/api/walletEx/advc/YOUR_WALLET"

# Zpool
curl -v "https://zpool.ca/api/walletEx?address=YOUR_WALLET"
```

### Expected Responses

All APIs should return:
- HTTP 200 on success
- JSON content-type
- Consistent field for cumulative payouts

---

## FAQ

### Q: How do I find a pool's API documentation?

A: Check:
1. Pool's official website (usually /api or /docs)
2. Pool's GitHub repository
3. Mining software documentation
4. Community forums/Discord

### Q: What if a pool doesn't have a `paid` field?

A: Look for alternatives:
- `total_paid`
- `totalPaid`
- `paid_total`
- `payouts` (array to sum)
- `stats.paid`

Modify the parser to calculate cumulative payouts from available data.

### Q: How do I handle pools that paginate results?

A: Implement pagination in the parser:
```python
async def fetch_all_pages(session, base_url):
    all_data = []
    page = 1
    while True:
        url = f"{base_url}&page={page}"
        data = await fetch(url)
        if not data:
            break
        all_data.extend(data)
        page += 1
    return all_data
```

### Q: What if a pool requires authentication?

A: Add auth headers to the request:
```python
headers = {
    "Authorization": f"Bearer {api_token}",
    "X-API-Key": api_key,
}
async with session.get(url, headers=headers) as response:
    ...
```

Store credentials in `.env` and `config.py`.
