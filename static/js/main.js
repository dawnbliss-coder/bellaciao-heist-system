/**
 * Operation Bella Ciao - shared frontend helpers
 *
 * Currently powers the AJAX-based inline resource quantity updates on the
 * Resources page: submitting the "Update Quantity" form patches the
 * resource via /api/resources/<id>/update and updates the card in place,
 * instead of doing a full page reload.
 *
 * If JavaScript is unavailable, the forms fall back to a normal POST to
 * /resources/update/<id> (see resources.html), so the feature degrades
 * gracefully.
 */

document.addEventListener('DOMContentLoaded', function () {
    initResourceInlineUpdates();
});

function initResourceInlineUpdates() {
    const forms = document.querySelectorAll('.js-resource-update-form');

    forms.forEach(function (form) {
        form.addEventListener('submit', function (event) {
            event.preventDefault();
            handleResourceUpdate(form);
        });
    });
}

function handleResourceUpdate(form) {
    const card = form.closest('.js-resource-card');
    if (!card) return;

    const resourceId = card.dataset.resourceId;
    const quantityInput = form.querySelector('input[name="quantity"]');
    const submitButton = form.querySelector('button[type="submit"]');
    const statusEl = form.querySelector('.js-update-status');

    const quantity = quantityInput.value;

    submitButton.disabled = true;
    if (statusEl) {
        statusEl.textContent = 'Updating...';
        statusEl.className = 'text-muted js-update-status';
    }

    const body = new URLSearchParams();
    body.set('quantity', quantity);

    fetch(`/api/resources/${resourceId}/update`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: body.toString()
    })
        .then(function (response) {
            return response.json().then(function (data) {
                return { ok: response.ok, data: data };
            });
        })
        .then(function (result) {
            if (!result.ok || !result.data.success) {
                const message = (result.data && result.data.error) || 'Update failed';
                throw new Error(message);
            }
            applyResourceUpdate(card, result.data.resource);
            if (statusEl) {
                statusEl.textContent = 'Updated!';
                statusEl.className = 'text-success js-update-status';
                setTimeout(function () {
                    statusEl.textContent = '';
                }, 2000);
            }
        })
        .catch(function (err) {
            if (statusEl) {
                statusEl.textContent = err.message || 'Update failed';
                statusEl.className = 'text-danger js-update-status';
            }
        })
        .finally(function () {
            submitButton.disabled = false;
        });
}

function applyResourceUpdate(card, resource) {
    card.dataset.status = resource.status;

    // Border color
    card.classList.remove('border-danger', 'border-warning', 'border-success');
    card.classList.add(statusToBorderClass(resource.status));

    // Quantity text
    const quantityValue = card.querySelector('.js-quantity-value');
    if (quantityValue) quantityValue.textContent = resource.CurrentQuantity;

    // Status badge
    const badge = card.querySelector('.js-status-badge');
    if (badge) {
        badge.classList.remove('status-critical', 'status-warning', 'status-good');
        badge.classList.add('status-' + resource.status);
        badge.textContent = resource.status.toUpperCase();
    }

    // Progress bar
    const progressBar = card.querySelector('.js-progress-bar');
    if (progressBar) {
        const criticalThreshold = parseFloat(card.dataset.criticalThreshold) || 0;
        const scaleMax = criticalThreshold > 0
            ? criticalThreshold * 3
            : Math.max(resource.CurrentQuantity, 1);
        const pct = Math.min(Math.round((resource.CurrentQuantity / scaleMax) * 100), 100);

        progressBar.style.width = pct + '%';
        progressBar.textContent = resource.CurrentQuantity;
        progressBar.classList.remove('bg-danger', 'bg-warning', 'bg-success');
        progressBar.classList.add(statusToBarClass(resource.status));
    }

    // Critical alert banner
    const alertEl = card.querySelector('.js-critical-alert');
    if (alertEl) {
        alertEl.style.display = resource.status === 'critical' ? '' : 'none';
    }
}

function statusToBorderClass(status) {
    if (status === 'critical') return 'border-danger';
    if (status === 'warning') return 'border-warning';
    return 'border-success';
}

function statusToBarClass(status) {
    if (status === 'critical') return 'bg-danger';
    if (status === 'warning') return 'bg-warning';
    return 'bg-success';
}
