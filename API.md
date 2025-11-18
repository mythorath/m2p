# M2P Wallet Verification System - API Documentation

Complete API reference for the M2P Wallet Verification System.

## Base URL

```
Development: http://localhost:5000
Production: https://your-domain.com
```

## Authentication

Admin endpoints require authentication via API key:

**Header:**
```
Authorization: Bearer YOUR_ADMIN_API_KEY
```

**OR**

```
X-API-Key: YOUR_ADMIN_API_KEY
```

## Public Endpoints

### Health Check

Check if the service is running.

**Endpoint:** `GET /health`

**Authentication:** None

**Response:**
```json
{
  "status": "healthy",
  "service": "M2P Wallet Verification",
  "timestamp": "2024-01-15T12:00:00.000000"
}
```

**Example:**
```bash
curl http://localhost:5000/health
```

---

### Register Player

Register a new player and generate verification challenge.

**Endpoint:** `POST /api/register`

**Authentication:** None

**Request Body:**
```json
{
  "wallet_address": "string"
}
```

**Response (Success - New Registration):**
```json
{
  "success": true,
  "player": {
    "id": 1,
    "wallet_address": "ADVC_wallet_address",
    "verified": false,
    "verification_amount": 0.4567,
    "verification_requested_at": "2024-01-15T12:00:00.000000",
    "verification_tx_hash": null,
    "verification_completed_at": null,
    "total_ap": 0.0,
    "created_at": "2024-01-15T12:00:00.000000",
    "updated_at": "2024-01-15T12:00:00.000000"
  },
  "verification_amount": 0.4567,
  "message": "Please send exactly 0.4567 ADVC to the dev wallet to verify"
}
```

**Response (Player Already Verified):**
```json
{
  "success": false,
  "message": "Wallet already verified",
  "player": {
    "id": 1,
    "wallet_address": "ADVC_wallet_address",
    "verified": true,
    "total_ap": 45.67,
    ...
  }
}
```

**Response (Verification Already Active):**
```json
{
  "success": true,
  "player": {...},
  "verification_amount": 0.4567,
  "message": "Verification challenge already active"
}
```

**Errors:**
- `400 Bad Request` - Wallet address missing
- `500 Internal Server Error` - Server error

**Example:**
```bash
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "wallet_address": "ADVC_test_wallet_123"
  }'
```

---

### Get Player Info

Retrieve player information and verification status.

**Endpoint:** `GET /api/player/:wallet_address`

**Authentication:** None

**URL Parameters:**
- `wallet_address` - Player's wallet address

**Response:**
```json
{
  "success": true,
  "player": {
    "id": 1,
    "wallet_address": "ADVC_wallet_address",
    "verified": false,
    "verification_amount": 0.4567,
    "verification_requested_at": "2024-01-15T12:00:00.000000",
    "total_ap": 0.0,
    ...
  }
}
```

**Errors:**
- `404 Not Found` - Player not found
- `500 Internal Server Error` - Server error

**Example:**
```bash
curl http://localhost:5000/api/player/ADVC_test_wallet_123
```

---

### Verify Now

Manually trigger verification check for a player.

**Endpoint:** `POST /api/verify-now`

**Authentication:** None

**Request Body:**
```json
{
  "wallet_address": "string"
}
```

**Response (Verification Successful):**
```json
{
  "success": true,
  "verified": true,
  "player": {
    "id": 1,
    "wallet_address": "ADVC_wallet_address",
    "verified": true,
    "verification_tx_hash": "0x123abc...",
    "total_ap": 45.67,
    ...
  },
  "message": "Verification successful!"
}
```

**Response (Verification Pending):**
```json
{
  "success": true,
  "verified": false,
  "message": "Verification pending. Transaction not found yet."
}
```

**Errors:**
- `400 Bad Request` - Wallet address missing
- `404 Not Found` - Player not found
- `500 Internal Server Error` - Server error

**Example:**
```bash
curl -X POST http://localhost:5000/api/verify-now \
  -H "Content-Type: application/json" \
  -d '{
    "wallet_address": "ADVC_test_wallet_123"
  }'
```

---

## Admin Endpoints

All admin endpoints require authentication.

### Manually Verify Player

Manually verify a player without blockchain verification (admin override).

**Endpoint:** `POST /admin/verify-player`

**Authentication:** Required

**Request Body:**
```json
{
  "wallet_address": "string",
  "tx_hash": "string (optional)"
}
```

**Response:**
```json
{
  "success": true,
  "player": {
    "id": 1,
    "wallet_address": "ADVC_wallet_address",
    "verified": true,
    "verification_tx_hash": "manual_verification",
    "total_ap": 45.67,
    ...
  },
  "message": "Player manually verified successfully"
}
```

