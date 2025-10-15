from django.db import models
from django.contrib.auth.models import User

# All transactional data goes into PostgreSQL

class Feed(models.Model):
    """Stores the main feed post."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text_content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True) 
    report_count = models.IntegerField(default=0) 

    class Meta:
        indexes = [
            models.Index(fields=['-created_at', 'is_active']),
        ]
        verbose_name = "Feed Post"

# class FeedImage(models.Model):
#     """Stores up to 4 images for a feed post."""
#     feed = models.ForeignKey(Feed, related_name='images', on_delete=models.CASCADE)
#     image_url = models.ImageField(upload_to='feed_images/')
#     # image_url = models.CharField(max_length=255) # URL/Path to stored image
#     order = models.PositiveSmallIntegerField(default=0) 

#     class Meta:
#         ordering = ['order']
class FeedImage(models.Model):
    """Stores up to 4 images for a feed post."""
    feed = models.ForeignKey(Feed, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='feed_images/')  # renamed from image_url
    order = models.PositiveSmallIntegerField(default=0) 

    class Meta:
        ordering = ['order']

class Comment(models.Model):
    """Stores single-level comments."""
    feed = models.ForeignKey(Feed, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text_content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class FeedReport(models.Model):
    """Tracks unique user reports on a feed."""
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reason = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('feed', 'user') # Ensures 3 UNIQUE users report