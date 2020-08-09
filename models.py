# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class LaboratoryReports(models.Model):
    report_title = models.CharField(max_length=255, blank=True, null=True)
    group_name = models.CharField(max_length=255, blank=True, null=True)
    sample_num = models.CharField(max_length=10, blank=True, null=True)
    bar_code = models.CharField(max_length=20, blank=True, null=True)
    patient_category = models.CharField(max_length=10, blank=True, null=True)
    patient_name = models.CharField(max_length=10, blank=True, null=True)
    patient_gender = models.CharField(max_length=5, blank=True, null=True)
    patient_age = models.CharField(max_length=5, blank=True, null=True)
    sample_type = models.CharField(max_length=20, blank=True, null=True)
    department = models.CharField(max_length=50, blank=True, null=True)
    ward = models.CharField(max_length=50, blank=True, null=True)
    bed_no = models.CharField(db_column='bed_No', max_length=5, blank=True, null=True)  # Field name made lowercase.
    medical_record_num = models.CharField(max_length=20, blank=True, null=True)
    medical_card_num = models.CharField(max_length=20, blank=True, null=True)
    apply_time = models.DateTimeField(blank=True, null=True)
    collect_time = models.DateTimeField(blank=True, null=True)
    send_inspect_doctor = models.CharField(max_length=50, blank=True, null=True)
    clinical_diagnosis = models.CharField(max_length=255, blank=True, null=True)
    remark = models.CharField(max_length=255, blank=True, null=True)
    received_time = models.DateTimeField(blank=True, null=True)
    report_time = models.DateTimeField(blank=True, null=True)
    received_doctor = models.CharField(max_length=50, blank=True, null=True)
    inspect_doctor = models.CharField(max_length=50, blank=True, null=True)
    review_doctor = models.CharField(max_length=50, blank=True, null=True)
    report_doctor = models.CharField(max_length=50, blank=True, null=True)
    is_lock = models.CharField(max_length=10, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'laboratory_reports'


class LaboratoryLogs(models.Model):
    laboratory_reports_id = models.IntegerField()
    laboratory_items_id = models.IntegerField()
    result_value = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    towards = models.CharField(max_length=20)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'laboratory_logs'


class LaboratoryItems(models.Model):
    laboratory_type = models.CharField(max_length=50)
    column_num = models.IntegerField(blank=True, null=True)
    laboratory_item_label = models.CharField(max_length=100)
    laboratory_item_abb = models.CharField(max_length=50)
    refer_value_start = models.DecimalField(max_digits=10, decimal_places=2)
    refer_value_end = models.DecimalField(max_digits=10, decimal_places=2)
    item_unit = models.CharField(max_length=50)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'laboratory_items'
