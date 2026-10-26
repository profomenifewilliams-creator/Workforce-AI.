# Generated as the initial migration for AfriLearn AI.
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.CreateModel(
            name="ChildProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nickname", models.CharField(max_length=40)),
                ("age_band", models.CharField(choices=[("3–6 years", "3–6 years"), ("7–9 years", "7–9 years"), ("10–12 years", "10–12 years"), ("13–17 years", "13–17 years")], max_length=16)),
                ("preferred_language", models.CharField(choices=[("English", "English"), ("Igbo", "Igbo"), ("Yoruba", "Yoruba"), ("Hausa", "Hausa"), ("Swahili", "Swahili")], default="English", max_length=12)),
                ("avatar_key", models.CharField(choices=[("sunrise", "Sunrise"), ("star", "Star"), ("leaf", "Leaf"), ("comet", "Comet"), ("rainbow", "Rainbow"), ("robot", "Robot")], default="sunrise", max_length=12)),
                ("interests", models.JSONField(blank=True, default=list)),
                ("guardian_acknowledged_at", models.DateTimeField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("parent", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="learner_profiles", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["created_at"]},
        ),
        migrations.CreateModel(
            name="LearningProgress",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("world_id", models.CharField(choices=[("math", "Math Mountain"), ("science", "Science Galaxy"), ("language", "Language Jungle"), ("code", "Code City"), ("creative", "Creative Island"), ("heritage", "African Heritage")], max_length=16)),
                ("xp", models.PositiveIntegerField(default=0)),
                ("lessons_completed", models.PositiveIntegerField(default=0)),
                ("progress_percent", models.PositiveSmallIntegerField(default=0)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("child", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="progress", to="learning.childprofile")),
            ],
            options={"ordering": ["world_id"]},
        ),
        migrations.AddConstraint(
            model_name="learningprogress",
            constraint=models.UniqueConstraint(fields=("child", "world_id"), name="unique_child_learning_world"),
        ),
    ]
