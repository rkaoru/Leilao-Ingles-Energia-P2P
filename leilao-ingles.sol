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
    address[] public participantes;

    event NovaOferta(address produtor, uint quantidade, uint precoMinimoPorKwh);
    event NovoLance(address comprador, uint valor);
    event LeilaoFinalizado(address vencedor, uint valor);
    event LancesRestituidos(address comprador, uint valor);

    modifier apenasAntesDoFinal() {
        require(block.timestamp < tempoFinal, "Leilao ja terminou");
        _;
    }

    modifier apenasBeneficiario() {
        require(msg.sender == beneficiario, "Apenas o beneficiario pode finalizar o leilao");
        _;
    }

    constructor(uint _duracaoLeilaoEmMinutos, address payable _beneficiario) {
        require(_beneficiario != address(0), "Beneficiario invalido");

        tempoFinal = block.timestamp + (_duracaoLeilaoEmMinutos * 1 minutes);
        beneficiario = _beneficiario;
        leilaoAtivo = true;
    }

    function tempoFinalLeilao() public view returns (uint) {
        return tempoFinal;
    }

    function definirOferta(address payable _produtor, uint _quantidadeDisponivel, uint _precoMinimoPorKwhEmReais) public {
        oferta = Oferta({
            produtor: _produtor,
            quantidadeDisponivel: _quantidadeDisponivel,
            precoMinimoPorKwhEmReais: _precoMinimoPorKwhEmReais,
            ativa: true
        });

        emit NovaOferta(_produtor, _quantidadeDisponivel, _precoMinimoPorKwhEmReais);
    }

    function fazerLance() public payable apenasAntesDoFinal {
        if (block.timestamp >= tempoFinal) {
            finalizarLeilaoAutomaticamente();
            return;
        }

        require(msg.value > maiorLance.valor, "Lance deve ser maior que o atual maior lance");
        require(msg.value >= oferta.precoMinimoPorKwhEmReais * 1 ether / etherToReais, "Lance abaixo do preco minimo");

        if (maiorLance.comprador != address(0)) {
            lances[maiorLance.comprador] += maiorLance.valor;
        }

        if (lances[msg.sender] == 0) {
            participantes.push(msg.sender);
        }

        maiorLance = Lance(payable(msg.sender), msg.value);

        emit NovoLance(msg.sender, msg.value);
    }

    function finalizarLeilao() public apenasBeneficiario {
        require(leilaoAtivo, "Leilao ja foi finalizado");
        leilaoAtivo = false;

        // Transferir valor do maior lance para o beneficiario
        if (maiorLance.comprador != address(0)) {
            beneficiario.transfer(maiorLance.valor);
            emit LeilaoFinalizado(maiorLance.comprador, maiorLance.valor);
        } else {
            emit LeilaoFinalizado(address(0), 0);
        }

        // Restituir lances para todos os participantes exceto o vencedor
        for (uint i = 0; i < participantes.length; i++) {
            address addr = participantes[i];
            uint valor = lances[addr];
            if (addr != maiorLance.comprador && valor > 0) {
                lances[addr] = 0;
                payable(addr).transfer(valor);
                emit LancesRestituidos(addr, valor);
            }
        }
    }

    function finalizarLeilaoAutomaticamente() private {
        require(block.timestamp >= tempoFinal, "Leilao ainda nao terminou");

        leilaoAtivo = false;

        // Transferir valor do maior lance para o beneficiario
        if (maiorLance.comprador != address(0)) {
            beneficiario.transfer(maiorLance.valor);
            emit LeilaoFinalizado(maiorLance.comprador, maiorLance.valor);
        } else {
            emit LeilaoFinalizado(address(0), 0);
        }

        // Restituir lances para todos os participantes exceto o vencedor
        for (uint i = 0; i < participantes.length; i++) {
            address addr = participantes[i];
            uint valor = lances[addr];
            if (addr != maiorLance.comprador && valor > 0) {
                lances[addr] = 0;
                payable(addr).transfer(valor);
                emit LancesRestituidos(addr, valor);
            }
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