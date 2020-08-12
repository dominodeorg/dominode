
from django.contrib.auth import authenticate
from django.contrib.auth.models import Group
from dotenv import load_dotenv

import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "geonode.settings")

# load django app model
django.setup()

load_dotenv()

user = authenticate(username=os.getenv("GEONODE_USERNAME"), password=os.getenv("GEONODE_USER_PASSWORD"))


lsd_user = User.objects.create_user(username=os.getenv("GEONODE_LSD_USERNAME"), email="",  password=os.getenv("GEONODE_LSD_PASSWORD"))
lsd_user.is_staff = False
lsd_user.is_superuser = False
lsd_user.save()

ppd_user = User.objects.create_user(username=os.getenv("GEONODE_PPD_USERNAME"), email="",  password=os.getenv("GEONODE_PPD_PASSWORD"))
ppd_user.is_staff = False
ppd_user.is_superuser = False
ppd_user.save()

groupLSD = Group(name="LSD_GROUP")
groupLSD.save()

groupLSD.users.add(lsd_user)
groupLSD.save()

groupPPD = Group(name="PPD_GROUP")
groupPPD.save()
groupPPD.users.add(ppd_user)
groupPPD.save()


