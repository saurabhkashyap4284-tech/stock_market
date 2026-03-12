from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import CustomUser, Watchlist
from .serializers import RegisterSerializer, UserProfileSerializer, WatchlistSerializer


class RegisterView(APIView):
    """
    POST /api/users/register/
    Naya user register karo.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {"id": user.id, "email": user.email, "message": "Registration successful"},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(APIView):
    """
    GET  /api/users/profile/  → apna profile
    PUT  /api/users/profile/  → update karo
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WatchlistView(APIView):
    """
    GET  /api/users/watchlists/       → saare watchlist
    POST /api/users/watchlists/       → naya watchlist banao
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        watchlists = Watchlist.objects.filter(user=request.user).order_by("-updated_at")
        serializer = WatchlistSerializer(watchlists, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = WatchlistSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WatchlistDetailView(APIView):
    """
    GET    /api/users/watchlists/<id>/   → detail
    PUT    /api/users/watchlists/<id>/   → update
    DELETE /api/users/watchlists/<id>/   → delete
    """
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        try:
            return Watchlist.objects.get(pk=pk, user=user)
        except Watchlist.DoesNotExist:
            return None

    def get(self, request, pk):
        watchlist = self.get_object(pk, request.user)
        if not watchlist:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = WatchlistSerializer(watchlist)
        return Response(serializer.data)

    def put(self, request, pk):
        watchlist = self.get_object(pk, request.user)
        if not watchlist:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = WatchlistSerializer(watchlist, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        watchlist = self.get_object(pk, request.user)
        if not watchlist:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        watchlist.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AddToWatchlistView(APIView):
    """
    POST /api/users/watchlists/<id>/add/
    Body: {"symbol": "RELIANCE"}
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            watchlist = Watchlist.objects.get(pk=pk, user=request.user)
        except Watchlist.DoesNotExist:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        symbol = request.data.get("symbol", "").upper()
        if not symbol:
            return Response({"error": "symbol required"}, status=status.HTTP_400_BAD_REQUEST)

        if symbol not in watchlist.symbols:
            watchlist.symbols.append(symbol)
            watchlist.save()

        return Response(WatchlistSerializer(watchlist).data)


class RemoveFromWatchlistView(APIView):
    """
    POST /api/users/watchlists/<id>/remove/
    Body: {"symbol": "RELIANCE"}
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            watchlist = Watchlist.objects.get(pk=pk, user=request.user)
        except Watchlist.DoesNotExist:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        symbol = request.data.get("symbol", "").upper()
        if not symbol:
            return Response({"error": "symbol required"}, status=status.HTTP_400_BAD_REQUEST)

        if symbol in watchlist.symbols:
            watchlist.symbols.remove(symbol)
            watchlist.save()

        return Response(WatchlistSerializer(watchlist).data)