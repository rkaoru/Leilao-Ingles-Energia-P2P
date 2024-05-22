const Web3 = window.Web3;
const web3 = new Web3(Web3.givenProvider || "http://localhost:7545");
const contractABI = [
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "_quantidadeDisponivel",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "_precoMinimoPorKwhEmReais",
				"type": "uint256"
			}
		],
		"name": "cadastrarOferta",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": false,
				"internalType": "address",
				"name": "comprador",
				"type": "address"
			},
			{
				"indexed": false,
				"internalType": "uint256",
				"name": "quantidade",
				"type": "uint256"
			},
			{
				"indexed": false,
				"internalType": "uint256",
				"name": "preco",
				"type": "uint256"
			}
		],
		"name": "CompraEfetuada",
		"type": "event"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "_ofertaIndex",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "_quantidadeDesejada",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "_precoOferecidoEmReais",
				"type": "uint256"
			}
		],
		"name": "fazerProposta",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "finalizarCompra",
		"outputs": [],
		"stateMutability": "payable",
		"type": "function"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": false,
				"internalType": "address",
				"name": "produtor",
				"type": "address"
			},
			{
				"indexed": false,
				"internalType": "uint256",
				"name": "quantidade",
				"type": "uint256"
			},
			{
				"indexed": false,
				"internalType": "uint256",
				"name": "precoMinimoPorKwh",
				"type": "uint256"
			}
		],
		"name": "NovaOferta",
		"type": "event"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": false,
				"internalType": "address",
				"name": "comprador",
				"type": "address"
			},
			{
				"indexed": false,
				"internalType": "uint256",
				"name": "ofertaIndex",
				"type": "uint256"
			},
			{
				"indexed": false,
				"internalType": "uint256",
				"name": "quantidade",
				"type": "uint256"
			},
			{
				"indexed": false,
				"internalType": "uint256",
				"name": "preco",
				"type": "uint256"
			}
		],
		"name": "NovaProposta",
		"type": "event"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": false,
				"internalType": "uint256",
				"name": "ofertaIndex",
				"type": "uint256"
			}
		],
		"name": "OfertaEsgotada",
		"type": "event"
	},
	{
		"inputs": [],
		"name": "comprador",
		"outputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "etherToReais",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "numeroOfertas",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"name": "ofertas",
		"outputs": [
			{
				"internalType": "address",
				"name": "produtor",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "quantidadeDisponivel",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "precoMinimoPorKwhEmReais",
				"type": "uint256"
			},
			{
				"internalType": "bool",
				"name": "ativa",
				"type": "bool"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "precoTotal",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "quantidadeComprada",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "visualizarOfertas",
		"outputs": [
			{
				"components": [
					{
						"internalType": "address",
						"name": "produtor",
						"type": "address"
					},
					{
						"internalType": "uint256",
						"name": "quantidadeDisponivel",
						"type": "uint256"
					},
					{
						"internalType": "uint256",
						"name": "precoMinimoPorKwhEmReais",
						"type": "uint256"
					},
					{
						"internalType": "bool",
						"name": "ativa",
						"type": "bool"
					}
				],
				"internalType": "struct MercadoEnergia.Oferta[]",
				"name": "",
				"type": "tuple[]"
			}
		],
		"stateMutability": "view",
		"type": "function"
	}
]; // Copie e cole o ABI do contrato MercadoEnergia aqui
const contractAddress = "0x0415C7A80D22BDEaA7d0Aa9F5E451d67DfAb755a"; // Insira o endereço do contrato MercadoEnergia aqui

const mercadoEnergiaContract = new web3.eth.Contract(contractABI, contractAddress);

async function getOffers() {
    try {
        // Chame a função do contrato para visualizar as ofertas
        const offers = await mercadoEnergiaContract.methods.visualizarOfertas().call();
        const offersElement = document.getElementById('offers');
        offersElement.innerHTML = '<h2>Ofertas cadastradas:</h2>';
        offers.forEach((offer, index) => {
            const offerDiv = document.createElement('div');
            offerDiv.innerHTML = `
                <h3>Oferta ${index + 1}:</h3>
                <p>Produtor: ${offer.produtor}</p>
                <p>Quantidade Disponível: ${offer.quantidadeDisponivel}</p>
                <p>Preço Mínimo por kWh em Reais: ${offer.precoMinimoPorKwhEmReais}</p>
                <p>Ativa: ${offer.ativa}</p>
            `;
            offersElement.appendChild(offerDiv);
        });
    } catch (error) {
        console.error('Erro ao recuperar as ofertas:', error);
    }
}

async function fazerProposta(ofertaIndex, quantidadeDesejada, precoOferecidoEmReais) {
	try {
		// Chamar a função do contrato para fazer uma proposta
		await mercadoEnergiaContract.methods.fazerProposta(ofertaIndex, quantidadeDesejada, precoOferecidoEmReais).send({ from: window.ethereum.selectedAddress });
		console.log('Proposta enviada com sucesso!');
	} catch (error) {
		console.error('Erro ao enviar proposta:', error);
	}
}

async function finalizarCompra() {
	try {
		// Chamar a função do contrato para finalizar uma compra
		await mercadoEnergiaContract.methods.finalizarCompra().send({ from: window.ethereum.selectedAddress, value: web3.utils.toWei('1', 'ether') }); // Substitua '1' pelo valor em Ether que deseja pagar
		console.log('Compra efetuada com sucesso!');
	} catch (error) {
		console.error('Erro ao finalizar compra:', error);
	}
}
  
  // Chame a função para recuperar as ofertas
  getOffers();