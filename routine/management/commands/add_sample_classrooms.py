from django.core.management.base import BaseCommand
from routine.models import Classroom


class Command(BaseCommand):
    help = 'Add sample classrooms to the database'

    def handle(self, *args, **options):
        """Create sample classrooms for each building"""
        
        classrooms_data = [
            # Building B-1
            {'room_number': '101', 'building': 'B-1', 'capacity': 50, 'floor': 1},
            {'room_number': '102', 'building': 'B-1', 'capacity': 60, 'floor': 1},
            {'room_number': '103', 'building': 'B-1', 'capacity': 45, 'floor': 1},
            {'room_number': '201', 'building': 'B-1', 'capacity': 55, 'floor': 2},
            {'room_number': '202', 'building': 'B-1', 'capacity': 70, 'floor': 2},
            {'room_number': '203', 'building': 'B-1', 'capacity': 40, 'floor': 2},
            
            # Building B-2
            {'room_number': '101', 'building': 'B-2', 'capacity': 50, 'floor': 1},
            {'room_number': '102', 'building': 'B-2', 'capacity': 60, 'floor': 1},
            {'room_number': '103', 'building': 'B-2', 'capacity': 48, 'floor': 1},
            {'room_number': '201', 'building': 'B-2', 'capacity': 65, 'floor': 2},
            {'room_number': '202', 'building': 'B-2', 'capacity': 55, 'floor': 2},
            {'room_number': '203', 'building': 'B-2', 'capacity': 42, 'floor': 2},
            
            # Building B-3
            {'room_number': '101', 'building': 'B-3', 'capacity': 50, 'floor': 1},
            {'room_number': '102', 'building': 'B-3', 'capacity': 58, 'floor': 1},
            {'room_number': '103', 'building': 'B-3', 'capacity': 46, 'floor': 1},
            {'room_number': '201', 'building': 'B-3', 'capacity': 60, 'floor': 2},
            {'room_number': '202', 'building': 'B-3', 'capacity': 52, 'floor': 2},
            {'room_number': '203', 'building': 'B-3', 'capacity': 44, 'floor': 2},
            
            # Building B-4
            {'room_number': '101', 'building': 'B-4', 'capacity': 50, 'floor': 1},
            {'room_number': '102', 'building': 'B-4', 'capacity': 62, 'floor': 1},
            {'room_number': '103', 'building': 'B-4', 'capacity': 47, 'floor': 1},
            {'room_number': '201', 'building': 'B-4', 'capacity': 58, 'floor': 2},
            {'room_number': '202', 'building': 'B-4', 'capacity': 50, 'floor': 2},
            {'room_number': '203', 'building': 'B-4', 'capacity': 45, 'floor': 2},
        ]
        
        created_count = 0
        skipped_count = 0
        
        for classroom_data in classrooms_data:
            building = classroom_data['building']
            room_number = classroom_data['room_number']
            full_room_id = f"{building}-{room_number}"
            
            # Check if classroom already exists
            if Classroom.objects.filter(
                building=building,
                room_number=room_number
            ).exists():
                self.stdout.write(
                    self.style.WARNING(f'⊘ Skipped: {full_room_id} (already exists)')
                )
                skipped_count += 1
                continue
            
            # Create classroom
            classroom = Classroom.objects.create(**classroom_data)
            created_count += 1
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Created: {full_room_id} (Capacity: {classroom_data["capacity"]}, Floor: {classroom_data["floor"]})'
                )
            )
        
        # Print summary
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Summary: Created {created_count} classrooms, Skipped {skipped_count} (already exist)'
            )
        )
