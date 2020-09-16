# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright (C) 2017 OSGeo
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################

from django.conf.urls import url, include
from django.views.generic import TemplateView

from geonode.urls import urlpatterns
from geonode.monitoring import register_url_event

from geonode_dominode.views import GroupDetailView, CLIListView, cli_executor, \
    cli_sync_geoserver

homepage = register_url_event()(TemplateView.as_view(template_name='site_index.html'))

urlpatterns = [
    url(r'^/?$',
        homepage,
        name='home'),
    url(r'^groups/group/(?P<slug>[-\w]+)/$',
        GroupDetailView.as_view(), name='group_detail'),
    url(r'^cli/group/(?P<slug>[-\w]+)/$',
        CLIListView.as_view(), name='cli_view'),
    url(r'^cli/execute/(?P<cli_slug>[-\w]+)/',
        cli_executor, name='cli_execute'),
    url(r'^cli/sync_geoserver/',
        cli_sync_geoserver, name='cli_sync_geoserver')
 ] + urlpatterns
