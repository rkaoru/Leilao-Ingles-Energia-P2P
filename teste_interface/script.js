document.addEventListener('DOMContentLoaded', function () {
    const sellerBtn = document.getElementById('sellerBtn');
    const buyerBtn = document.getElementById('buyerBtn');

    sellerBtn.addEventListener('click', function () {
        window.location.href = 'vendedor.html';
    });

    buyerBtn.addEventListener('click', function () {
        window.location.href = 'comprador.html';
    });
});
