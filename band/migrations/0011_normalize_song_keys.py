from django.db import migrations
import re

# Maps lowercase raw key strings → canonical form
_BASE = {'c': 'C', 'd': 'D', 'e': 'E', 'f': 'F', 'g': 'G', 'a': 'A', 'b': 'B'}
_FLAT_MAP = {'db': 'Db', 'eb': 'Eb', 'gb': 'Gb', 'ab': 'Ab', 'bb': 'Bb',
             'c#': 'Db', 'd#': 'Eb', 'f#': 'Gb', 'g#': 'Ab', 'a#': 'Bb',
             'd♭': 'Db', 'e♭': 'Eb', 'g♭': 'Gb',
             'a♭': 'Ab', 'b♭': 'Bb', 'c♯': 'Db',
             'd♯': 'Eb', 'f♯': 'Gb', 'g♯': 'Ab', 'a♯': 'Bb'}


def _normalize_key(raw):
    if not raw:
        return raw
    s = raw.strip()
    # Strip common suffixes
    lower = re.sub(r'\s*(major|maj|minor|min)\s*$', '', s.lower()).strip()
    minor = 'min' in s.lower() or s.lower().endswith('m')
    # Already canonical (e.g. 'D', 'Bb', 'Am')
    if s in ('C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B',
             'Cm', 'Dm', 'Em', 'Fm', 'Gm', 'Am', 'Bbm', 'Bm'):
        return s
    if lower in _FLAT_MAP:
        base = _FLAT_MAP[lower]
    elif lower in _BASE:
        base = _BASE[lower]
    else:
        # Try stripping trailing 'm' for minor lookup
        stripped = lower.rstrip('m')
        if stripped in _FLAT_MAP:
            base = _FLAT_MAP[stripped]
            minor = True
        elif stripped in _BASE:
            base = _BASE[stripped]
            minor = True
        else:
            return s  # unrecognised — leave unchanged
    if minor and not base.endswith('m'):
        base += 'm'
    return base


def normalize_keys(apps, schema_editor):
    Song = apps.get_model('band', 'Song')
    to_update = []
    for song in Song.objects.all():
        new_key = _normalize_key(song.default_key)
        if new_key != song.default_key:
            song.default_key = new_key
            to_update.append(song)
    if to_update:
        Song.objects.bulk_update(to_update, ['default_key'])


class Migration(migrations.Migration):

    dependencies = [
        ('band', '0010_church_pco_credentials'),
    ]

    operations = [
        migrations.RunPython(normalize_keys, migrations.RunPython.noop),
    ]
