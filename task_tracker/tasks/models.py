from django.db import models
from django.core.validators import MinLengthValidator

class Task(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('review', 'In Review'),
        ('done', 'Completed'),
    ]
    
    title = models.CharField(
        max_length=200,
        validators=[MinLengthValidator(1)],
        help_text="Title of the task"
    )
    description = models.TextField(blank=True, help_text="Detailed description of the task")
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium',
        help_text="Priority level of the task"
    )
    due_date = models.DateField(null=True, blank=True, help_text="Due date for the task")
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='todo',
        help_text="Current status of the task"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
            models.Index(fields=['due_date']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"