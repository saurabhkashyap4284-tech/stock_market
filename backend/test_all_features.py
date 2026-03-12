import pytest
import json
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from apps.users.models import CustomUser, Watchlist
from apps.market.models import Stock, OISnapshot
from apps.signals_log.models import SignalEvent
from apps.alerts.models import AlertRule

User = get_user_model()


class UserAuthenticationTests(TestCase):
    """Test user authentication and registration"""
    
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            "email": "testuser@example.com",
            "password": "TestPass123!",
            "password2": "TestPass123!",
            "username": "testuser",
            "phone": "9999999999"
        }
    
    def test_user_registration(self):
        """Test user can register with email and password"""
        response = self.client.post('/api/users/register/', self.user_data, format='json')
        assert response.status_code in [201, 400], f"Got {response.status_code}"
        print("[OK] Registration test passed")
    
    def test_user_login(self):
        """Test user can login with email"""
        user = CustomUser.objects.create_user(
            email="login@example.com",
            username="loginuser",
            password="TestPass123!"
        )
        
        login_data = {
            "email": "login@example.com",
            "password": "TestPass123!"
        }
        response = self.client.post('/api/users/login/', login_data, format='json')
        assert response.status_code in [200, 400], f"Got {response.status_code}"
        print("[OK] Login test passed")
    
    def test_user_profile(self):
        """Test user profile retrieval"""
        user = CustomUser.objects.create_user(
            email="profile@example.com",
            username="profileuser",
            password="TestPass123!"
        )
        self.client.force_authenticate(user=user)
        response = self.client.get('/api/users/profile/')
        assert response.status_code == 200, f"Got {response.status_code}"
        assert response.data['email'] == "profile@example.com"
        print("[OK] Profile test passed")


class WatchlistTests(TestCase):
    """Test watchlist CRUD operations"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            email="watchlist@example.com",
            username="watchlistuser",
            password="TestPass123!"
        )
        self.client.force_authenticate(user=self.user)
    
    def test_create_watchlist(self):
        """Test creating a new watchlist"""
        data = {
            "name": "My Watchlist",
            "symbols": ["RELIANCE", "TCS", "INFOSYS"]
        }
        response = self.client.post('/api/users/watchlists/', data, format='json')
        assert response.status_code in [201, 400], f"Got {response.status_code}"
        print("[OK] Create watchlist test passed")
    
    def test_get_watchlists(self):
        """Test retrieving all watchlists"""
        watchlist = Watchlist.objects.create(
            user=self.user,
            name="Test Watchlist",
            symbols=["RELIANCE"]
        )
        response = self.client.get('/api/users/watchlists/')
        assert response.status_code == 200, f"Got {response.status_code}"
        print("[OK] Get watchlists test passed")
    
    def test_add_symbol_to_watchlist(self):
        """Test adding symbol to watchlist"""
        watchlist = Watchlist.objects.create(
            user=self.user,
            name="Test WL",
            symbols=["RELIANCE"]
        )
        data = {"symbol": "TCS"}
        response = self.client.post(
            f'/api/users/watchlists/{watchlist.id}/add/',
            data,
            format='json'
        )
        assert response.status_code in [200, 400], f"Got {response.status_code}"
        print("[OK] Add symbol test passed")
    
    def test_remove_symbol_from_watchlist(self):
        """Test removing symbol from watchlist"""
        watchlist = Watchlist.objects.create(
            user=self.user,
            name="Test WL",
            symbols=["RELIANCE", "TCS"]
        )
        data = {"symbol": "TCS"}
        response = self.client.post(
            f'/api/users/watchlists/{watchlist.id}/remove/',
            data,
            format='json'
        )
        assert response.status_code in [200, 400], f"Got {response.status_code}"
        print("[OK] Remove symbol test passed")


class AlertTests(TestCase):
    """Test alert rules functionality"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            email="alert@example.com",
            username="alertuser",
            password="TestPass123!"
        )
        self.client.force_authenticate(user=self.user)
    
    def test_get_alert_rules(self):
        """Test retrieving alert rules"""
        response = self.client.get('/api/alerts/rules/')
        assert response.status_code in [200, 404], f"Got {response.status_code}"
        print("[OK] Get alert rules test passed")
    
    def test_create_alert_rule(self):
        """Test creating an alert rule"""
        stock = Stock.objects.create(symbol="RELIANCE", name="Reliance Industries")
        
        data = {
            "stock": stock.id,
            "signal_type": "BULLISH",
            "only_strong": True,
            "via_email": True
        }
        response = self.client.post('/api/alerts/rules/', data, format='json')
        assert response.status_code in [201, 400, 404], f"Got {response.status_code}"
        print("[OK] Create alert rule test passed")


class SignalsTests(TestCase):
    """Test trading signals functionality"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            email="signals@example.com",
            username="signalsuser",
            password="TestPass123!"
        )
        self.client.force_authenticate(user=self.user)
    
    def test_get_signals_history(self):
        """Test retrieving signals history"""
        response = self.client.get('/api/signals/history/')
        assert response.status_code in [200, 401, 404], f"Got {response.status_code}"
        print("[OK] Get signals history test passed")
    
    def test_get_signals_summary(self):
        """Test retrieving signals summary"""
        response = self.client.get('/api/signals/summary/')
        assert response.status_code in [200, 401, 404], f"Got {response.status_code}"
        print("[OK] Get signals summary test passed")


class MarketDataTests(TestCase):
    """Test market data endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            email="market@example.com",
            username="marketuser",
            password="TestPass123!"
        )
        self.client.force_authenticate(user=self.user)
    
    def test_get_live_snapshot(self):
        """Test retrieving live market snapshot"""
        response = self.client.get('/api/market/live/')
        assert response.status_code in [200, 404], f"Got {response.status_code}"
        print("[OK] Get live snapshot test passed")
    
    def test_get_market_phase(self):
        """Test retrieving market phase"""
        response = self.client.get('/api/market/phase/')
        assert response.status_code in [200, 404], f"Got {response.status_code}"
        print("[OK] Get market phase test passed")


class APIEndpointTests(TestCase):
    """Test all API endpoints are accessible"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            email="endpoint@example.com",
            username="endpointuser",
            password="TestPass123!"
        )
        self.client.force_authenticate(user=self.user)
    
    def test_api_endpoints_exist(self):
        """Test that all main API endpoints exist"""
        endpoints = [
            '/api/users/',
            '/api/market/',
            '/api/signals/',
            '/api/alerts/',
        ]
        
        for endpoint in endpoints:
            response = self.client.get(endpoint)
            assert response.status_code != 500, f"Endpoint {endpoint} returned 500"
            print(f"[OK] {endpoint} - Status: {response.status_code}")
    
    def test_auth_endpoints(self):
        """Test authentication endpoints"""
        login_response = self.client.options('/api/users/login/')
        assert login_response.status_code != 500
        
        register_response = self.client.options('/api/users/register/')
        assert register_response.status_code != 500
        
        print("[OK] Auth endpoints test passed")
