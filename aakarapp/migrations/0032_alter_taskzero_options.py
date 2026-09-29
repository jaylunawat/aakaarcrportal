from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("aakarapp", "0031_alter_taskzero_address_alter_taskzero_dept"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="taskzero",
            options={
                "ordering": ("names",),
                "verbose_name": "CR profile",
                "verbose_name_plural": "CR profiles",
            },
        ),
    ]
