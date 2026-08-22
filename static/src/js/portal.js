/* Staff Joining Portal — portal.js */
document.addEventListener('DOMContentLoaded', function () {

    // Photo preview on new application form
    var photoInput = document.getElementById('photo');
    var photoArea  = document.getElementById('photo-area');
    var photoFname = document.getElementById('photo-fname');
    if (photoInput && photoArea) {
        photoInput.addEventListener('change', function () {
            var file = this.files[0];
            if (!file) return;
            if (photoFname) photoFname.textContent = file.name;
            var reader = new FileReader();
            reader.onload = function (e) {
                var prev = photoArea.querySelector('.sj-photo-prev');
                if (!prev) {
                    prev = document.createElement('img');
                    prev.className = 'sj-photo-prev';
                    prev.style.cssText = 'width:80px;height:80px;border-radius:50%;object-fit:cover;margin:10px auto;display:block;border:3px solid #4f46e5;';
                    photoArea.insertBefore(prev, photoArea.querySelector('.sj-hint, #photo-fname'));
                }
                prev.src = e.target.result;
            };
            reader.readAsDataURL(file);
        });
    }

    // Generic fname span handler for new application form
    document.querySelectorAll('span.sj-fname[data-for]').forEach(function (span) {
        var input = document.getElementById(span.dataset.for);
        if (!input) return;
        input.addEventListener('change', function () {
            if (this.files[0]) {
                span.textContent = this.files[0].name;
                span.classList.add('chosen');
            } else {
                span.textContent = 'No file chosen';
                span.classList.remove('chosen');
            }
        });
    });

    // Update portal: doc row interaction
    document.querySelectorAll('.sj-doc-row input.sj-file-hidden').forEach(function (input) {
        input.addEventListener('change', function () {
            var file = this.files[0];
            var row  = document.getElementById('row-' + this.id);
            var sub  = document.getElementById('sub-' + this.id);
            var btn  = this.previousElementSibling;
            if (!file || !row) return;
            row.classList.remove('row-done', 'row-req');
            row.classList.add('row-picked');
            var icon = row.querySelector('.sj-doc-icon i');
            if (icon) { icon.className = 'fa fa-check'; }
            if (sub)  { sub.textContent = '→ ' + file.name; }
            if (btn)  { btn.className = 'sj-btn-upload sj-btn-chosen'; btn.innerHTML = '<i class="fa fa-check"></i> Selected'; }
        });
    });

    // Aadhaar XXXX XXXX XXXX
    var aadInput = document.getElementById('aadhaar_number');
    if (aadInput) {
        aadInput.addEventListener('input', function () {
            var v = this.value.replace(/\D/g,'').substring(0,12);
            this.value = v.replace(/(\d{4})(?=\d)/g,'$1 ').trim();
        });
    }

    // IFSC uppercase
    var ifsc = document.getElementById('bank_ifsc');
    if (ifsc) { ifsc.addEventListener('input', function(){ this.value = this.value.toUpperCase(); }); }

    // Phone - digits only on update lookup
    var phoneUpdate = document.querySelector('.sj-phone-field');
    if (phoneUpdate) {
        phoneUpdate.addEventListener('input', function(){
            this.value = this.value.replace(/\D/g,'').substring(0,10);
        });
    }

    // Validate new application form before submit
    var joinForm = document.querySelector('form[action="/join/submit"]');
    if (joinForm) {
        joinForm.addEventListener('submit', function (e) {
            var ph = document.getElementById('phone');
            if (ph && !/^[6-9]\d{9}$/.test(ph.value.trim())) {
                e.preventDefault();
                alert('Please enter a valid 10-digit Indian mobile number starting with 6-9.');
                ph.focus(); return;
            }
            var ad = document.getElementById('aadhaar_number');
            if (ad && ad.value.replace(/\s/g,'').length !== 12) {
                e.preventDefault();
                alert('Aadhaar number must be exactly 12 digits.');
                ad.focus();
            }
        });
    }
});
