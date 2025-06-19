from django.db import models
from django.urls import reverse
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

def custom_url_validator(value):
    """Allow URLs with or without http/https"""
    validator = URLValidator()
    try:
        # If the user enters without scheme (e.g., "example.com"), add "https://"
        if not value.startswith(('http://', 'https://')):
            value = "https://" + value  
        validator(value)  # Validate the formatted URL
    except ValidationError:
        raise ValidationError("Enter a valid website URL.")
    
class Sector(models.Model):
    """Categorization of climate finance projects"""
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("sector_detail", args=[str(self.id)])


class FundingSource(models.Model):
    """Stores entities providing climate finance"""
    SOURCE_TYPES = [
        ('government', 'Government'),
        ('ngo', 'NGO'),
        ('private', 'Private Sector'),
        ('international', 'International Agency'),
    ]

    name = models.CharField(max_length=255, unique=True)
    type = models.CharField(max_length=50, choices=SOURCE_TYPES)
    country = models.CharField(max_length=100)
    contact_email = models.EmailField(null=True, blank=True)
    website = models.CharField(max_length=255, blank=True, null=True, validators=[custom_url_validator])  # Apply custom validator
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("funding_source_detail", args=[str(self.id)])
    
    def save(self, *args, **kwargs):
        if self.website and not self.website.startswith(('http://', 'https://')):
            self.website = "https://" + self.website  # Auto-correct missing scheme
        super().save(*args, **kwargs)


class Recipient(models.Model):
    """Tracks organizations or projects receiving climate finance"""
    RECIPIENT_TYPES = [
        ('government', 'Government Agency'),
        ('ngo', 'NGO'),
        ('private', 'Private Sector'),
        ('community', 'Community Organization'),
    ]

    name = models.CharField(max_length=255)
    type = models.CharField(max_length=50, choices=RECIPIENT_TYPES)
    location = models.CharField(max_length=255)
    contact_email = models.EmailField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("recipient_detail", args=[str(self.id)])


class ClimateProject(models.Model):
    """Climate-related projects that receive funding"""
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    recipient = models.ForeignKey(Recipient, on_delete=models.CASCADE, related_name="projects")
    sector = models.ForeignKey(Sector, on_delete=models.SET_NULL, null=True, related_name="projects")
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("project_detail", args=[str(self.id)])


class ClimateFinanceData(models.Model):
    """Tracks climate finance transactions for projects"""
    FUNDING_TYPES = [
        ('grant', 'Grant'),
        ('loan', 'Loan'),
        ('equity', 'Equity'),
        ('technical_assistance', 'Technical Assistance'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('disbursed', 'Disbursed'),
        ('completed', 'Completed'),
    ]

    project = models.ForeignKey(ClimateProject, on_delete=models.CASCADE, related_name="funding_records")
    funding_source = models.ForeignKey(FundingSource, on_delete=models.CASCADE, related_name="funding_records")
    funding_type = models.CharField(max_length=20, choices=FUNDING_TYPES)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=10, choices=[('KES', 'KES'), ('USD', 'USD'), ('EUR', 'EUR')], default='KES')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['project', 'funding_source', 'funding_type'], name='unique_funding_entry')
        ]

    def __str__(self):
        return f"{self.project.name} - {self.funding_source.name} - {self.total_amount} {self.currency}"

    def get_absolute_url(self):
        return reverse("climatefinance_detail", args=[str(self.id)])

    def get_update_url(self):
        return reverse("data_update", args=[self.pk])

    def get_delete_url(self):
        return reverse("data_delete", args=[self.pk])


class Disbursement(models.Model):
    """Tracks individual fund releases to a project"""
    finance_data = models.ForeignKey(ClimateFinanceData, on_delete=models.CASCADE, related_name="disbursements")
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=10, choices=[('KES', 'KES'), ('USD', 'USD'), ('EUR', 'EUR')], default='KES')
    disbursement_date = models.DateField()
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.finance_data.project.name} - {self.amount} {self.currency} on {self.disbursement_date}"

    def get_absolute_url(self):
        return reverse("disbursement_detail", args=[str(self.id)])


class AuditLog(models.Model):
    """Logs modifications to climate finance records for transparency"""
    ACTION_TYPES = [
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('deleted', 'Deleted'),
    ]

    finance_data = models.ForeignKey(ClimateFinanceData, on_delete=models.CASCADE, related_name="audit_logs")
    action = models.CharField(max_length=10, choices=ACTION_TYPES)
    performed_by = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.action} - {self.finance_data.project.name} by {self.performed_by}"

    def get_absolute_url(self):
        return reverse("auditlog_detail", args=[str(self.id)])