**Errors:**
- `401 Unauthorized` - Invalid or missing API key
- `400 Bad Request` - Wallet address missing
- `404 Not Found` - Player not found
- `500 Internal Server Error` - Server error

**Example:**
```bash
curl -X POST http://localhost:5000/admin/verify-player \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_admin_api_key" \
  -d '{
    "wallet_address": "ADVC_test_wallet_123",
    "tx_hash": "0x123abc..."
  }'
```

---

### Get All Players

Retrieve list of all players with optional filtering.

**Endpoint:** `GET /admin/players`

**Authentication:** Required

**Query Parameters:**
- `verified` (optional) - Filter by verification status (true/false)
- `limit` (optional) - Number of results (default: 100, max: 1000)
- `offset` (optional) - Pagination offset (default: 0)

**Response:**
```json
{
  "success": true,
  "players": [
    {
      "id": 1,
      "wallet_address": "ADVC_wallet_1",
      "verified": true,
      "total_ap": 100.0,
      ...
    },
    {
      "id": 2,
      "wallet_address": "ADVC_wallet_2",
      "verified": false,
      "total_ap": 0.0,
      ...
    }
  ],
  "total": 2,
  "limit": 100,
  "offset": 0
}
```

**Errors:**
- `401 Unauthorized` - Invalid or missing API key
- `500 Internal Server Error` - Server error

**Examples:**
```bash
# Get all players
curl http://localhost:5000/admin/players \
  -H "X-API-Key: your_admin_api_key"

# Get only verified players
curl "http://localhost:5000/admin/players?verified=true" \
  -H "X-API-Key: your_admin_api_key"

# Get with pagination
curl "http://localhost:5000/admin/players?limit=50&offset=100" \
  -H "X-API-Key: your_admin_api_key"
```

---

### Get Verification Logs

Retrieve verification attempt logs for monitoring and debugging.

**Endpoint:** `GET /admin/verification-logs`

**Authentication:** Required

**Query Parameters:**
- `wallet_address` (optional) - Filter by wallet address
- `status` (optional) - Filter by status (success/failed/expired/error)
- `limit` (optional) - Number of results (default: 100)
- `offset` (optional) - Pagination offset (default: 0)

**Response:**
```json
{
  "success": true,
  "logs": [
    {
      "id": 1,
      "player_id": 1,
      "wallet_address": "ADVC_wallet_1",
      "verification_method": "advc_explorer_api",
      "status": "success",
      "tx_hash": "0x123abc...",
      "amount": 0.4567,
      "ap_credited": 45.67,
      "error_message": null,
      "created_at": "2024-01-15T12:00:00.000000"
    },
    {
      "id": 2,
      "player_id": 2,
      "wallet_address": "ADVC_wallet_2",
      "verification_method": "pool_payment_history",
      "status": "failed",
      "tx_hash": null,
      "amount": 0.3456,
      "ap_credited": null,
      "error_message": "Transaction not found",
      "created_at": "2024-01-15T12:05:00.000000"
    }
  ],
  "total": 2,
  "limit": 100,
  "offset": 0
}
```

**Log Status Values:**
- `success` - Verification successful
- `failed` - Verification failed (transaction not found)
- `expired` - Verification challenge expired
- `error` - System error during verification

**Errors:**
- `401 Unauthorized` - Invalid or missing API key
- `500 Internal Server Error` - Server error

**Examples:**
```bash
# Get all logs
curl http://localhost:5000/admin/verification-logs \
  -H "X-API-Key: your_admin_api_key"

# Get logs for specific wallet
curl "http://localhost:5000/admin/verification-logs?wallet_address=ADVC_wallet_1" \
  -H "X-API-Key: your_admin_api_key"

# Get only failed verifications
curl "http://localhost:5000/admin/verification-logs?status=failed" \
  -H "X-API-Key: your_admin_api_key"
```

---

## WebSocket Events

The system uses Socket.IO for real-time notifications.

### Client → Server Events

#### Connect
Establish WebSocket connection.

```javascript
const socket = io('http://localhost:5000');

socket.on('connect', () => {
  console.log('Connected to M2P server');
});
```

#### Join Room
Join a wallet address room to receive notifications.

**Event:** `join`

**Data:**
```json
{
  "wallet_address": "string"
}
```

**Response:** `joined` event

```javascript
socket.emit('join', { wallet_address: 'ADVC_wallet_123' });

socket.on('joined', (data) => {
  console.log('Joined room:', data.wallet_address);
});
```

---

### Server → Client Events

