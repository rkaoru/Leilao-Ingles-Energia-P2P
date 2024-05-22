// Substitua "CONTRACT_ADDRESS" pelo endereço do seu contrato
const CONTRACT_ADDRESS = 'CONTRACT_ADDRESS';
// Substitua "CONTRACT_ABI" pelo ABI do seu contrato
const CONTRACT_ABI = CONTRACT_ABI;

let web3;
let mercadoEnergiaContract;

async function initWeb3() {
    // Configuração para conexão com o Ganache
    const ganacheUrl = 'http://localhost:7545'; // Porta padrão do Ganache
    const provider = new Web3.providers.HttpProvider(ganacheUrl);
    web3 = new Web3(provider);

    // Verifica se o Metamask ou outro provedor está instalado
    if (window.ethereum) {
        try {
            // Solicita ao usuário a permissão para se conectar
            await window.ethereum.enable();
            web3 = new Web3(window.ethereum);
        } catch (error) {
            console.error('User denied account access');
        }
    } else if (window.web3) {
        // Caso o Metamask esteja instalado, utiliza o provedor atual
        web3 = new Web3(web3.currentProvider);
    } else {
        console.error('No Web3 detected. Please install MetaMask or use a Web3-enabled browser');
    }
}

async function initContract() {
    // Inicializa o contrato inteligente
    mercadoEnergiaContract = new web3.eth.Contract(CONTRACT_ABI, CONTRACT_ADDRESS);
}

async function cadastrarOferta(quantidade, preco) {
    // Função para cadastrar uma nova oferta no contrato
    try {
        const accounts = await web3.eth.getAccounts();
        await mercadoEnergiaContract.methods.cadastrarOferta(quantidade, preco).send({ from: accounts[0] });
        alert('Oferta cadastrada com sucesso');
    } catch (error) {
        console.error('Erro ao cadastrar oferta:', error);
    }
}

async function carregarOfertas() {
    // Função para carregar as ofertas disponíveis do contrato
    try {
        const ofertas = await mercadoEnergiaContract.methods.visualizarOfertas().call();
        const ofertasList = document.getElementById('ofertasList');
        ofertasList.innerHTML = '';
        ofertas.forEach((oferta, index) => {
            if (oferta.ativa) {
                const option = document.createElement('option');
                option.value = index;
                option.textContent = `Produtor: ${oferta.produtor} | Quantidade: ${oferta.quantidadeDisponivel} kWh | Preço: ${oferta.precoMinimoPorKwhEmReais} Reais`;
                document.getElementById('ofertaSelect').appendChild(option);
            }
        });
    } catch (error) {
        console.error('Erro ao carregar ofertas:', error);
    }
}

async function fazerProposta(ofertaIndex, quantidade, preco) {
    // Função para fazer uma proposta de compra
    try {
        const accounts = await web3.eth.getAccounts();
        await mercadoEnergiaContract.methods.fazerProposta(ofertaIndex, quantidade, preco).send({ from: accounts[0] });
        alert('Proposta realizada com sucesso');
    } catch (error) {
        console.error('Erro ao fazer proposta:', error);
    }
}

document.addEventListener('DOMContentLoaded', async function () {
    // Inicializa o provedor Web3 e o contrato inteligente
    await initWeb3();
    await initContract();
});
