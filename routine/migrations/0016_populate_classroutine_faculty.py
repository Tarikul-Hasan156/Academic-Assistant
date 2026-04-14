# Generated migration to populate faculty field in ClassRoutine based on faculty_code

from django.db import migrations

def populate_faculty(apps, schema_editor):
    """Populate faculty field in ClassRoutine based on matching faculty_code"""
    ClassRoutine = apps.get_model('routine', 'ClassRoutine')
    Faculty = apps.get_model('routine', 'Faculty')
    
    classroutines = ClassRoutine.objects.filter(faculty__isnull=True, faculty_code__isnull=False)
    
    for classroutine in classroutines:
        try:
            faculty = Faculty.objects.get(faculty_code=classroutine.faculty_code)
            classroutine.faculty = faculty
            classroutine.save(update_fields=['faculty'])
            print(f"Updated ClassRoutine {classroutine.class_code} with Faculty {faculty.name}")
        except Faculty.DoesNotExist:
            print(f"Warning: Faculty with code {classroutine.faculty_code} not found for ClassRoutine {classroutine.class_code}")
        except Faculty.MultipleObjectsReturned:
            print(f"Warning: Multiple Faculty with code {classroutine.faculty_code} found for ClassRoutine {classroutine.class_code}")

def reverse_populate(apps, schema_editor):
    """Reverse the population (optional)"""
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('routine', '0015_classroutine_faculty'),
    ]

    operations = [
        migrations.RunPython(populate_faculty, reverse_populate),
    ]
