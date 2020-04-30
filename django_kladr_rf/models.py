from django.db import models


class KLADRBase(models.Model):
    name = models.CharField(max_length=256, verbose_name='Название')
    code_kladr = models.CharField(max_length=32, verbose_name='Код КЛАДР')
    post_index = models.CharField(max_length=32, verbose_name='Почтовый индекс')
    code_okato = models.CharField(max_length=32, verbose_name='Код ОКАТО')
    tax_code = models.CharField(max_length=32, verbose_name='Налоговый код')
    latitude = models.FloatField(verbose_name='Широта', null=True)
    longitude = models.FloatField(verbose_name='Долгота', null=True)

    class Meta:
        abstract = True


class KLADRRegion(KLADRBase):
    region_code = models.CharField(max_length=32, verbose_name='Код региона')

    class Meta:
        verbose_name = 'регион кладр'
        verbose_name_plural = 'регионы кладр'

    def __str__(self):
        return '{} - {}'.format(self.region_code, self.name)


class KLADRCity(KLADRBase):
    region = models.ForeignKey(
        KLADRRegion, on_delete=models.CASCADE, verbose_name='Регион'
    )

    class Meta:
        verbose_name = 'город кладр'
        verbose_name_plural = 'город кладр'

    def __str__(self):
        return '{}'.format(self.name)


class KLADRDistrict(KLADRBase):
    region = models.ForeignKey(
        KLADRRegion, on_delete=models.CASCADE, verbose_name='Регион'
    )

    class Meta:
        verbose_name = 'район кладр'
        verbose_name_plural = 'район кладр'

    def __str__(self):
        return '{}'.format(self.name)
