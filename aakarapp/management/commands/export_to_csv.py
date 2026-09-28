import csv
from django.core.management.base import BaseCommand
from aakarapp.models import fnb_model, pitch_submission  # Replace  aakarapp' with your actual app name

class Command(BaseCommand):
    help = 'Export data to CSV for fnb_model and pitch_submission'

    def handle(self, *args, **kwargs):
        # Export fnb_model data
        with open('fnb_model_backup.csv', 'w', newline='') as fnb_csvfile:
            fnb_writer = csv.writer(fnb_csvfile)
            fnb_writer.writerow(['Email', 'Startup Name', 'Web Link', 'Private?', 'Details', 'Contact', 'City', 'Theme', 'Unique', 'Stage', 'Validation', 'Patent', 'Incubated', 'Incubator Name', 'Looking For'])  # Header row
            
            
            for obj in fnb_model.objects.all():
                fnb_writer.writerow([
                    obj.email1,
                    obj.startup_name,
                    obj.web_link,
                    obj.pvt_yn,
                    obj.details,
                    obj.contact,
                    obj.city,
                    obj.theme,
                    obj.unique,
                    obj.stage,
                    obj.validation,
                    obj.patent,
                    obj.incubated,
                    obj.incubator_name,
                    obj.looking_for
                ])
        
        self.stdout.write(self.style.SUCCESS('fnb_model data exported to fnb_model_backup.csv'))

        # Export pitch_submission data
        with open('pitch_submission_backup.csv', 'w', newline='') as pitch_csvfile:
            pitch_writer = csv.writer(pitch_csvfile)
            pitch_writer.writerow(['Pitch Email', 'Pitch Link', 'Pitch Video'])  # Header row
            
            for obj in pitch_submission.objects.all():
                pitch_writer.writerow([
                    obj.pitch_email,
                    obj.pitch_link,
                    obj.pitch_video
                ])
        
        self.stdout.write(self.style.SUCCESS('pitch_submission data exported to pitch_submission_backup.csv'))
