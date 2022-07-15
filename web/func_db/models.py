from django.db import models


class Crate(models.Model):

    class Meta:
        verbose_name = 'crate'
        verbose_name_plural = 'crates'

    name = models.CharField('crate_name', max_length=15)
    version = models.CharField('crate_version', max_length=15)
    

class Function(models.Model):
    """Base function module
    """

    class Meta:
        verbose_name = 'function'
        verbose_name_plural = 'functions' 

    class FType(models.IntegerChoices):
        NORMAL = (0, 'normal')
        METHOD = (1, 'method')
        TRAIT = (2, 'trait')
        CLOSURE = (3, 'closure')

    class AnalyStat(models.IntegerChoices):
        NORMAL = (0, 'normal')
        ERR_FORMAT = (1, 'unknown format')
        # For Bin
        ERR_BIN = (2, 'bin file error')
        ERR_CRATE = (3, 'not wanted crate')

    crate = models.CharField('crate', max_length=15)
    name = models.CharField('name', max_length=63)
    full_name = models.CharField('full_name', max_length=255)
    ftype = models.SmallIntegerField('ftype', choices=FType.choices)
    astat = models.SmallIntegerField('astat', choices=AnalyStat.choices)

    # path for normal, impl_class for method and trait
    # not consider closure yet, possibly, same as the outer function
    path = models.CharField('path', max_length=63),
    impl_class = models.CharField('impl class', max_length=63),
    impl_trait = models.CharField('impl class', max_length=63),


class Mir(Function):

    class Meta:
        verbose_name = 'function mir'
        verbose_name_plural = 'functions mir' 

    version_tag = models.CharField('version', max_length=15)
    matched = models.BooleanField('matched', default=False)
    # inlined = models.BooleanField('inlined', default=False)

    
class Bin(Function):

    class Source:
        verbose_name = 'function bin'
        verbose_name_plural = 'functions bin' 

    bin_crate = models.CharField('bin crate', max_length=15)
    matched_mir = models.ForeignKey(
        Mir,
        on_delete=models.SET_NULL,
        null=True,
    )

