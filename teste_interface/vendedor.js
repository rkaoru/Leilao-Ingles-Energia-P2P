document.addEventListener('DOMContentLoaded', async function () {
    await initWeb3();
    await initContract();

    const connectGanacheBtn = document.getElementById('connectGanacheBtn');
    connectGanacheBtn.addEventListener('click', async function () {
        const ganacheAddress = document.getElementById('ganacheAddress').value;
        if (ganacheAddress.trim() !== '') {
            web3.eth.defaultAccount = ganacheAddress;
            alert('Conectado à conta do Ganache com sucesso');
        } else {
            alert('Por favor, insira o endereço da conta do Ganache');
        }
    });

    const logoutBtn = document.getElementById('logoutBtn');
    logoutBtn.addEventListener('click', function () {
        window.location.href = 'index.html';
    });

    const ofertaForm = document.getElementById('ofertaForm');
    ofertaForm.addEventListener('submit', async function (event) {
        event.preventDefault();
        const quantidade = document.getElementById('quantidade').value;
        const preco = document.getElementById('preco').value;
        await cadastrarOferta(quantidade, preco);
    });
});
