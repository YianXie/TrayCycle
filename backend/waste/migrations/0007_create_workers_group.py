from django.db import migrations

def create_user_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.get_or_create(name='Workers')

def remove_user_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name__exact="Workers").delete()

class Migration(migrations.Migration):

    dependencies = [
        ('waste', '0006_alter_overproductionlog_date'),
    ]

    operations = [
        migrations.RunPython(create_user_groups, reverse_code=remove_user_groups),
    ]
