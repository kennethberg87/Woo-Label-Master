document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Test Printer Connection
    const testPrinterBtn = document.getElementById('test-printer-btn');
    if (testPrinterBtn) {
        testPrinterBtn.addEventListener('click', function() {
            const printerIp = document.getElementById('printer_ip').value;
            const printerPort = document.getElementById('printer_port').value || 9100;
            
            if (!printerIp) {
                showAlert('Please enter a printer IP address', 'danger');
                return;
            }
            
            showAlert('Testing printer connection...', 'info');
            
            fetch('/api/test-printer', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    ip: printerIp,
                    port: printerPort
                }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showAlert(data.message, 'success');
                } else {
                    showAlert(data.message, 'danger');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showAlert('Error testing printer connection', 'danger');
            });
        });
    }
    
    // Test WooCommerce Connection
    const testWooBtn = document.getElementById('test-woocommerce-btn');
    if (testWooBtn) {
        testWooBtn.addEventListener('click', function() {
            const wooUrl = document.getElementById('woocommerce_url').value;
            const wooKey = document.getElementById('woocommerce_consumer_key').value;
            const wooSecret = document.getElementById('woocommerce_consumer_secret').value;
            
            if (!wooUrl || !wooKey || !wooSecret) {
                showAlert('Please enter all WooCommerce API credentials', 'danger');
                return;
            }
            
            showAlert('Testing WooCommerce connection...', 'info');
            
            fetch('/api/test-woocommerce', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    url: wooUrl,
                    consumer_key: wooKey,
                    consumer_secret: wooSecret
                }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showAlert(data.message, 'success');
                } else {
                    showAlert(data.message, 'danger');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showAlert('Error testing WooCommerce connection', 'danger');
            });
        });
    }
    
    // Handle label size selection
    const labelWidthSelect = document.getElementById('label_width');
    const labelHeightGroup = document.getElementById('label-height-group');
    const labelHeightInput = document.getElementById('label_height');
    
    if (labelWidthSelect && labelHeightGroup && labelHeightInput) {
        labelWidthSelect.addEventListener('change', function() {
            if (labelWidthSelect.value === 'custom') {
                labelHeightGroup.classList.remove('d-none');
            } else {
                labelHeightGroup.classList.add('d-none');
                labelHeightInput.value = 'AUTO';
            }
        });
        
        // Trigger once on page load
        if (labelWidthSelect.value === 'custom') {
            labelHeightGroup.classList.remove('d-none');
        } else {
            labelHeightGroup.classList.add('d-none');
        }
    }
});

function showAlert(message, type) {
    const alertPlaceholder = document.getElementById('alert-placeholder');
    if (!alertPlaceholder) return;
    
    const wrapper = document.createElement('div');
    wrapper.innerHTML = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    
    alertPlaceholder.appendChild(wrapper);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        const alert = bootstrap.Alert.getOrCreateInstance(wrapper.querySelector('.alert'));
        alert.close();
    }, 5000);
}
