# Generated by Django 3.0.1 on 2020-05-14 03:36

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Site',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('crest', models.IntegerField(verbose_name='CREST ID')),
                ('project_type', models.CharField(choices=[('Brownfield', 'Brownfield'), ('Greenfield', 'Greenfield')], default='Greenfield', max_length=10, verbose_name='Projet Type')),
                ('network_name', models.CharField(max_length=96, verbose_name='Network Name')),
                ('address', models.CharField(max_length=96, verbose_name='Site Address')),
                ('capacity', models.IntegerField(verbose_name='Site Capacity')),
                ('headcount', models.IntegerField(verbose_name='Site Headcount')),
                ('network_type', models.CharField(choices=[('Micro Branch', 'Micro Branch'), ('Mini Branch', 'Mini Branch'), ('Small Branch', 'Small Branch'), ('Medium Branch (1-2 Floors)', 'Medium Branch (1-2 Floors)'), ('Medium Branch (3-10 Floors)', 'Medium Branch (3-10 Floors)'), ('Large Branch', 'Large Branch'), ('Medium Campus', 'Medium Campus'), ('Large Campus', 'Large Campus')], default='Micro Branch', max_length=27, verbose_name='Network Type')),
                ('nearest_dc', models.CharField(choices=[('AM1', 'AM1'), ('AM2', 'AM2')], max_length=4, verbose_name='Nearest DC')),
                ('router', models.CharField(choices=[('ASR 1001-X', 'ASR 1001-X'), ('ASR 1001-HX', 'ASR 1001-HX'), ('ISR 4331', 'ISR 4331'), ('ISR 4351', 'ISR 4351'), ('ISR 4451', 'ISR 4451')], max_length=11, verbose_name='Router Layer')),
                ('core', models.CharField(choices=[('No Core Layer', 'No Core Layer'), ('Catalyst 3850', 'Catalyst 3850'), ('Catalyst 6840', 'Catalyst 6840'), ('Catalyst 6880', 'Catalyst 6880'), ('Catalyst 9500', 'Catalyst 9500')], max_length=13, verbose_name='Core Layer')),
                ('server', models.CharField(choices=[('No Server Layer', 'No Server Layer'), ('Catalyst 4500', 'Catalyst 4500'), ('Catalyst 9500', 'Catalyst 9500')], max_length=15, verbose_name='Server Layer')),
                ('signal_created_access', models.BooleanField(null=True, verbose_name='Access Created')),
                ('signal_created_wan', models.BooleanField(null=True, verbose_name='WAN Created')),
                ('signal_duplicate_vlan', models.BooleanField(null=True, verbose_name='Duplicate VLAN')),
                ('signal_exception_site', models.BooleanField(null=True, verbose_name='Site Non-standard')),
                ('signal_onboarded_site', models.BooleanField(null=True, verbose_name='Site Onboarded')),
                ('signal_overlapping_access', models.BooleanField(null=True, verbose_name='Access Port Block Overlapping')),
                ('signal_present_core', models.BooleanField(null=True, verbose_name='Core Present')),
                ('signal_present_server', models.BooleanField(null=True, verbose_name='Server Present')),
                ('signal_updated_access', models.BooleanField(null=True, verbose_name='Access Updated')),
                ('signal_updated_core', models.BooleanField(null=True, verbose_name='Core Updated')),
                ('signal_updated_server', models.BooleanField(null=True, verbose_name='Server Updated')),
                ('signal_updated_wan', models.BooleanField(null=True, verbose_name='WAN Updated')),
            ],
        ),
    ]
