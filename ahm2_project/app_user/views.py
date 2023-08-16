from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib.auth import logout,authenticate, login as auth_login, get_user_model
from django.contrib import messages
from django.contrib.auth.hashers import make_password,check_password
from django import forms 
from admins_toko.models import Produkahm, Promosi,Pesanan
from .models import KeranjangItem,Keranjang
from django.db import models
from django.http import HttpResponse,HttpResponseNotAllowed
from .models import Keranjang, KeranjangItem, Produkahm
from decimal import Decimal
from django.shortcuts import render, redirect
from .models import Keranjang, KeranjangItem, Pesanan
from django.shortcuts import redirect

User = get_user_model()

# Create your views here.
def menu_index(request):
    return render(request,'index.html')

@login_required(login_url=settings.LOGIN_USER)
def beranda(request):
    product = Produkahm.objects.all()
    return render(request,'afterlogin/beranda.html', {'product':product})

def menu_produk(request):
    product = Produkahm.objects.all()
    return render(request,'shop.html', {'product':product})
#detailproduk

def detail_produk(request, id_produk):
    if request.method == 'POST':
        pilihan = request.POST.get('size')
        jumlah = request.POST.get('jumlah')

        produk = Produkahm.objects.get(id_produk=id_produk)

        keranjang, created = Keranjang.objects.get_or_create(user=request.user)

        # Cek apakah produk sudah ada di dalam keranjang
        item = keranjang.items.filter(produk=produk).first()
        if item:
            item.jumlah += int(jumlah)
            item.save()
        else:
            KeranjangItem.objects.create(keranjang=keranjang, produk=produk, pilihan=pilihan, jumlah=jumlah)

        return redirect('keranjang')

    else:
        product = Produkahm.objects.filter(id_produk=id_produk)
        related_products = Produkahm.objects.exclude(id_produk=id_produk).order_by('?')[:4]
        return render(request, 'detail_produk.html', {'product': product, 'related_products': related_products})

#detailprodukafter1

@login_required(login_url=settings.LOGIN_USER)
def menu_cart(request):
    if request.method == 'POST':
        id_pesanan = request.POST.get('id')
        produk = request.POST.get('id_produk')
        pilihan = request.POST.get('size')
        jumlah = int(request.POST.get('jumlah'))
        produk = Produkahm.objects.get(produk=produk)
        keranjang = Keranjang.objects.get_or_create(user=request.user)
        KeranjangItem.objects.create(keranjang=keranjang, produk=produk, pilihan=pilihan, jumlah=jumlah, id=id_pesanan)

        return redirect('keranjang')

    else:
        # Mendapatkan keranjang yang terkait dengan pengguna saat ini
        keranjang = Keranjang.objects.get(user=request.user)
        keranjang.update_total()  # Memperbarui total keranjang
        item =  keranjang.items.all()
        total = keranjang.total
    context = {
        'keranjang': keranjang,
        'item': item,
        'total': total,
    }
    return render(request, 'cart.html', context)


def hapus_keranjang(request, id):
    item = get_object_or_404(KeranjangItem, id=id)
    item.delete()
    messages.success(request, "Data Berhasil Dihapus")
    return redirect('keranjang')

def tambah_pesanan(request):
    if request.method == 'POST':
        produk = request.POST.get('id_produk')
        pilihan = request.POST.get('pilihan')
        jumlah = int(request.POST.get('jumlah'))

        # Mendapatkan produk dari database berdasarkan ID
        produk = Produkahm.objects.get(id=produk)

        # Mendapatkan atau membuat objek keranjang untuk pengguna saat ini
        keranjang, created = Keranjang.objects.get_or_create(user=request.user)

        # Cek apakah produk sudah ada di dalam keranjang
        item = KeranjangItem.objects.filter(keranjang=keranjang, produk=produk, pilihan=pilihan).first()
        if item:
            item.jumlah += jumlah
            item.save()
        else:
            KeranjangItem.objects.create(keranjang=keranjang, produk=produk, pilihan=pilihan, jumlah=jumlah)

        return redirect('keranjang')


def riwayat_pesanan(request):
    riwayat_pesanan = Keranjang.objects.filter(user=request.user)
    return render(request, 'riwayat.html', {'riwayat_pesanan': riwayat_pesanan})


def menu_kontak(request):
    promos = Promosi.objects.all()
    return render(request, 'contact.html', {'promos': promos})

@login_required(login_url=settings.LOGIN_USER)
def checkout(request):
    # Get the cart object for the current user
    keranjang = Keranjang.objects.get(user=request.user)
    items = keranjang.items.all()
    total = keranjang.total

    context = {
        'keranjang': keranjang,
        'items': items,
        'total': total,
    }
    return render(request, 'checkout.html', context)

def create_pesanan(request):
    if request.method == 'POST':
        # Get the cart object for the current user
        keranjang = Keranjang.objects.get(user=request.user)
        keranjang_items = KeranjangItem.objects.all()
        # Get cart items to be transferred to the order
        keranjang_items = KeranjangItem.objects.filter(keranjang=keranjang)

        if keranjang_items.exists():
            # Create a new order object
            pesanan = Pesanan.objects.create(
                user=request.user,
                konfirmasi_pembayaran='paid',
                # Add other attributes as needed
            )

            for keranjang_item in keranjang_items:
                # Add items from cart to the order
                subtotal = keranjang_item.produk.harga_per_dus * keranjang_item.jumlah
                pesanan_item = Pesanan.objects.create(
                    pesanan=pesanan,
                    produk=keranjang_item.produk,
                    jumlah=keranjang_item.jumlah,
                    pilihan=keranjang_item.pilihan,
                    subtotal=subtotal,
                )

                # Associate the pesanan item with the order
                pesanan.items.add(pesanan_item)

            # Delete cart items after transferring to the order
            keranjang_items.delete()

            # Perform any other necessary operations for the order

            return HttpResponse("Pesanan berhasil dibuat")
        else:
            # Handle case when the cart is empty
            return redirect('keranjang')
    else:
        return HttpResponseNotAllowed(['POST'])
   
def menu_login(request):
    return render(request,'loginn.html')

def regist(request):
    if request.method=='POST':
        username=request.POST.get('username')
        email=request.POST.get('email')
        password=request.POST.get('password')
        hashed_password = make_password(password)
        confirm_password=hashed_password
        user=User(username=username, email=email, password=hashed_password)
        user.save()
        
        messages.success(request, "Akun Kamu Berhasil Dibuat")
        return redirect('/loginn/')
    else:
        return render(request, "register.html")

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.role == User.ADMIN_ROLE:
                auth_login(request, user)
                messages.error(request, 'Anda Admin')
                return redirect('menu_admin')
            if user.role == User.USER_ROLE:
                auth_login(request, user)
                messages.success(request,'Silahkan login untuk melanjutkan')
                return redirect('/beranda/')  # Ganti 'user_dashboard' dengan nama URL untuk dashboard user
            else:
                messages.error(request, 'Anda tidak memiliki izin untuk mengakses halaman ini.')
        else:
            messages.error(request, 'Username/Password salah.')

    return render(request,'loginn.html')

def logoutuser(request):
    logout(request)
    return redirect('loginn')



