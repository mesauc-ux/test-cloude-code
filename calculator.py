#!/usr/bin/env python3
"""
Basit Python Hesap Makinesi
Toplama, çıkarma, çarpma ve bölme işlemlerini yapar.
"""

def toplama(x, y):
    """İki sayıyı toplar"""
    return x + y

def cikarma(x, y):
    """İki sayıyı çıkarır"""
    return x - y

def carpma(x, y):
    """İki sayıyı çarpar"""
    return x * y

def bolme(x, y):
    """İki sayıyı böler"""
    if y == 0:
        return "Hata: Sıfıra bölme yapılamaz!"
    return x / y

def hesap_makinesi():
    """Ana hesap makinesi fonksiyonu"""
    print("=" * 40)
    print("    Basit Python Hesap Makinesi")
    print("=" * 40)

    while True:
        print("\nİşlem seçin:")
        print("1. Toplama (+)")
        print("2. Çıkarma (-)")
        print("3. Çarpma (*)")
        print("4. Bölme (/)")
        print("5. Çıkış")

        secim = input("\nSeçiminiz (1-5): ")

        if secim == '5':
            print("Hesap makinesinden çıkılıyor. Hoşça kalın!")
            break

        if secim not in ['1', '2', '3', '4']:
            print("Geçersiz seçim! Lütfen 1-5 arasında bir sayı girin.")
            continue

        try:
            sayi1 = float(input("Birinci sayıyı girin: "))
            sayi2 = float(input("İkinci sayıyı girin: "))

            if secim == '1':
                sonuc = toplama(sayi1, sayi2)
                print(f"\n{sayi1} + {sayi2} = {sonuc}")
            elif secim == '2':
                sonuc = cikarma(sayi1, sayi2)
                print(f"\n{sayi1} - {sayi2} = {sonuc}")
            elif secim == '3':
                sonuc = carpma(sayi1, sayi2)
                print(f"\n{sayi1} × {sayi2} = {sonuc}")
            elif secim == '4':
                sonuc = bolme(sayi1, sayi2)
                print(f"\n{sayi1} ÷ {sayi2} = {sonuc}")

        except ValueError:
            print("Hata: Lütfen geçerli bir sayı girin!")
        except Exception as e:
            print(f"Bir hata oluştu: {e}")

if __name__ == "__main__":
    hesap_makinesi()
