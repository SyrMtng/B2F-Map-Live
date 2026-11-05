# B2F Live Monitor

Monitoring pemain online dan server publik untuk:
- Mount Blossom Peak — `89188079951257`
- Sekolah Malam Club — `117969282373364`
- Our Flower Garden — `132699740251419`

## Setup GitHub

1. Buat repository GitHub bernama `B2F-Map-Live`.
2. Upload seluruh isi folder proyek ini, termasuk folder `.github/workflows`.
3. Buka **Settings → Secrets and variables → Actions → New repository secret**.
4. Buat secret bernama `DISCORD_WEBHOOK_URL`.
5. Isi Value dengan URL Discord Webhook kamu, lalu simpan.
6. Buka **Settings → Actions → General → Workflow permissions**.
7. Pastikan workflow memiliki izin tulis repository (workflow ini memakai `permissions: contents: write`).
8. Buka tab **Actions**, pilih **BRF Roblox Live Monitor**, lalu klik **Run workflow** untuk tes pertama.
9. Setelah tes berhasil, workflow akan berjalan terjadwal setiap 5 menit.

## Catatan

- Webhook hanya disimpan di GitHub Secrets; jangan menaruh URL webhook di file kode.
- Bot mengedit pesan Discord yang sama setelah ID pesan pertama tersimpan.
- Jumlah pemain online diambil dari statistik experience Roblox (lebih baik daripada hanya menjumlahkan pemain dari halaman server yang terlihat).
- Jumlah server adalah server publik yang berhasil terpantau melalui endpoint daftar server Roblox; server privat/VIP tidak termasuk.
- API daftar server memakai pagination dan dapat membatasi hasil yang dikembalikan. Script memindai maksimal 20 halaman per map; angka server adalah jumlah yang terpantau, bukan jaminan seluruh server global.
- Jadwal GitHub Actions dapat terlambat beberapa menit; ini bukan sistem real-time 60 detik.
- GitHub Actions scheduled workflows pada repository publik berjalan di default branch. Simpan file workflow di branch default.
