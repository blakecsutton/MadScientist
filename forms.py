from django import forms
from widgets import FacetedColumnCheckboxSelectMultiple
from models import Idea, Tag


class IdeaForm(forms.ModelForm):
    
    # Set up my custom widget of columns of checkboxes grouped by facet.
    # It's important to sort the queryset by facet, otherwise the widget 
    # grouping will be incorrect.
    tag = forms.ModelMultipleChoiceField(required=False, 
                                         queryset=Tag.objects.order_by('facet', 'name'),
                                         widget=FacetedColumnCheckboxSelectMultiple )
    class Meta:
        model = Idea