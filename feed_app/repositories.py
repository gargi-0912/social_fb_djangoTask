from django.core.cache import cache
from .models import Feed, FeedReport, Comment, FeedImage
from django.db import transaction

class FeedRepository:
    """Handles direct database operations for Feed and related models."""

    @staticmethod
    def get_latest_feeds(offset=0, limit=10):
        """Fetches active feeds with Redis caching for performance."""
        cache_key = f'feeds_list_offset_{offset}_limit_{limit}'
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            return cached_data

        # Filter only active feeds and order by creation time
        queryset = Feed.objects.filter(is_active=True).order_by('-created_at')
        # Pre-fetch related data for efficient listing
        feeds = list(queryset[offset:offset + limit].prefetch_related('images', 'comments__user'))
        
        # Cache for 60 seconds (Meeting < 2 sec requirement)
        cache.set(cache_key, feeds, 60) 
        
        return feeds

    @staticmethod
    def get_feed_by_id(feed_id):
        return Feed.objects.filter(id=feed_id).first()

    # @staticmethod
    # @transaction.atomic
    # def create_feed(user, text_content, image_urls):
    #     feed = Feed.objects.create(user=user, text_content=text_content)
    #     for i, url in enumerate(image_urls[:4]): 
    #         FeedImage.objects.create(feed=feed, image_url=url, order=i + 1)
    #     return feed

    @staticmethod
    @transaction.atomic
    def create_feed(user, text_content, images):
        """
        images: list of uploaded file objects from request.FILES
        """
        feed = Feed.objects.create(user=user, text_content=text_content)
        for i, image in enumerate(images[:4]):
            FeedImage.objects.create(feed=feed, image=image, order=i)
        return feed


    @staticmethod
    @transaction.atomic
    def create_report_and_get_count(feed, user):
        """Creates the report and returns the *new* unique report count."""
        report, created = FeedReport.objects.get_or_create(feed=feed, user=user)
        
        if created:
            feed.report_count += 1
            feed.save(update_fields=['report_count'])
        
        return feed.report_count

class CommentRepository:
    """Handles direct database operations for Comment models."""
    @staticmethod
    def create_comment(feed, user, text_content):
        return Comment.objects.create(feed=feed, user=user, text_content=text_content)