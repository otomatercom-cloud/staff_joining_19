/* Staff Joining Portal v2 */
(function () {
    'use strict';

    function onPhotoChange(e) {
        var file = e.target.files[0];
        if (!file) return;

        var fname = document.getElementById('photo-fname');
        if (fname) fname.textContent = file.name;

        var reader = new FileReader();
        reader.onload = function (evt) {
            /* Re-query every time — never use closed-over variable */
            var area = document.getElementById('photo-area');
            if (!area) return;

            var prev = area.querySelector('.sj-photo-prev');
            if (!prev) {
                prev = document.createElement('img');
                prev.className = 'sj-photo-prev';
                prev.style.cssText = [
                    'width:90px', 'height:90px', 'border-radius:50%',
                    'object-fit:cover', 'margin:10px auto 6px', 'display:block',
                    'border:3px solid #4f46e5',
                    'box-shadow:0 2px 10px rgba(79,70,229,.3)'
                ].join(';');
                var icon = area.querySelector('i');
                if (icon) icon.style.display = 'none';
                var p = area.querySelector('p');
                if (p) area.insertBefore(prev, p);
                else area.appendChild(prev);
            }
            prev.src = evt.target.result;
        };
        reader.readAsDataURL(file);
    }

    function onFileChange(e) {
        var input = e.target;
        var span  = document.querySelector('span.sj-fname[data-for="' + input.id + '"]');
        if (!span) return;
        if (input.files[0]) {
            span.textContent      = input.files[0].name;
            span.style.color      = '#16a34a';
            span.style.fontWeight = '600';
        } else {
            span.textContent      = 'No file chosen';
            span.style.color      = '';
            span.style.fontWeight = '';
        }
    }

    function onDocRowChange(e) {
        var input = e.target;
        var file  = input.files[0];
        if (!file) return;

        var row = document.getElementById('row-' + input.id);
        var sub = document.getElementById('sub-' + input.id);
        var btn = input.previousElementSibling;

        if (row) {
            row.classList.remove('row-done', 'row-req');
            row.classList.add('row-picked');
            var icon = row.querySelector('.sj-doc-icon i');
            if (icon) icon.className = 'fa fa-check';
        }
        if (sub) sub.textContent = '→ ' + file.name;
        if (btn) {
            btn.className = 'sj-btn-upload sj-btn-chosen';
            btn.innerHTML = '<i class="fa fa-check"></i> Selected';
        }
    }

    function init() {
        /* Photo */
        var photoEl = document.getElementById('photo');
        var areaEl  = document.getElementById('photo-area');
        if (photoEl) photoEl.addEventListener('change', onPhotoChange);
        if (areaEl && photoEl) {
            areaEl.style.cursor = 'pointer';
            areaEl.addEventListener('click', function (e) {
                if (e.target !== photoEl) photoEl.click();
            });
        }

        /* Generic file inputs with sj-fname span */
        document.querySelectorAll('input[type="file"].sj-file-hidden').forEach(function (inp) {
            if (inp.id === 'photo') return;
            if (inp.closest('.sj-doc-row')) return; /* handled separately */
            inp.addEventListener('change', onFileChange);
        });

        /* Doc-row inputs (update portal) */
        document.querySelectorAll('.sj-doc-row input[type="file"]').forEach(function (inp) {
            inp.addEventListener('change', onDocRowChange);
        });

        /* Aadhaar formatting */
        var aad = document.getElementById('aadhaar_number');
        if (aad) {
            aad.addEventListener('input', function () {
                var v = this.value.replace(/\D/g, '').substring(0, 12);
                this.value = v.replace(/(\d{4})(?=\d)/g, '$1 ').trim();
            });
        }

        /* IFSC uppercase */
        var ifsc = document.getElementById('bank_ifsc');
        if (ifsc) {
            ifsc.addEventListener('input', function () {
                this.value = this.value.toUpperCase();
            });
        }

        /* Update lookup: digits only */
        var phoneUpd = document.querySelector('.sj-phone-field');
        if (phoneUpd) {
            phoneUpd.addEventListener('input', function () {
                this.value = this.value.replace(/\D/g, '').substring(0, 10);
            });
        }

        /* New application submit validation */
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
                var ad = document.getElementById('aadhaar_number');
                if (ad && ad.value.replace(/\s/g, '').length !== 12) {
                    e.preventDefault();
                    alert('Aadhaar number must be exactly 12 digits.');
                    ad.focus();
                }
            });
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

}());
