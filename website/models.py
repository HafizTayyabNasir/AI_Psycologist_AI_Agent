from django.db import models
from django.utils import timezone


class ContactMessage(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now, editable=False)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.full_name} - '{self.subject}'"

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"