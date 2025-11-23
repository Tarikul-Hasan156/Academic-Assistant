from django import forms
from .models import Student, Faculty, ClassRoutine
from django.contrib.auth.models import User


class StudentRegisterForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    class Meta:

        
        model = Student
        fields = ['student_name', 'student_id', 'department', 'intake', 'section', 'blood_group']

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("password1") != cleaned_data.get("password2"):
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        student = super().save(commit=False)
        user = User.objects.create_user(
            username=self.cleaned_data['student_id'],
            password=self.cleaned_data['password1']
        )
        student.user = user
        if commit:
            student.save()
        return student


class FacultyRegisterForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Faculty
        fields = ['name', 'email', 'department', 'position', 'faculty_code']

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("password1") != cleaned_data.get("password2"):
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        faculty = super().save(commit=False)
        user = User.objects.create_user(
            username=self.cleaned_data['email'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password1']
        )
        faculty.user = user
        if commit:
            faculty.save()
        return faculty
