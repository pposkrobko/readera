from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit



from book_stats.models import Author, Book



class AddNewBookForm(forms.Form):
    author = forms.CharField(
        max_length=100,
        required=True
    )

    title = forms.CharField(
        max_length=100,
        required=True
    )

    max_pages= forms.IntegerField(
        required=True
    )


    def __init__(self, *args, **kwargs):
        super(AddNewBookForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = [
            'author',
            'title',
            'max_pages']

        self.helper = FormHelper()
        self.helper.form_id = 'id-exampleForm'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.form_method = 'post'
        self.helper.form_action = '/stats/get_new_book_form/'

        self.helper.add_input(Submit('submit', 'Wyślij'))

    def save(self, commit=True):
        b = Book()
        b.title = self.cleaned_data['title']
        b.max_pages = self.cleaned_data['max_pages']
        author_name = self.cleaned_data['author']
        new_author = Author.objects.filter(name=author_name)
        if not new_author.exists():
            author = Author()
            author.name = self.cleaned_data['author']
            author.save()
            b.author = author
        else:
            b.author = new_author[0]

        if commit:
            b.save()
        return b




