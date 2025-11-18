# Mine to Play - React Game Client

A React-based frontend for the Mine to Play game, where Dogecoin miners can earn Adventure Coins (ADVC) and Adventure Points (AP) through their mining activities.

## Features

- **User Authentication**: Login and registration with Dogecoin wallet verification
- **Real-time Updates**: WebSocket integration for live mining reward notifications
- **Game Dashboard**: Interactive mining scene with animated visuals
- **Leaderboards**: Competitive rankings with multiple time periods (All-Time, Weekly, Daily)
- **Achievements System**: Unlock achievements and earn bonus AP
- **Global Statistics**: View network-wide stats and your contribution
- **Responsive Design**: Mobile-friendly dark theme with glassmorphism effects
- **Animated Rewards**: Beautiful reward popups with Framer Motion animations

## Tech Stack

- **React**: Frontend framework
- **React Router**: Client-side routing
- **Socket.io Client**: Real-time WebSocket communication
- **Axios**: HTTP client for API requests
- **Framer Motion**: Animation library
- **Context API**: Global state management

## Project Structure

```
client/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── Login.js              # Login page
│   │   ├── Register.js           # Registration with wallet verification
│   │   ├── GameView.js           # Main game interface
│   │   ├── Leaderboard.js        # Leaderboard rankings
│   │   ├── Achievements.js       # Achievement showcase
│   │   ├── Stats.js              # Global statistics
│   │   └── RewardPopup.js        # Animated reward notifications
│   ├── services/
│   │   ├── api.js                # API service with all endpoints
│   │   └── socket.js             # WebSocket connection
│   ├── hooks/
│   │   ├── usePlayer.js          # Player data management hook
│   │   └── useWebSocket.js       # WebSocket event handling hook
│   ├── context/
│   │   └── GameContext.js        # Global game state context
│   ├── App.js                    # Main app with routing
│   ├── App.css                   # Global styles
│   └── index.js                  # Entry point
├── package.json
└── README.md
```

## Installation

### Prerequisites

- Node.js (v14 or higher)
- npm or yarn
- Running Mine to Play backend server

### Setup Instructions

1. **Navigate to the client directory**:
   ```bash
   cd client
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Create environment file**:
   ```bash
   cp .env.example .env
   ```

4. **Configure environment variables** (edit `.env`):
   ```env
   REACT_APP_API_URL=http://localhost:5000/api
   REACT_APP_SOCKET_URL=http://localhost:5000
   ```

5. **Start the development server**:
   ```bash
   npm start
   ```

6. **Open your browser**:
   Navigate to `http://localhost:3000`

## Available Scripts

