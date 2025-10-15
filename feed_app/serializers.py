# from rest_framework import serializers
# from .models import Feed, FeedImage, Comment
# from django.contrib.auth.models import User

# # --- Nested Serializers for Read Operations ---

# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ('id', 'username')

# class FeedImageSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = FeedImage
#         fields = ('image_url', 'order')

# class CommentSerializer(serializers.ModelSerializer):
#     user = UserSerializer(read_only=True)
    
#     class Meta:
#         model = Comment
#         fields = ('id', 'user', 'text_content', 'created_at')
#         read_only_fields = ('user', 'created_at') 

# # --- Main Feed Serializer (Read/Listing) ---

# class FeedListSerializer(serializers.ModelSerializer):
#     user = UserSerializer(read_only=True)
#     images = FeedImageSerializer(many=True, read_only=True)
#     comments = CommentSerializer(many=True, read_only=True) 

#     class Meta:
#         model = Feed
#         fields = ('id', 'user', 'text_content', 'images', 'comments', 'created_at')

# # --- Feed Creation Serializer (Write) ---

# class FeedCreateSerializer(serializers.Serializer):
#     """Handles validation for feed creation."""
#     text_content = serializers.CharField(required=False, allow_blank=True, max_length=5000)
#     image_urls = serializers.ListField(
#         child=serializers.CharField(max_length=255), 
#         required=False, 
#         max_length=4 
#     )

#     def validate_image_urls(self, value):
#         if len(value) > 4:
#             raise serializers.ValidationError("A feed can only have up to 4 images.")
#         return value
        
# # --- User Authentication Serializers ---

# class UserRegisterSerializer(serializers.ModelSerializer):
#     """Serializer for new user registration."""
#     password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
#     password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

#     class Meta:
#         model = User
#         fields = ('username', 'email', 'password', 'password2')

#     def validate(self, data):
#         if data['password'] != data['password2']:
#             raise serializers.ValidationError({"password": "Password fields didn't match."})
#         if User.objects.filter(username=data['username']).exists():
#             raise serializers.ValidationError({"username": "A user with that username already exists."})
#         return data

#     def create(self, validated_data):
#         user = User.objects.create_user(
#             username=validated_data['username'],
#             email=validated_data['email'],
#             password=validated_data['password']
#         )
#         return 



from rest_framework import serializers
from .models import Feed, FeedImage, Comment
from django.contrib.auth.models import User


# --- Nested Serializers for Read Operations ---

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')


class FeedImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedImage
        fields = ('id', 'image', 'order')  # ✅ use image field directly


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'user', 'text_content', 'created_at')
        read_only_fields = ('user', 'created_at')


# --- Main Feed Serializer (Read/Listing) ---

class FeedListSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    images = FeedImageSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Feed
        fields = ('id', 'user', 'text_content', 'images', 'comments', 'created_at')


# --- Feed Creation Serializer (Write) ---

class FeedCreateSerializer(serializers.ModelSerializer):
    """
    Handles feed creation with text and up to 4 uploaded images.
    """
    images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False,
        allow_empty=True
    )

    class Meta:
        model = Feed
        fields = ('text_content', 'images')

    def validate_images(self, value):
        """Ensure no more than 4 images are uploaded."""
        if len(value) > 4:
            raise serializers.ValidationError("A feed can only have up to 4 images.")
        return value

    def create(self, validated_data):
        """Create a Feed and its associated FeedImage entries."""
        images = validated_data.pop('images', [])
        request = self.context.get('request')
        user = request.user if request else None

        # Create Feed
        feed = Feed.objects.create(user=user, **validated_data)

        # Create FeedImage entries
        for idx, image in enumerate(images):
            FeedImage.objects.create(feed=feed, image=image, order=idx)

        return feed


# --- User Authentication Serializers ---

class UserRegisterSerializer(serializers.ModelSerializer):
    """Serializer for new user registration."""
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2')

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError({"username": "A user with that username already exists."})
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user
