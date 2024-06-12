// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract MercadoEnergiaLeilao {
    struct Oferta {
        address payable produtor;
        uint quantidadeDisponivel;
        uint precoMinimoPorKwhEmReais;
        bool ativa;
    }

    struct Lance {
        address payable comprador;
        uint valor;
    }

    Oferta public oferta;
    address payable public beneficiario;
    uint public tempoFinal;
    bool public leilaoAtivo;
    Lance public maiorLance;
    mapping(address => uint) public lances;

    event NovaOferta(address produtor, uint quantidade, uint precoMinimoPorKwh);
    event NovoLance(address comprador, uint valor);
    event LeilaoFinalizado(address vencedor, uint valor);
    event LancesRestituidos(address comprador, uint valor);

    modifier apenasAntesDoFinal() {
        require(block.timestamp < tempoFinal, "Leilao ja terminou");
        _;
    }

    modifier apenasDepoisDoFinal() {
        require(block.timestamp >= tempoFinal, "Leilao ainda nao terminou");
        _;
    }

    constructor(uint _duracaoLeilaoEmMinutos, address payable _beneficiario) {
        require(_beneficiario != address(0), "Beneficiario invalido");

        tempoFinal = block.timestamp + (_duracaoLeilaoEmMinutos * 1 minutes);
        beneficiario = _beneficiario;
        leilaoAtivo = true;

    }

    function fazerLance() public payable apenasAntesDoFinal {
        require(msg.value > maiorLance.valor, "Lance deve ser maior que o atual maior lance");
        require(msg.value >= oferta.precoMinimoPorKwhEmReais * 1 ether / etherToReais, "Lance abaixo do preco minimo");

        if (maiorLance.comprador != address(0)) {
            lances[maiorLance.comprador] += maiorLance.valor;
        }

        maiorLance = Lance(payable(msg.sender), msg.value);

        emit NovoLance(msg.sender, msg.value);
    }

    function finalizarLeilao() public apenasDepoisDoFinal {
        require(leilaoAtivo, "Leilao ja foi finalizado");
        leilaoAtivo = false;

        if (maiorLance.comprador != address(0)) {
            beneficiario.transfer(maiorLance.valor);
            emit LeilaoFinalizado(maiorLance.comprador, maiorLance.valor);
        } else {
            emit LeilaoFinalizado(address(0), 0);
        }
    }

    function retirarLance() public {
        uint valor = lances[msg.sender];
        require(valor > 0, "Nao ha fundos para retirar");

        lances[msg.sender] = 0;
        payable(msg.sender).transfer(valor);

        emit LancesRestituidos(msg.sender, valor);
    }

    function melhorLance() public view returns (address comprador, uint valor) {
        return (maiorLance.comprador, maiorLance.valor);
    }

    uint public etherToReais = 500; // Fator de conversão de ETH para Reais (por exemplo, 1 ETH = 500 Reais)
}
