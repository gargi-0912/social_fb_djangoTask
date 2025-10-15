from .repositories import FeedRepository, CommentRepository
from django.core.cache import cache
from .utils.loggers import logger 

REPORT_THRESHOLD = 3 

class FeedService:
    """Handles business logic for Feed creation, listing, and reporting."""

    @staticmethod
    def _invalidate_feed_cache():
        """Helper to clear all feed list caches when data changes."""
        keys = cache.keys('feeds_list*')
        cache.delete_many(keys)

    # @staticmethod
    # def create_feed(user, text_content, image_urls):
    #     try:
    #         feed = FeedRepository.create_feed(user, text_content, image_urls)
    #         FeedService._invalidate_feed_cache() 
    #         return feed
    #     except Exception as e:
    #         logger.error(f"Error creating feed for user {user.id}", exc_info=True)
    #         raise e
    @staticmethod
    def create_feed(user, text_content, images=None):
        """
        Creates a feed post along with uploaded images.
        `images` should be a list of uploaded files from request.FILES.
        """
        from feed_app.models import Feed, FeedImage  # import models if needed

        try:
            # Create main feed
            feed = Feed.objects.create(user=user, text_content=text_content)

            # Save uploaded images
            if images:
                for idx, img in enumerate(images[:4]):  # max 4 images
                    FeedImage.objects.create(feed=feed, image=img, order=idx)

            FeedService._invalidate_feed_cache()
            return feed
        except Exception as e:
            logger.error(f"Error creating feed for user {user.id}", exc_info=True)
            raise e



    @staticmethod
    def get_feeds(offset, limit):
        return FeedRepository.get_latest_feeds(offset, limit)

    @staticmethod
    def handle_report(feed_id, reporting_user):
        """Manages the reporting process, checking the 3 unique user threshold."""
        feed = FeedRepository.get_feed_by_id(feed_id)
        if not feed or not feed.is_active:
            return None 

        new_count = FeedRepository.create_report_and_get_count(feed, reporting_user)

        if new_count >= REPORT_THRESHOLD and feed.is_active:
            # If 3 unique users report a feed, it should disappear
            feed.is_active = False 
            feed.save(update_fields=['is_active'])
            FeedService._invalidate_feed_cache()
            logger.info(f"Feed {feed.id} automatically deactivated due to {REPORT_THRESHOLD} reports.")

        return feed

class CommentService:
    @staticmethod
    def create_comment(feed_id, user, text_content):
        feed = FeedRepository.get_feed_by_id(feed_id)
        if not feed or not feed.is_active:
            raise ValueError("Feed not found or is inactive.")
            
        return CommentRepository.create_comment(feed, user, text_content)