from django.db import migrations


def clear_confidence(apps, schema_editor):
    PersonSongPreference = apps.get_model('band', 'PersonSongPreference')
    PersonSongPreference.objects.exclude(confidence='').update(confidence='')


class Migration(migrations.Migration):

    dependencies = [
        ('band', '0008_servicemember'),
    ]

    operations = [
        migrations.RunPython(clear_confidence, migrations.RunPython.noop),
    ]
