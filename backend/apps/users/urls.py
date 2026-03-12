from django.urls import path
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .models import CustomUser, Watchlist
from .serializers import RegisterSerializer, UserProfileSerializer, WatchlistSerializer, LoginSerializer


class LoginView(APIView):
    """POST /api/users/login/ - Login with email & password"""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            refresh = RefreshToken.for_user(user)
            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "email": user.email,
                "username": user.username
            })
        return Response(serializer.errors, status=400)


class RegisterView(APIView):
    """POST /api/users/register/"""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {"message": "Account ban gaya!", "email": user.email},
                status=201
            )
        return Response(serializer.errors, status=400)


class ProfileView(APIView):
    """
    GET  /api/users/profile/   → apni profile dekho
    PUT  /api/users/profile/   → update karo
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserProfileSerializer(request.user).data)

    def put(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)


class WatchlistView(APIView):
    """
    GET  /api/users/watchlists/   → saari watchlists
    POST /api/users/watchlists/   → naya watchlist banao
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        wl = Watchlist.objects.filter(user=request.user)
        return Response(WatchlistSerializer(wl, many=True).data)

    def post(self, request):
        serializer = WatchlistSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class WatchlistDetailView(APIView):
    """
    GET    /api/users/watchlists/<id>/
    PUT    /api/users/watchlists/<id>/   → symbols update karo
    DELETE /api/users/watchlists/<id>/
    """
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        try:
            return Watchlist.objects.get(pk=pk, user=user)
        except Watchlist.DoesNotExist:
            return None

    def get(self, request, pk):
        wl = self.get_object(pk, request.user)
        if not wl:
            return Response({"error": "Not found"}, status=404)
        return Response(WatchlistSerializer(wl).data)

    def put(self, request, pk):
        wl = self.get_object(pk, request.user)
        if not wl:
            return Response({"error": "Not found"}, status=404)
        serializer = WatchlistSerializer(wl, data=request.data, partial=True, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        wl = self.get_object(pk, request.user)
        if not wl:
            return Response({"error": "Not found"}, status=404)
        wl.delete()
        return Response(status=204)


class AddToWatchlistView(APIView):
    """
    POST /api/users/watchlists/<id>/add/
    Body: { "symbol": "RELIANCE" }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            wl     = Watchlist.objects.get(pk=pk, user=request.user)
            symbol = request.data.get("symbol", "").upper()
            if not symbol:
                return Response({"error": "Symbol required"}, status=400)
            if symbol not in wl.symbols:
                wl.symbols.append(symbol)
                wl.save(update_fields=["symbols"])
            return Response({"symbols": wl.symbols})
        except Watchlist.DoesNotExist:
            return Response({"error": "Not found"}, status=404)


class RemoveFromWatchlistView(APIView):
    """
    POST /api/users/watchlists/<id>/remove/
    Body: { "symbol": "RELIANCE" }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            wl     = Watchlist.objects.get(pk=pk, user=request.user)
            symbol = request.data.get("symbol", "").upper()
            wl.symbols = [s for s in wl.symbols if s != symbol]
            wl.save(update_fields=["symbols"])
            return Response({"symbols": wl.symbols})
        except Watchlist.DoesNotExist:
            return Response({"error": "Not found"}, status=404)


urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("register/", RegisterView.as_view(), name="register"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("watchlists/", WatchlistView.as_view(), name="watchlist-list"),
    path("watchlists/<int:pk>/", WatchlistDetailView.as_view(), name="watchlist-detail"),
    path("watchlists/<int:pk>/add/", AddToWatchlistView.as_view(), name="add-to-watchlist"),
    path("watchlists/<int:pk>/remove/", RemoveFromWatchlistView.as_view(), name="remove-from-watchlist"),
]