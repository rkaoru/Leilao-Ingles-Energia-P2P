const express = require('express');
const { Web3 } = require('web3');
const app = express();

// Middleware para fazer o parsing do corpo das requisições
app.use((req, res, next) => {
	res.header('Access-Control-Allow-Origin', '*');
	res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept');
	next();
  });

const web3 = new Web3(new Web3.providers.HttpProvider('http://localhost:7545'));

const contractAddress = '0x00fc93b551fc0590D9884cd9862BD7544744BB3a'; // Endereço do contrato deployado
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
				"name": "_precoInicialPorKwhEmReais",
				"type": "uint256"
			}
		],
		"name": "cadastrarOferta",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
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
				"name": "_precoOferecidoPorKwhEmReais",
				"type": "uint256"
			}
		],
		"name": "fazerProposta",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "_ofertaIndex",
				"type": "uint256"
			}
		],
		"name": "finalizarLeilao",
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
				"name": "vencedor",
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
				"name": "precoTotalEmReais",
				"type": "uint256"
			}
		],
		"name": "LeilaoFinalizado",
		"type": "event"
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
				"name": "precoAtualPorKwh",
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
				"name": "precoOferecidoPorKwhEmReais",
				"type": "uint256"
			}
		],
		"name": "NovaProposta",
		"type": "event"
	},
	{
		"inputs": [],
		"name": "removerTodasOfertas",
		"outputs": [],
		"stateMutability": "nonpayable",
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
		"name": "melhoresPropostas",
		"outputs": [
			{
				"internalType": "address",
				"name": "comprador",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "quantidade",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "precoOferecidoPorKwhEmReais",
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
				"name": "precoAtualPorKwhEmReais",
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
		"name": "visualizarOfertas",
		"outputs": [
			{
				"internalType": "address[]",
				"name": "produtores",
				"type": "address[]"
			},
			{
				"internalType": "uint256[]",
				"name": "quantidadesDisponiveis",
				"type": "uint256[]"
			},
			{
				"internalType": "uint256[]",
				"name": "precosAtuaisPorKwhEmReais",
				"type": "uint256[]"
			},
			{
				"internalType": "bool[]",
				"name": "ativas",
				"type": "bool[]"
			}
		],
		"stateMutability": "view",
		"type": "function"
	}
]; // Your contract ABI

const contractInstance = new web3.eth.Contract(contractABI, contractAddress);

app.post('/cadastrarOferta', async (req, res) => {
    try {
      const { quantidadeDisponivel, precoInicialPorKwhEmReais, from } = req.body;
      const accounts = await web3.eth.getAccounts();
      const gas = await contractInstance.methods.cadastrarOferta(quantidadeDisponivel, precoInicialPorKwhEmReais).estimateGas({ from });
      const result = await contractInstance.methods.cadastrarOferta(quantidadeDisponivel, precoInicialPorKwhEmReais).send({ from, gas });
      res.send(`Transação enviada: ${result.transactionHash}`);
    } catch (error) {
      res.status(500).send(`Erro ao cadastrar oferta: ${error.message}`);
    }
  });  

// Endpoint para fazer proposta de compra em uma oferta de leilão
app.post('/fazerProposta', async (req, res) => {
    try {
      const { ofertaIndex, quantidadeDesejada, precoOferecidoPorKwhEmReais, from } = req.body;
      const accounts = await web3.eth.getAccounts();
      const gas = await contractInstance.methods.fazerProposta(ofertaIndex, quantidadeDesejada, precoOferecidoPorKwhEmReais).estimateGas({ from });
      const result = await contractInstance.methods.fazerProposta(ofertaIndex, quantidadeDesejada, precoOferecidoPorKwhEmReais).send({ from, gas });
      res.send(`Transação enviada: ${result.transactionHash}`);
    } catch (error) {
      res.status(500).send(`Erro ao fazer proposta: ${error.message}`);
    }
  });
  
  // Endpoint para finalizar o leilão automaticamente para a melhor oferta
  app.post('/finalizarLeilao', async (req, res) => {
    try {
      const { ofertaIndex, from } = req.body;
      const accounts = await web3.eth.getAccounts();
      const gas = await contractInstance.methods.finalizarLeilao(ofertaIndex).estimateGas({ from });
      const result = await contractInstance.methods.finalizarLeilao(ofertaIndex).send({ from, gas });
      res.send(`Transação enviada: ${result.transactionHash}`);
    } catch (error) {
      res.status(500).send(`Erro ao finalizar leilão: ${error.message}`);
    }
  });

// Endpoint para remover todas as ofertas
app.post('/removerTodasOfertas', (req, res) => {
  contractInstance.methods.removerTodasOfertas().send({ from: req.body.from })
    .on('transactionHash', hash => {
      res.send(`Transação enviada: ${hash}`);
    })
    .on('error', error => {
      res.status(500).send(`Erro ao remover ofertas: ${error}`);
    });
});

// Endpoint para visualizar todas as ofertas cadastradas
app.get('/visualizarOfertas', async (req, res) => {
    try {
      const ofertas = await contractInstance.methods.visualizarOfertas().call();
      const response = ofertas.produtores.map((produtor, index) => ({
        produtor,
        quantidadeDisponivel: ofertas.quantidadesDisponiveis[index].toString(),
        precoAtualPorKwhEmReais: ofertas.precosAtuaisPorKwhEmReais[index].toString(),
        ativa: ofertas.ativas[index]
      }));
      res.json(response);
    } catch (error) {
      res.status(500).send(`Erro ao visualizar ofertas: ${error}`);
    }
});

app.listen(3000, () => {
  console.log('API listening on port 3000');
});