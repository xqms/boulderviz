

from django import forms
from models import Climber

from django.utils.translation import ugettext_lazy as _

class ClimberSelectForm(forms.Form):
	climber = forms.ModelChoiceField(
		queryset=Climber.objects.order_by('name'),
		empty_label=_('Climber'),
		required=False,
	)
