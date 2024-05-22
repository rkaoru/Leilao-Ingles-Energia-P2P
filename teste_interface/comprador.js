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

    const propostaForm = document.getElementById('propostaForm');
    propostaForm.addEventListener('submit', async function (event) {
        event.preventDefault();
        const ofertaIndex = document.getElementById('ofertaSelect').value;
        const quantidade = document.getElementById('quantidade').value;
        const preco = document.getElementById('preco').value;
        await fazerProposta(ofertaIndex, quantidade, preco);
    });

    setInterval(carregarOfertas, 3000); // Atualiza a lista de ofertas a cada 3 segundos
});
