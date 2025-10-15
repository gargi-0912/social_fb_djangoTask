from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from feed_app.services import FeedService, CommentService
from .serializers import (
    FeedListSerializer, 
    FeedCreateSerializer, 
    CommentSerializer, 
    UserRegisterSerializer
)

# --- Frontend Views with Authentication Logic ---
from rest_framework.parsers import MultiPartParser, FormParser
@require_http_methods(["GET"])
def feed_list_ui(request):
    """Renders the main Django Template UI, requiring authentication."""
    if not request.user.is_authenticated:
        return redirect('login') 
        
    context = {'current_username': request.user.username}
    return render(request, 'feed_app/feed_list.html', context)

@require_http_methods(["GET", "POST"])
def user_signup(request):
    """Handles user registration."""
    if request.user.is_authenticated:
        return redirect('feed_list_ui')

    if request.method == 'POST':
        serializer = UserRegisterSerializer(data=request.POST)
        if serializer.is_valid():
            try:
                user = serializer.save()
                login(request, user) 
                messages.success(request, 'Registration successful. Welcome!')
                return redirect('feed_list_ui')
            except Exception as e:
                from .utils.loggers import logger
                logger.error(f"Signup error for user {request.POST.get('username')}", exc_info=True)
                messages.error(request, 'An unexpected error occurred during registration.')
        else:
            for field, errors in serializer.errors.items():
                messages.error(request, f"{field}: {', '.join(errors)}")

    return render(request, 'auth/signup.html') 
from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
@require_http_methods(["GET", "POST"])
def user_login(request):
    """Handles user login."""
    if request.user.is_authenticated:
        return redirect('feed_list_ui')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {username}!")
            return redirect('feed_list_ui')
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'auth/login.html') 

@require_http_methods(["GET"])
def user_logout(request):
    """Handles user logout."""
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, "You have been logged out.")
    return redirect('login')


# --- DRF ViewSet (Backend APIs) ---
class FeedViewSet(viewsets.ViewSet):
    print("==========================")
    permission_classes = [IsAuthenticated]

    
    def list(self, request):
        try:
            limit = int(request.query_params.get('limit', 10))
            offset = int(request.query_params.get('offset', 0))
        except ValueError:
            return Response({"detail": "Invalid pagination parameters."}, status=status.HTTP_400_BAD_REQUEST)
        
        feeds = FeedService.get_feeds(offset=offset, limit=limit)
        
        serializer = FeedListSerializer(feeds, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
     

    # def create(self, request):
    #     serializer = FeedCreateSerializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)

    #     feed = FeedService.create_feed(
    #         user=request.user,
    #         text_content=serializer.validated_data.get('text_content', ''),
    #         image_urls=serializer.validated_data.get('image_urls', [])            
    #     )
    #     print("==========================")
    #     print(serializer.validated_data.get('image_urls', []))
        
    #     return Response(FeedListSerializer(feed).data, status=status.HTTP_201_CREATED)
    def create(self, request):
        serializer = FeedCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        feed = serializer.save()  # the serializer now handles feed + images creation

        return Response(FeedListSerializer(feed).data, status=status.HTTP_201_CREATED)


    @action(detail=True, methods=['post'])
    def report(self, request, pk=None):
        feed = FeedService.handle_report(feed_id=pk, reporting_user=request.user)
        
        if not feed:
            return Response({"detail": "Feed not found or is inactive."}, status=status.HTTP_404_NOT_FOUND)
        
        if not feed.is_active:
            return Response({"detail": "Feed removed due to reporting threshold."}, status=status.HTTP_200_OK)
            
        return Response({"detail": "Feed reported successfully."}, status=status.HTTP_200_OK)
        
    @action(detail=True, methods=['post'])
    def comments(self, request, pk=None):
        serializer = CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            comment = CommentService.create_comment(
                feed_id=pk,
                user=request.user,
                text_content=serializer.validated_data['text_content']
            )
            return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)