### `npm start`
Runs the app in development mode at [http://localhost:3000](http://localhost:3000).

### `npm test`
Launches the test runner in interactive watch mode.

### `npm run build`
Builds the app for production to the `build` folder.
- Optimized and minified bundle
- Ready for deployment

### `npm run eject`
**Note: this is a one-way operation!**
Ejects from Create React App for full configuration control.

## Usage Guide

### Registration

1. Click "Register here" on the login page
2. Enter your Dogecoin wallet address
3. Choose a display name
4. Send the exact verification amount to the donation address
5. Submit your transaction ID (TXID)
6. Wait for verification (may take a few moments)

### Login

1. Enter your verified Dogecoin wallet address
2. Click "Login"
3. Access your game dashboard

### Game Dashboard

- **Mining Scene**: Animated visualization of your mining activity
- **Stats Bar**: View your ADVC, AP, and achievement count
- **Activity Feed**: Real-time notifications of mining rewards
- **Navigation**: Access leaderboards and achievements

### Leaderboards

- Switch between All-Time, Weekly, and Daily rankings
- View top miners by ADVC and AP
- Your rank is highlighted
- Auto-refreshes every 30 seconds

### Achievements

- Browse all available achievements
- Filter by Locked/Unlocked status
- Sort by AP reward or name
- Track progress on multi-stage achievements
- View total AP earned from achievements

### Global Statistics

- View network-wide statistics
- See your contribution percentage
- Mining events in the last 24 hours
- Total players and achievements

## API Integration

The client communicates with the backend through:

### REST API Endpoints

- `POST /api/players/register` - Register new player
- `POST /api/players/verify` - Verify wallet ownership
- `GET /api/players/:wallet` - Get player data
- `GET /api/leaderboard` - Get leaderboard rankings
- `GET /api/achievements` - Get all achievements
- `GET /api/players/:wallet/achievements` - Get player achievements
- `GET /api/stats` - Get global statistics

### WebSocket Events

**Client → Server:**
- `subscribe_wallet` - Subscribe to wallet updates
- `unsubscribe_wallet` - Unsubscribe from updates

**Server → Client:**
- `mining_reward` - New mining reward received
- `achievement_unlocked` - Achievement unlocked
- `player_updated` - Player data changed

## Styling

The app features a dark theme with:
- Glassmorphism effects
- Gradient backgrounds
- Smooth animations
- Responsive design
- Custom scrollbars
- Hover effects

### Color Scheme

- **Primary**: #667eea (Purple-Blue)
- **Secondary**: #764ba2 (Purple)
- **Success**: #4ade80 (Green)
- **Warning**: #fbbf24 (Yellow)
- **Danger**: #ef4444 (Red)
- **Background**: #1a1a2e → #16213e (Gradient)

## State Management

Uses React Context API for global state:
- Player authentication
- WebSocket connection status
- Notifications
- Reward popups

### GameContext Provides:

```javascript
{
  // Authentication
  wallet,
  isAuthenticated,
  login,
  logout,

  // Player Data
  player,
  playerLoading,
  playerError,
  refreshPlayer,
  updatePlayer,

  // WebSocket
  socketConnected,
  socketError,
  lastEvent,

  // Notifications
  notifications,
  addNotification,
  removeNotification,
  clearNotifications,

  // Reward Popup
  showRewardPopup,
  rewardData,
  hideRewardPopup,
}
```

## Performance Optimizations

- Code splitting with React Router
- Lazy loading of components
- Memoization of expensive calculations
- Debounced API calls
- Efficient re-renders with React hooks
- WebSocket connection pooling

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Troubleshooting

### Connection Issues

If you can't connect to the backend:
1. Verify the backend is running on port 5000
2. Check your `.env` file has correct URLs
3. Ensure CORS is enabled on the backend
4. Check browser console for errors

### WebSocket Disconnections

- The app auto-reconnects on disconnect
- Check the connection status indicator in the header
- Verify firewall settings aren't blocking WebSockets

### Build Errors

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear React cache
npm start -- --reset-cache
```

## Production Deployment

1. **Build the production bundle**:
   ```bash
   npm run build
   ```

2. **Update environment variables**:
   Update `.env` with production API URLs

3. **Deploy the build folder**:
   - Serve with nginx, Apache, or any static file server
   - Or deploy to platforms like Vercel, Netlify, or AWS S3

4. **Example nginx configuration**:
   ```nginx
   server {
     listen 80;
     server_name your-domain.com;
     root /path/to/build;
     index index.html;

     location / {
       try_files $uri $uri/ /index.html;
     }
   }
   ```

## Security Considerations

- Never commit `.env` files with sensitive data
- Validate all user inputs
- Sanitize data before rendering
- Use HTTPS in production
- Implement rate limiting on the backend
- Keep dependencies updated

## Contributing

1. Follow the existing code style
2. Use meaningful component and variable names
3. Add comments for complex logic
4. Test thoroughly before submitting
5. Update documentation as needed

## License

This project is part of the Mine to Play system.

## Support

For issues or questions:
- Check the backend server logs
- Review browser console for client errors
- Ensure all dependencies are installed correctly
- Verify environment variables are set properly

---

**Happy Mining!** ⛏️💎
