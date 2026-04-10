from django.db import migrations, models


def copy_category_name_from_name_en(apps, schema_editor):
    Category = apps.get_model('blog', 'Category')
    for category in Category.objects.all():
        category.name = category.name_en
        category.save(update_fields=['name'])


class Migration(migrations.Migration):
    dependencies = [
        ('blog', '0002_remove_category_name_category_name_en_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='name',
            field=models.CharField(max_length=100, null=True, unique=True),
        ),
        migrations.RunPython(copy_category_name_from_name_en, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='category',
            name='name_en',
        ),
        migrations.RemoveField(
            model_name='category',
            name='name_kk',
        ),
        migrations.RemoveField(
            model_name='category',
            name='name_ru',
        ),
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
