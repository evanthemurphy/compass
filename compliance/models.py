# compliance/models.py
from django.db import models
from django.core.exceptions import ValidationError
import re

class IDP(models.Model):
    project_name = models.CharField(max_length=200)
    budget_code = models.CharField(max_length=50, unique=True)
    approved_amount = models.DecimalField(max_digits=15, decimal_places=2)
    fiscal_year = models.CharField(max_length=9)
    date_approved = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.project_name} ({self.budget_code})"

    class Meta:
        verbose_name = "IDP Project"


class Requisition(models.Model):
    requisition_number = models.CharField(max_length=50, unique=True)
    idp = models.ForeignKey(IDP, on_delete=models.PROTECT)
    description = models.TextField()
    estimated_cost = models.DecimalField(max_digits=15, decimal_places=2)
    date_requested = models.DateField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[('DRAFT', 'Draft'), ('APPROVED', 'Approved')],
        default='DRAFT'
    ) 

def clean(self):
    # Check IDP link
    if not self.idp_id:
        raise ValidationError({'idp': "Requisition MUST be linked to an approved IDP project."})
    
    # Check budget
    if self.estimated_cost > self.idp.approved_amount:
        raise ValidationError("Estimated cost exceeds IDP budget!")

class Specification(models.Model):
    spec_number = models.CharField(max_length=50, unique=True)
    requisition = models.OneToOneField(Requisition, on_delete=models.PROTECT)
    content = models.TextField()
    date_drafted = models.DateField(auto_now_add=True)
    rigged_keywords_found = models.JSONField(default=list, blank=True)

    def clean(self):
        if self.requisition.status != 'APPROVED':
            raise ValidationError("Specification can only be created for APPROVED requisitions.")
        
        keywords = self.scan_for_rigged_keywords()
        if keywords:
            self.rigged_keywords_found = keywords
            raise ValidationError(f"Rigged specification detected: {', '.join(keywords)}")

    def scan_for_rigged_keywords(self):
        patterns = [
            r'\bMust be from [A-Z][a-z]+\b',
            r'\bOnly [A-Z][a-z]+ supplier\b',
            r'\bBrand: [A-Z]+\b',
            r'\bModel: [A-Z0-9-]+\b',
            r'\bMinimum 10 years experience\b',
            r'\bLocal content 100%\b',
        ]
        found = []
        content_lower = self.content.lower()
        for pattern in patterns:
            if re.search(pattern.lower(), content_lower):
                found.append(pattern)
        return found

    def __str__(self):
        return f"SPEC {self.spec_number}"