"""
Load testing configuration using Locust.

Usage:
    locust -f server/tests/load/locustfile.py --host=http://localhost:5000
"""
from locust import HttpUser, task, between, events
import random
import string
import json


def generate_wallet_address():
    """Generate a random wallet address for testing."""
    chars = string.ascii_letters + string.digits
    return '1' + ''.join(random.choices(chars, k=42))


class M2PUser(HttpUser):
    """Simulated M2P user for load testing."""

    wait_time = between(1, 5)  # Wait 1-5 seconds between tasks

    def on_start(self):
        """Called when a user starts."""
        self.wallet_address = generate_wallet_address()
        self.register_player()

    def register_player(self):
        """Register a new player."""
        payload = {
            'wallet_address': self.wallet_address,
            'username': f'LoadTest_{random.randint(1000, 9999)}'
        }

        with self.client.post(
            '/api/register',
            json=payload,
            catch_response=True
        ) as response:
            if response.status_code == 201:
                response.success()
            elif response.status_code == 409:
                # Already registered - that's ok
                response.success()
            else:
                response.failure(f"Registration failed: {response.status_code}")

    @task(3)
    def get_player(self):
        """Get player information."""
        with self.client.get(
            f'/api/player/{self.wallet_address}',
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 404:
                response.failure("Player not found")
            else:
                response.failure(f"Get player failed: {response.status_code}")

    @task(5)
    def get_leaderboard_all(self):
        """Get all-time leaderboard."""
        with self.client.get(
            '/api/leaderboard?period=all',
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Leaderboard failed: {response.status_code}")

    @task(2)
    def get_leaderboard_daily(self):
        """Get daily leaderboard."""
        with self.client.get(
            '/api/leaderboard?period=daily',
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Leaderboard failed: {response.status_code}")

    @task(2)
    def get_leaderboard_weekly(self):
        """Get weekly leaderboard."""
        with self.client.get(
            '/api/leaderboard?period=weekly',
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Leaderboard failed: {response.status_code}")

    @task(2)
    def get_leaderboard_monthly(self):
        """Get monthly leaderboard."""
        with self.client.get(
            '/api/leaderboard?period=monthly',
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Leaderboard failed: {response.status_code}")

    @task(1)
    def get_achievements(self):
        """Get all achievements."""
        with self.client.get(
            '/api/achievements',
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Achievements failed: {response.status_code}")

    @task(1)
    def get_player_achievements(self):
        """Get player's achievements."""
        with self.client.get(
            f'/api/player/{self.wallet_address}/achievements',
            catch_response=True
        ) as response:
            if response.status_code in [200, 404]:
                response.success()
            else:
                response.failure(f"Player achievements failed: {response.status_code}")


class AdminUser(HttpUser):
    """Simulated admin user for load testing."""

    wait_time = between(5, 15)

    @task
    def get_stats(self):
        """Get system statistics."""
        with self.client.get(
            '/api/admin/stats',
            catch_response=True
        ) as response:
            if response.status_code in [200, 401, 404]:
                response.success()
            else:
                response.failure(f"Stats failed: {response.status_code}")


class WebSocketUser(HttpUser):
    """Simulated WebSocket user for load testing."""

    wait_time = between(1, 3)

    def on_start(self):
        """Connect to WebSocket."""
        # WebSocket connection would be established here
        pass

    @task
    def listen_events(self):
        """Listen for WebSocket events."""
        # Simulate listening for events
        pass


# Event handlers for custom metrics
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when test starts."""
    print("Load test starting...")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when test stops."""
    print("Load test completed!")
    print(f"Total requests: {environment.stats.total.num_requests}")
    print(f"Total failures: {environment.stats.total.num_failures}")
    print(f"Average response time: {environment.stats.total.avg_response_time:.2f}ms")
    print(f"RPS: {environment.stats.total.total_rps:.2f}")


# Custom load test shapes
from locust import LoadTestShape


class StepLoadShape(LoadTestShape):
    """
    Step load pattern:
    - Start with 10 users
    - Add 10 users every 60 seconds
    - Up to 100 users
    - Run for 600 seconds total
    """

    step_time = 60
    step_load = 10
    spawn_rate = 5
    time_limit = 600

    def tick(self):
        run_time = self.get_run_time()

        if run_time > self.time_limit:
            return None

        current_step = run_time // self.step_time
        user_count = min(current_step * self.step_load + 10, 100)

        return (user_count, self.spawn_rate)


class SpikeLoadShape(LoadTestShape):
    """
    Spike load pattern:
    - Normal load: 20 users
    - Spike: 200 users
    - Alternates every 120 seconds
    """

    time_limit = 600
    spike_duration = 120

    def tick(self):
        run_time = self.get_run_time()

        if run_time > self.time_limit:
            return None

        # Determine if we're in a spike
        cycle_time = run_time % (self.spike_duration * 2)

        if cycle_time < self.spike_duration:
            # Normal load
            return (20, 5)
        else:
            # Spike load
            return (200, 20)
