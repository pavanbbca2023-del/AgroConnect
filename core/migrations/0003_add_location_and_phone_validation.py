# Generated migration for adding location field and phone validation

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_alter_companyprofile_registration_number_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='wasteproduct',
            name='location',
            field=models.CharField(default='', help_text='Location where waste is available', max_length=200),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='phone',
            field=models.CharField(max_length=15, validators=[django.core.validators.RegexValidator(message='Phone number must be 10-15 digits, optionally starting with +', regex='^[+]?[0-9]{10,15}$')]),
        ),
    ]