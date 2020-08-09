from django.db import models

class TestSheet(models.Model):
    name = models.CharField(max_length=30)
    address = models.CharField(max_length=50)
    city = models.CharField(max_length=60)
    state_province = models.CharField(max_length=30)
    country = models.CharField(max_length=50)
    website = models.URLField()

    class Meta:
      db_table = 'test_sheets'


class LaboratoryReport(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    apply_num = models.CharField(max_length=20, blank=True, null=True)
    test_order_num = models.CharField(max_length=10, blank=True, null=True)
    patient_name = models.CharField(max_length=10, blank=True, null=True)
    patient_gender = models.CharField(max_length=5, blank=True, null=True)
    patient_age = models.CharField(max_length=5, blank=True, null=True)

    medical_record_num = models.CharField(max_length=20, blank=True, null=True)
    department = models.CharField(max_length=50, blank=True, null=True)
    bed_no = models.CharField(db_column='bed_No', max_length=5, blank=True, null=True)  # Field name made lowercase.

    sample_type = models.CharField(max_length=20, blank=True, null=True)
    apply_time = models.DateTimeField(blank=True, null=True)
    collect_time = models.DateTimeField(blank=True, null=True)

    clinical_diagnosis = models.CharField(max_length=255, blank=True, null=True)
    patient_feature = models.CharField(max_length=255, blank=True, null=True)
    send_doctor = models.CharField(max_length=50, blank=True, null=True)

    ward = models.CharField(max_length=50, blank=True, null=True)
    inspect_doctor = models.CharField(max_length=50, blank=True, null=True)
    review_doctor = models.CharField(max_length=50, blank=True, null=True)

    inspect_time = models.DateTimeField(blank=True, null=True)
    report_time = models.DateTimeField(blank=True, null=True)
    publish_time = models.DateTimeField(blank=True, null=True)

    culture_result = models.CharField(blank=True, max_length=255, null=True)
    culture_time = models.DateTimeField(blank=True, null=True)

    is_lock = models.CharField(max_length=10, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'laboratory_reports'

class LaboratoryLog(models.Model):
    laboratory_reports_id = models.IntegerField()
    laboratory_items_id = models.IntegerField()
    result_value = models.CharField(max_length=20)
    towards = models.CharField(max_length=20)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'laboratory_logs'

class LaboratoryItem(models.Model):
    laboratory_type = models.CharField(max_length=50)
    laboratory_item_label = models.CharField(max_length=100)
    refer_value = models.CharField(max_length=50, blank=True, null=True)
    item_unit = models.CharField(max_length=50)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'laboratory_items'

class LabInfoETZ(models.Model):
    lab_info_E = models.CharField(max_length=50)
    lab_info_Z = models.CharField(max_length=100)

    class Meta:
        db_table = 'lab_info_ETZs'


