"""
Base and common models for the application
"""
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    """
    Abstract base model that provides self-updating 'created_at' and 'updated_at' fields.
    All models should inherit from this to maintain consistency.
    """
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created At',
        db_index=True
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Updated At'
    )

    class Meta:
        abstract = True
        ordering = ['-created_at']


class SoftDeleteModel(models.Model):
    """
    Abstract base model that provides soft delete functionality.
    Objects are never actually deleted, just marked as deleted.
    """
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Deleted At'
    )
    is_deleted = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name='Is Deleted'
    )

    class Meta:
        abstract = True

    def soft_delete(self):
        """Mark object as deleted without removing from database"""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_deleted', 'deleted_at'])

    def restore(self):
        """Restore a soft-deleted object"""
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=['is_deleted', 'deleted_at'])


class FullyTrackedModel(TimeStampedModel, SoftDeleteModel):
    """
    Combines TimeStampedModel and SoftDeleteModel for comprehensive tracking.
    Use for critical models that need both timestamp and soft delete functionality.
    """
    class Meta:
        abstract = True
