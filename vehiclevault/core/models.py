from django.db import models

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name} - {self.subject}"

class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    category = models.CharField(max_length=50, choices=[('general', 'General'), ('buying', 'Buying'), ('selling', 'Selling'), ('finance', 'Finance'), ('technical', 'Technical')], default='general')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']

    def __str__(self):
        return self.question

class PrivacyPolicy(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    last_updated = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class TermsAndConditions(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    last_updated = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class AboutUs(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    mission = models.TextField(blank=True)
    vision = models.TextField(blank=True)
    team_description = models.TextField(blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class Sitemap(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    last_updated = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

