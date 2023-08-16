
from django.db import models
from django.contrib.humanize.templatetags import humanize
from decimal import Decimal
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import pre_save

   

DEFAULT_IMAGE = 'images/2023/06/09/torpedo.jpg'
class Produkahm(models.Model):
    id_produk= models.CharField(max_length=10,primary_key =True,default='1' )
    kategori = models.ForeignKey('Kategori', on_delete=models.CASCADE, null=True)
    nama_produk= models.CharField(max_length=100, null=True)
    stok_per_dus= models.IntegerField(default=0)
    gambar_produk= models.ImageField(upload_to='images/%Y/%m/%d/', null=True, blank=True ,default=DEFAULT_IMAGE)
    harga_per_dus= models.DecimalField(max_digits=10, decimal_places=3)

    def __str__(self):
        return f'{self.nama_produk}- Rp {humanize.intcomma(self.harga_per_dus)}'  
    
    @property
    def harga_idr(self):
        return f'Rp {humanize.intcomma(self.harga_per_dus)}'
    
    def update_stock(self, jumlah):
        self.stok_per_dus += jumlah
        self.save()
    

class Pembelian(models.Model):
    id_pembelian = models.CharField(max_length=10, primary_key=True, default='P001')
    id_produk = models.ForeignKey(Produkahm, on_delete=models.CASCADE, null=True)
    harga_pembelian = models.DecimalField(max_digits=10, decimal_places=3, null=True)
    jumlah = models.IntegerField()
    total_harga = models.DecimalField(max_digits=10, decimal_places=3)
    tanggal = models.DateField(auto_now_add=True)
    catatan = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.id_produk.nama_produk
    def __str__(self):
        return f'{self.id_pembelian} - {self.tanggal}'
    def __str__(self):
        return f'{self.id_pembelian} - {self.id_produk.nama_produk}'

    @property
    def total(self):
        return f'Rp {humanize.intcomma(self.total_harga)}'
    
    @property
    def harga(self):
        return f'Rp {humanize.intcomma(self.harga_pembelian)}'
    
    def save(self, *args, **kwargs):
        # Menghitung total_harga
        self.total_harga = Decimal(self.harga_pembelian) * self.jumlah

        id_produk = self.id_produk
        jumlah = self.jumlah
        if id_produk and jumlah:
            try:
                produk = Produkahm.objects.get(id_produk=id_produk)
                produk.stok_per_dus += jumlah
                produk.save()
            except ObjectDoesNotExist:
                # Handle ketika objek Produkahm tidak ditemukan
                # Misalnya, tampilkan pesan kesalahan atau lakukan tindakan lainnya
                pass
        
        super().save(*args, **kwargs)
  
# promosi

class Promosi(models.Model):
    id_promosi = models.AutoField(primary_key=True)
    nama_promosi = models.CharField(max_length=100)
    deskripsi = models.TextField()
    gambar_promosi= models.ImageField(upload_to='promosi/%Y/%m/%d/', null=True, blank=True)
    tanggal_mulai = models.DateField(auto_now_add=True ,editable=False)
    tanggal_berakhir = models.DateField()
    kode_promosi = models.CharField(max_length=50)

    def __str__(self):
        return self.nama_promosi
    


class Kategori(models.Model):
    id_kategori = models.CharField(max_length=10, primary_key=True ,default='K1')
    nama_kategori = models.CharField(max_length=100)

    def __str__(self):
        return self.nama_kategori

#RATING

class Ratings(models.Model):

    id_rating = models.CharField(max_length=10, primary_key=True)
    komentar = models.TextField()

    def __str__(self):
        return self.komentar


@receiver(pre_save, sender=Ratings)
def set_default_id_rating(sender, instance, **kwargs):
    if not instance.id_rating:
        last_rating = Ratings.objects.order_by('-id_rating').first()
        if last_rating:
            last_id = int(last_rating.id_rating[1:])
            new_id = last_id + 1
            instance.id_rating = f'R{new_id}'
        else:
            instance.id_rating = 'R1'

    


class Pembayaran(models.Model):
    CHOICES = (
        ('BRI', 'BRI'),
        ('BCA', 'BCA'),
        ('COD', 'COD'),
    )
    id_pembayaran = models.CharField(max_length=10, primary_key=True, default='PEM1')
    id_pembelian = models.ForeignKey('Pembelian', on_delete=models.CASCADE, null=True)
    tanggal_pembayaran = models.DateField(null=True, editable=True)
    metode_pembayaran = models.CharField(max_length=10, choices=CHOICES)
    bukti_transfer = models.ImageField(upload_to='bukti_transfer/%Y/%m/%d/', null=True, blank=True)
    status = models.CharField(max_length=100)
    total_harga = models.CharField(max_length=100)

    def save(self, *args, **kwargs):
        if self.id_produk:
            self.harga_idr = self.id_produk.total_harga
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Pembayaran - id_pembayaran: {self.id_pembayaran}"
    
    @property
    def total(self):
        return f'Rp {humanize.intcomma(self.total_harga)}'


from django.db import models
from django.conf import settings
from django.contrib.humanize.templatetags import humanize

class Pesanan(models.Model):
    KONFIRMASI_PEMBAYARAN_CHOICES = (
        ('paid', 'Paid'),
        ('unpaid', 'Unpaid'),
        ('failed', 'Failed'),
    )
    PILIHAN_CHOICES = (
        ('dus', 'Dus'),
        ('lusin', 'Lusin'),
    )
    id_pesanan = models.CharField(max_length=10, primary_key=True, default=None, blank=True)
    konfirmasi_pembayaran = models.CharField(max_length=10, choices=KONFIRMASI_PEMBAYARAN_CHOICES, default='unpaid')
    produk = models.ManyToManyField(Produkahm)
    jumlah = models.IntegerField(default=0)
    pilihan = models.CharField(max_length=50, choices=PILIHAN_CHOICES, default='dus')
    subtotal = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)

    def hitung_subtotal(self):
        subtotal = self.produk.harga_per_dus * self.jumlah
        self.subtotal = subtotal
        self.save()
        return subtotal

    def __str__(self):
        return f"Pemesanan {self.id_pesanan}"

    @property
    def total(self):
        return f'Rp {humanize.intcomma(self.subtotal)}'


@receiver(pre_save, sender=Pesanan)
def set_default_id_pesanan(sender, instance, **kwargs):
    if instance.id_pesanan is None:
        last_pesanan = Pesanan.objects.order_by('-id_pesanan').first()
        if last_pesanan:
            last_id = int(last_pesanan.id_pesanan[2:])
            new_id = last_id + 1
            instance.id_pesanan = f'PS{new_id:03}'
        else:
            instance.id_pesanan = 'PS001'



class Laporan(models.Model):
    id_laporan = models.AutoField(primary_key=True)
    id_pembelian = models.ForeignKey(Pembelian, on_delete=models.CASCADE)
    id_produk = models.ForeignKey(Produkahm, on_delete=models.CASCADE)
    catatan = models.TextField()

    def __str__(self):
        return f"Laporan {self.id_laporan}"

    











    



