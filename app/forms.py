from django import forms
from .models import User, Profile, Tag


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control form-control-lg",
                                                             "placeholder": "Enter your nick"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control form-control-lg",
                                                                 "placeholder": "Enter your password"}))


class SignUpForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control form-control-lg",
                                                             "placeholder": "george"}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "form-control form-control-lg",
                                                            "placeholder": "george@vk.com"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control form-control-lg",
                                                                 "placeholder": "Enter your password"}))
    password_repeat = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control form-control-lg",
                                                                        "placeholder": "Enter your password again"}))
    avatar = forms.ImageField(required=False, widget=forms.FileInput(attrs={"class": "form-control form-control-lg"}))

    def save(self):
        user = User.objects.create(username=self.cleaned_data.get("username"),
                                   email=self.cleaned_data.get("email"))
        user.set_password(self.cleaned_data.get("password"))
        Profile.objects.create(user=user, login=user.username)
        user.save()
        return user

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_repeat = cleaned_data.get("password_repeat")

        if password != password_repeat:
            self.add_error(None, "Passwords do not match!")
        if len(User.objects.filter(username=self.cleaned_data.get("username"))) != 0:
            self.add_error(None, "User exists!")
        if len(User.objects.filter(email=self.cleaned_data.get("email"))) != 0:
            self.add_error(None, "Email exists!")


class SettingsForm(forms.Form):
    username = forms.CharField(required=False, widget=forms.TextInput(attrs={"class": "form-control form-control-lg",
                                                                             "placeholder": "george"}))
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={"class": "form-control form-control-lg",
                                                                            "placeholder": "george@vk.com"}))
    avatar = forms.ImageField(required=False, widget=forms.FileInput(attrs={"class": "form-control form-control-lg"}))


class AskForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control form-control-lg",
                                                          "placeholder": "How to delete french language from Linux?"}))
    text = forms.CharField(widget=forms.Textarea(attrs={"class": "form-control form-control-lg",
                                                        "placeholder": "I'm crying, I can't find how(", "rows": 8}))
    tags = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control form-control-lg",
                                                         "placeholder": "Separate by space"}))

    def save(self):
        tags = []
        for tag in self.cleaned_data["tags"].split(' '):
            tags.append(tag.strip())
        tag_list = []
        for tag in tags:
            this_tag = Tag.objects.filter(name=tag).first()
            if this_tag is None:
                this_tag = Tag.objects.create(name=tag, rating=0)
            else:
                this_tag.rating += 1
                this_tag.save()
            tag_list.append(this_tag)
        return tag_list


class AnswerForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea(attrs={"class": "form-control form-control-lg",
                                                        "placeholder": "Enter your answer...", "rows": 8}), label="")
