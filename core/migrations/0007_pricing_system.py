# Generated migration for pricing system changes

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_wasteproduct_photo'),
    ]

    operations = [
        migrations.RenameField(
            model_name='wasteproduct',
            old_name='price_per_ton',
            new_name='admin_price_per_ton',
        ),
        migrations.AddField(
            model_name='order',
            name='company_price_per_ton',
            field=models.DecimalField(decimal_places=2, default=0.01, help_text='Price offered by company', max_digits=10, validators=[django.core.validators.MinValueValidator(0.01)]),
            preserve_default=False,
        ),
    ]