# Migration to populate NULL departments in ClassRoutine based on class_code patterns

from django.db import migrations

def populate_departments(apps, schema_editor):
    """Populate NULL departments in ClassRoutine"""
    ClassRoutine = apps.get_model('routine', 'ClassRoutine')
    
    # Find all ClassRoutines with NULL department
    null_routines = ClassRoutine.objects.filter(department__isnull=True)
    
    for routine in null_routines:
        # Try to find another ClassRoutine with same class_code but with a valid department
        similar = ClassRoutine.objects.filter(
            class_code=routine.class_code,
            department__isnull=False
        ).first()
        
        if similar:
            routine.department = similar.department
            routine.save(update_fields=['department'])
            print(f"Updated ClassRoutine {routine.id} ({routine.class_code}): set department to {similar.department}")
        else:
            # If no similar routine found, infer from class_code pattern
            # Most codes start with department prefix (e.g., CSE 301, EEE 401, etc.)
            code_parts = routine.class_code.split()
            if code_parts:
                dept_prefix = code_parts[0]
                # Map common prefixes to departments
                dept_map = {
                    'CSE': 'CSE',
                    'EEE': 'EEE',
                    'BBA': 'BBA',
                    'CIVIL': 'CIVIL',
                    'MATH': 'MATH',
                }
                if dept_prefix in dept_map:
                    routine.department = dept_map[dept_prefix]
                    routine.save(update_fields=['department'])
                    print(f"Updated ClassRoutine {routine.id} ({routine.class_code}): inferred department to {dept_map[dept_prefix]}")

def reverse_populate(apps, schema_editor):
    """Reverse the operation (optional)"""
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('routine', '0016_populate_classroutine_faculty'),
    ]

    operations = [
        migrations.RunPython(populate_departments, reverse_populate),
    ]
