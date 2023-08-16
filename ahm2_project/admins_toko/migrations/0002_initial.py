# Generated by Django 4.2.1 on 2023-06-25 07:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('admins_toko', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='pesanan',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='pembelian',
            name='id_produk',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='admins_toko.produkahm'),
        ),
        migrations.AddField(
            model_name='pembayaran',
            name='id_pembelian',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='admins_toko.pembelian'),
        ),
        migrations.AddField(
            model_name='laporan',
            name='id_pembelian',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='admins_toko.pembelian'),
        ),
        migrations.AddField(
            model_name='laporan',
            name='id_produk',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='admins_toko.produkahm'),
        ),
    ]