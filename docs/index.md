# Postchi
Postchi is a Python package which provides better mailing infrastructures, helping you :

 - Use Django templates in your Emails
 -  send emails asynchronously using [easy-job](https://github.com/inb-co/easy-job) 

### Installation

 1. install postchi using pip 	`pip install postchi`
 2. specify postchi as your email backend

```
# settings.py
EMAIL_BACKEND = "postchi.backend.PostchiEmailBackend"
```

 3. (Optional) if you want to use postchi in async mode or specify logger, you should provide some more configurations:

```
# settings.py
POSTCHI = {
    "send_type": "async",
    "easy_job_worker_name": "postchi",
    "logger": "mail"
}
```


 - for the send_type you can choose sync or async, default is sync
 - easy_job_worker_name is the name of worker you already defined in your [easy_job configurations](http://easy-job.readthedocs.io/en/latest/#1-first-open-your-settings-file-and-add-the-following)
 - logger is the name of the python logger you want to use in postchi , if you don't specify logger , postchi will use root logger for logging.

### Usage
at this point postchi is ready and you should create your Mail classes by extending `postchi.mails.BaseMail` , for example if you have a Django app named myapp you can define a mails.py module in your app package and for each type of email create a Mail class.
for example if you have Welcome Mail message , you can define it like this :

```
# myapp/mails.py
from postchi.mails import BaseMail


class WelcomeEmail(BaseMail):
    template_name = "mails/welcome.html"
    subject = "Welcome to my web site ^_^ "
```

finally for sending mails ( for example in your views) :

```
# myapp/views.py
def register_view(request, *args, **kwargs):
	user = save_user_to_db(request.POST)
	from myapp.mails import WelcomeEmail
	WelcomeEmail(username=user.username).send()
```

the `__init__` parameters are actually context values which will be used to render mail templates.
there is one more thing you need to know , if there are some constant values which exists in all templates, you can use specify them in EMAIL_COMMON_CONTEXT inside your settings:
```
# settings.py
EMAIL_COMMON_CONTEXT = {
    "base_url": "http://mywebsitename.com/",
    "static_url": "http://mywebsitename.com/static/",
}
```
these two constant values (base_url and static_url) will be available in all mail templates .

