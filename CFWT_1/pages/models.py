 # articles/models.py
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse


class ClimateFinanceData(models.Model):
    project_name = models.CharField(max_length=255)
    funding_source = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.project_name

    def get_absolute_url(self):
        return reverse('climatefinance_detail', args=[str(self.id)])
    
    def get_update_url(self):
        return reverse("data_update", args=[self.pk])

    def get_delete_url(self):
        return reverse("data_delete", args=[self.pk])
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['project_name', 'funding_source', 'amount'],
                name='unique_project_funding'
            )
        ]

    def __str__(self):
        return f"{self.project_name} - {self.funding_source} - {self.amount}"
