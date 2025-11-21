document.addEventListener('DOMContentLoaded', function () {
  const resetBtn = document.getElementById('reset-filters');
  if (resetBtn) {
    resetBtn.addEventListener('click', function () {
      const form = document.getElementById('filters-form');
      // Clear non-hidden inputs
      [...form.elements].forEach(el => {
        if (el.type !== 'hidden') {
          if (el.tagName === 'SELECT') el.selectedIndex = 0;
          else el.value = '';
        }
      });
      // Submit to reload full list
      form.submit();
    });
  }
});