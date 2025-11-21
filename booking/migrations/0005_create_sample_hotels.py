from django.db import migrations


def create_sample_hotels(apps, schema_editor):
    Hotel = apps.get_model('booking', 'Hotel')
    # create a few sample hotels for testing
    sample_data = [
        {
            'name': 'Seaside Inn',
            'location': 'Cebu City',
            'description': 'Cozy hotel near the beach with free breakfast.',
            'price_per_night': '1500.00',
        },
        {
            'name': 'Mountain View Lodge',
            'location': 'Baguio',
            'description': 'Scenic lodge with mountainside views and fireplace.',
            'price_per_night': '2200.00',
        },
        {
            'name': 'City Center Hotel',
            'location': 'Manila',
            'description': 'Convenient location in the city center, close to malls.',
            'price_per_night': '1800.00',
        },
    ]

    for data in sample_data:
        Hotel.objects.get_or_create(name=data['name'], defaults=data)


def reverse_func(apps, schema_editor):
    Hotel = apps.get_model('booking', 'Hotel')
    Hotel.objects.filter(name__in=['Seaside Inn', 'Mountain View Lodge', 'City Center Hotel']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0004_alter_hotel_image'),
    ]

    operations = [
        migrations.RunPython(create_sample_hotels, reverse_func),
    ]
