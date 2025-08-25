from django import forms
from .models import DesignAsset, AssetImage, DesignReview


class DesignAssetForm(forms.ModelForm):
    class Meta:
        model = DesignAsset
        fields = ['category', 'name', 'price', 'discount', 'cover_image', 'description', 'is_active']


class AssetImageForm(forms.ModelForm):
    class Meta:
        model = AssetImage
        fields = ['image', 'alt_text', 'ordering']


AssetImageFormSet = forms.inlineformset_factory(
    DesignAsset, AssetImage, form=AssetImageForm, extra=1, can_delete=True
)


class DesignReviewForm(forms.ModelForm):
    rating = forms.IntegerField(min_value=1, max_value=5, widget=forms.NumberInput(attrs={'class':'form-control','min':1,'max':5}))
    comment = forms.CharField(required=False, widget=forms.Textarea(attrs={'class':'form-control','rows':3,'placeholder':'Share your experience...'}))

    class Meta:
        model = DesignReview
        fields = ['rating', 'comment']

    def clean_comment(self):
        comment = self.cleaned_data.get('comment','').strip()
        if len(comment) > 2000:
            raise forms.ValidationError('Comment too long (max 2000 characters).')
        return comment