#### Connected
Sent when client successfully connects.

**Event:** `connected`

**Data:**
```json
{
  "message": "Connected to M2P verification service"
}
```

#### Verification Complete
Sent when player verification is successful.

**Event:** `verification_complete`

**Data:**
```json
{
  "wallet_address": "ADVC_wallet_123",
  "tx_hash": "0x123abc...",
  "ap_credited": 45.67,
  "total_ap": 45.67,
  "message": "Verification successful! 45.67 AP credited."
}
```

```javascript
socket.on('verification_complete', (data) => {
  console.log('Verification complete!', data);
  // Update UI with new AP balance
});
```

#### Verification Expired
Sent when verification challenge expires (24 hours).

**Event:** `verification_expired`

**Data:**
```json
{
  "wallet_address": "ADVC_wallet_123",
  "message": "Verification challenge expired. Please register again."
}
```

```javascript
socket.on('verification_expired', (data) => {
  console.log('Verification expired:', data);
  // Prompt user to re-register
});
```

---

## Error Responses

All endpoints follow a consistent error response format:

```json
{
  "error": "Error message description"
}
```

### HTTP Status Codes

- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request parameters
- `401 Unauthorized` - Authentication required or failed
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

---

## Rate Limiting

Currently no rate limiting is implemented. For production deployment, consider:

- Player registration: 5 requests per IP per hour
- Verify now: 10 requests per wallet per hour
- Admin endpoints: 100 requests per minute

---

## Example Client Implementations

### JavaScript (Browser)

```html
<!DOCTYPE html>
<html>
<head>
  <title>M2P Wallet Verification</title>
  <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
</head>
<body>
  <h1>M2P Wallet Verification</h1>

  <input type="text" id="wallet" placeholder="Enter wallet address">
  <button onclick="register()">Register</button>
  <button onclick="checkVerification()">Check Verification</button>

  <div id="status"></div>

  <script>
    const API_URL = 'http://localhost:5000';
    const socket = io(API_URL);

    socket.on('connect', () => {
      console.log('Connected to server');
    });

    async function register() {
      const wallet = document.getElementById('wallet').value;

      const response = await fetch(`${API_URL}/api/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ wallet_address: wallet })
      });

      const data = await response.json();

      if (data.success) {
        document.getElementById('status').innerHTML =
          `Send ${data.verification_amount} ADVC to verify`;

        // Join room for notifications
        socket.emit('join', { wallet_address: wallet });

        // Listen for verification complete
        socket.on('verification_complete', (result) => {
          document.getElementById('status').innerHTML =
            `✓ Verified! ${result.ap_credited} AP credited`;
        });
      }
    }

    async function checkVerification() {
      const wallet = document.getElementById('wallet').value;

      const response = await fetch(`${API_URL}/api/verify-now`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ wallet_address: wallet })
      });

      const data = await response.json();

      document.getElementById('status').innerHTML =
        data.verified ? '✓ Verified!' : 'Not verified yet';
    }
  </script>
</body>
</html>
```

### Python Client

```python
import requests
import socketio

API_URL = 'http://localhost:5000'

# Create Socket.IO client
sio = socketio.Client()

@sio.on('connect')
def on_connect():
    print('Connected to server')

@sio.on('verification_complete')
def on_verification_complete(data):
    print(f"Verified! {data['ap_credited']} AP credited")
    print(f"Total AP: {data['total_ap']}")

# Register player
def register_player(wallet_address):
    response = requests.post(
        f'{API_URL}/api/register',
        json={'wallet_address': wallet_address}
    )
    data = response.json()

    if data['success']:
        print(f"Send {data['verification_amount']} ADVC to verify")

        # Connect WebSocket and join room
        sio.connect(API_URL)
        sio.emit('join', {'wallet_address': wallet_address})

        return data
    else:
        print(f"Error: {data.get('message')}")
        return None

# Check verification
def check_verification(wallet_address):
    response = requests.post(
        f'{API_URL}/api/verify-now',
        json={'wallet_address': wallet_address}
    )
    return response.json()

# Example usage
if __name__ == '__main__':
    wallet = 'ADVC_test_wallet_123'

    # Register
    result = register_player(wallet)

    # Wait for verification (WebSocket will notify)
    sio.wait()
```

---

## Testing

See [tests/](tests/) directory for comprehensive test suite.

Run tests:
```bash
pytest tests/ -v
```

---

## Changelog

### Version 1.0.0 (2024-01-15)
- Initial release
- Three verification methods (API, Pool, Web Scraping)
- Background verification loop
- WebSocket notifications
- Admin endpoints
- Comprehensive logging
