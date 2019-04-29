# from mptt.models import MPTTModel, TreeForeignKey
from .base import *
from .resources import *
from django_extensions.db.fields.json import JSONField
# from polymorphic.models import PolymorphicModel
# from polymorphic.managers import PolymorphicManager
from polymorphic_tree.models import PolymorphicMPTTModel, PolymorphicTreeForeignKey
from simple_history.models import HistoricalRecords
# class AbBaseService(PolymorphicModel)


class BaseService(PolymorphicMPTTModel, BaseConcurrentModel):
    parent = PolymorphicTreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    resources = models.ManyToManyField(BaseResource, blank=True, through='ServiceResourcesRelation')
    name = models.CharField(max_length=64)
    tree_path_cache = models.CharField(max_length=255, blank=True,  null=True)
    info = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        self.tree_path_cache = self.path(new=False if self.pk else True)
        super(BaseService, self).save(*args, **kwargs)

    class Meta(PolymorphicMPTTModel.Meta):
        verbose_name = "Tree node"
        verbose_name_plural = "Tree nodes"

    def path(self, new=False):
        p = [""]
        if new:
            s = self
            while s.parent:
                p.append(s.name)
                s=s.parent
            p.append(self.name)
            return '/'.join(p)

        for x in self.get_ancestors(ascending=False, include_self=False):
            p.append(x.name)
        p.append(self.name)
        return '/'.join(p)


class NormalService(BaseService):
    git = models.CharField(max_length=255)
    objects = PolymorphicManager()
    history = HistoricalRecords()

    class Meta(PolymorphicMPTTModel.Meta):
        verbose_name = "normal-service"
        verbose_name_plural = "normal-services"


class Version(BaseConcurrentModel):
    service = models.ForeignKey(BaseService, on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=255)


class ServiceResourcesRelation(models.Model):
    history = HistoricalRecords()
    service = models.ForeignKey(BaseService, on_delete=models.CASCADE)
    resource = models.ForeignKey(BaseResource, on_delete=models.CASCADE)
    version = models.ForeignKey(Version, null=True, on_delete=models.PROTECT)
    _ctime = models.DateTimeField(auto_now_add=True)
    _mtime = models.DateTimeField(auto_now=True)


class DbService(BaseService):
    use_types = (
        ('shard', 'shard'),
        ('master-slave', 'master-slave'),
        ('pxc', 'pxc'),
    )
    history = HistoricalRecords()
    objects = PolymorphicManager()
    use_type = models.CharField(choices=use_types, null=False, max_length=255)

    class Meta(PolymorphicMPTTModel.Meta):
        verbose_name = "db-service"
        verbose_name_plural = "db-services"