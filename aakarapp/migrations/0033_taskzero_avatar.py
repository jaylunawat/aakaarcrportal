from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("aakarapp", "0032_alter_taskzero_options"),
    ]

    operations = [
        migrations.AddField(
            model_name="taskzero",
            name="avatar",
            field=models.CharField(
                choices=[
                    ("rhino-orange", "Rhino — orange"),
                    ("black-bear", "Black bear"),
                    ("koala", "Koala"),
                    ("brown-bear", "Brown bear"),
                    ("owl", "Owl"),
                    ("deer", "Deer"),
                    ("raccoon", "Raccoon"),
                    ("fox", "Fox"),
                    ("rhino-green", "Rhino — green"),
                ],
                default="fox",
                max_length=20,
            ),
        ),
    ]
