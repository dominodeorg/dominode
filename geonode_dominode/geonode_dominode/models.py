from django.db import models
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _
import asyncio
from geonode.groups.models import GroupProfile


class CLI(models.Model):
    """Assign groups that can execute CLI command.
    """

    name = models.CharField(_('Command name'), max_length=255)
    slug = models.CharField(_('slug'), max_length=255, blank=True)
    groups = models.ManyToManyField(GroupProfile)
    command = models.TextField(_('Command'))

    class Meta:
        permissions = [
            ('execute_cli', 'Can Execute CLI'),
        ]

    def save(self, **kwargs):
        self.slug = slugify(self.name)
        super(CLI, self).save(**kwargs)

    def __str__(self):
        return "{}".format(self.name)

    def render_command(self, context=None):
        """Render command from template into an executable shell text."""
        # generate context
        # TODO: add instance specific context
        context = dict() if not context else context
        return str(self.command).format(**context)

    async def execute_command(self, context=None):
        """Execute the command asynchrounously"""
        command_string = self.render_command(context)
        proc = await asyncio.create_subprocess_shell(
            command_string,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)
        return proc
