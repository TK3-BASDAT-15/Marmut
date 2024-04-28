# Marmut

## Prerequisites
Sebelum menjalankan program untuk pertama kalinya, buka Terminal / Command Prompt dan ikuti langkah-langkah berikut:

1. Jalankan command `python -m venv env`
2. Jalankan command `source env/bin/activate` untuk pengguna macOS dan Linux atau `.\env\Scripts\activate.bat` untuk pengguna Windows

    > Catatan: Lakukan Step 2 setiap kamu membuka Terminal/Command Prompt baru sebelum menjalankan program.

3. Jalankan command `pip install -r requirements.txt`
4. Buatlah file baru bernama `.env`, kemudian isi file tersebut dengan format data berikut:

    ```env
    PG_NAME="<nama_db>"
    PG_USER="<username_db>"
    PG_PASSWORD="<password_db>"
    PG_HOST="<hostname_db>"
    PG_PORT="<port_db>"
    ```

5. Selesai
