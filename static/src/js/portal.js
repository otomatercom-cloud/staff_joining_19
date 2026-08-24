/* Staff Joining Portal — portal.js */
(function () {
    'use strict';

    function init() {

        // ── Photo upload preview ───────────────────────────────────────
        var photoInput = document.getElementById('photo');
        var photoArea  = document.getElementById('photo-area');
        var photoFname = document.getElementById('photo-fname');

        if (photoInput && photoArea) {
            photoArea.style.cursor = 'pointer';
            photoArea.addEventListener('click', function (e) {
                if (e.target !== photoInput) photoInput.click();
            });

            photoInput.addEventListener('change', function () {
                var file = this.files[0];
                if (!file) return;
                if (photoFname) photoFname.textContent = file.name;

                var reader = new FileReader();
                reader.onload = function (e) {
                    if (!photoArea) return;                          // guard
                    var prev = photoArea.querySelector('.sj-photo-prev');
                    if (!prev) {
                        prev = document.createElement('img');
                        prev.className = 'sj-photo-prev';
                        prev.style.cssText = 'width:90px;height:90px;border-radius:50%;object-fit:cover;margin:10px auto 6px;display:block;border:3px solid #4f46e5;box-shadow:0 2px 10px rgba(79,70,229,.3);';
                        var icon = photoArea.querySelector('i');
                        if (icon) icon.style.display = 'none';
                        var firstP = photoArea.querySelector('p');
                        if (firstP) photoArea.insertBefore(prev, firstP);
                        else photoArea.appendChild(prev);
                    }
                    prev.src = e.target.result;
                };
                reader.readAsDataURL(file);
            });
        }

        // ── Generic file input → show filename (span[data-for]) ───────
        document.querySelectorAll('input[type="file"].sj-file-hidden').forEach(function (input) {
            if (input.id === 'photo') return;
            input.addEventListener('change', function () {
                var span = document.querySelector('span.sj-fname[data-for="' + this.id + '"]');
                if (!span) return;
                if (this.files[0]) {
                    span.textContent     = this.files[0].name;
                    span.style.color     = '#16a34a';
                    span.style.fontWeight = '600';
                } else {
                    span.textContent     = 'No file chosen';
                    span.style.color     = '';
                    span.style.fontWeight = '';
                }
            });
        });

        // ── Update portal: doc-row file pick ──────────────────────────
        document.querySelectorAll('.sj-doc-row input[type="file"]').forEach(function (input) {
            input.addEventListener('change', function () {
                var file = this.files[0];
                if (!file) return;
                var row = document.getElementById('row-' + this.id);
                var sub = document.getElementById('sub-' + this.id);
                var btn = this.previousElementSibling;
                if (row) {
                    row.classList.remove('row-done', 'row-req');
                    row.classList.add('row-picked');
                    var icon = row.querySelector('.sj-doc-icon i');
                    if (icon) icon.className = 'fa fa-check';
                }
                if (sub) sub.textContent = '→ ' + file.name;
                if (btn) {
                    btn.className   = 'sj-btn-upload sj-btn-chosen';
                    btn.innerHTML   = '<i class="fa fa-check"></i> Selected';
                }
            });
        });

        // ── Aadhaar: XXXX XXXX XXXX ───────────────────────────────────
        var aad = document.getElementById('aadhaar_number');
        if (aad) {
            aad.addEventListener('input', function () {
                var v = this.value.replace(/\D/g, '').substring(0, 12);
                this.value = v.replace(/(\d{4})(?=\d)/g, '$1 ').trim();
            });
        }

        // ── IFSC uppercase ────────────────────────────────────────────
        var ifsc = document.getElementById('bank_ifsc');
        if (ifsc) {
            ifsc.addEventListener('input', function () {
                this.value = this.value.toUpperCase();
            });
        }

        // ── Update lookup: digits only ────────────────────────────────
        var phoneUpd = document.querySelector('.sj-phone-field');
        if (phoneUpd) {
            phoneUpd.addEventListener('input', function () {
                this.value = this.value.replace(/\D/g, '').substring(0, 10);
            });
        }

        // ── New application: submit validation ────────────────────────
        var joinForm = document.querySelector('form[action="/join/submit"]');
        if (joinForm) {
            joinForm.addEventListener('submit', function (e) {
                var ph = document.getElementById('phone');
                if (ph && !/^[6-9]\d{9}$/.test(ph.value.trim())) {
                    e.preventDefault();
                    alert('Please enter a valid 10-digit Indian mobile number (starting with 6–9).');
                    ph.focus();
                    return;
                }
                var ad2 = document.getElementById('aadhaar_number');
                if (ad2 && ad2.value.replace(/\s/g, '').length !== 12) {
                    e.preventDefault();
                    alert('Aadhaar number must be exactly 12 digits.');
                    ad2.focus();
                }
            });
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
