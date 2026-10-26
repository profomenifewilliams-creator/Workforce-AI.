from django.conf import settings
from django.db import models


class ChildProfile(models.Model):
    AGE_BANDS = [
        ("3–6 years", "3–6 years"),
        ("7–9 years", "7–9 years"),
        ("10–12 years", "10–12 years"),
        ("13–17 years", "13–17 years"),
    ]
    LANGUAGES = [
        ("English", "English"),
        ("Igbo", "Igbo"),
        ("Yoruba", "Yoruba"),
        ("Hausa", "Hausa"),
        ("Swahili", "Swahili"),
    ]
    AVATARS = [
        ("sunrise", "Sunrise"),
        ("star", "Star"),
        ("leaf", "Leaf"),
        ("comet", "Comet"),
        ("rainbow", "Rainbow"),
        ("robot", "Robot"),
    ]

    parent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="learner_profiles")
    nickname = models.CharField(max_length=40)
    age_band = models.CharField(max_length=16, choices=AGE_BANDS)
    preferred_language = models.CharField(max_length=12, choices=LANGUAGES, default="English")
    avatar_key = models.CharField(max_length=12, choices=AVATARS, default="sunrise")
    interests = models.JSONField(default=list, blank=True)
    guardian_acknowledged_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.nickname} ({self.age_band})"


class LearningProgress(models.Model):
    WORLDS = [
        ("math", "Math Mountain"),
        ("science", "Science Galaxy"),
        ("language", "Language Jungle"),
        ("code", "Code City"),
        ("creative", "Creative Island"),
        ("heritage", "African Heritage"),
    ]
    child = models.ForeignKey(ChildProfile, on_delete=models.CASCADE, related_name="progress")
    world_id = models.CharField(max_length=16, choices=WORLDS)
    xp = models.PositiveIntegerField(default=0)
    lessons_completed = models.PositiveIntegerField(default=0)
    progress_percent = models.PositiveSmallIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["child", "world_id"], name="unique_child_learning_world")
        ]
        ordering = ["world_id"]

    def __str__(self):
        return f"{self.child.nickname}: {self.get_world_id_display()}"
