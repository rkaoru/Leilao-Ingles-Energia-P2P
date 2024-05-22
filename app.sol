// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract MercadoEnergia {
    struct Oferta {
        address produtor;
        uint quantidadeDisponivel;
        uint precoMinimoPorKwhEmReais;
        bool ativa;
    }

    Oferta[] public ofertas;
    address public comprador;
    uint public quantidadeComprada;
    uint public precoTotal;
    uint public etherToReais = 500; // Fator de conversão de ETH para Reais (por exemplo, 1 ETH = 500 Reais)

    event NovaOferta(address produtor, uint quantidade, uint precoMinimoPorKwh);
    event NovaProposta(address comprador, uint quantidade, uint preco);
    event CompraEfetuada(address comprador, uint quantidade, uint preco);

    // Função para cadastrar oferta de energia
    function cadastrarOferta(uint _quantidadeDisponivel, uint _precoMinimoPorKwhEmReais) public {
        require(_quantidadeDisponivel > 0, "Quantidade deve ser maior que zero");
        require(_precoMinimoPorKwhEmReais > 0, "Preco deve ser maior que zero");

        ofertas.push(Oferta(msg.sender, _quantidadeDisponivel, _precoMinimoPorKwhEmReais, true));
        emit NovaOferta(msg.sender, _quantidadeDisponivel, _precoMinimoPorKwhEmReais);
    }

    // Função para fazer proposta de compra
    function fazerProposta(uint _quantidadeDesejada, uint _precoOferecidoEmReais) public {
        uint melhorOfertaIndex = _encontrarMelhorOferta(_quantidadeDesejada);
        Oferta storage melhorOferta = ofertas[melhorOfertaIndex];

        require(melhorOferta.ativa, "Nenhuma oferta disponivel");
        require(_quantidadeDesejada <= melhorOferta.quantidadeDisponivel, "Quantidade desejada excede oferta disponivel");
        require(_precoOferecidoEmReais >= melhorOferta.precoMinimoPorKwhEmReais, "Preco oferecido abaixo do minimo");

        quantidadeComprada = _quantidadeDesejada;
        // Converte o valor oferecido em reais para wei
        precoTotal = (_precoOferecidoEmReais * etherToReais) / 1 ether; // Convertendo para wei
        comprador = msg.sender;

        emit NovaProposta(msg.sender, quantidadeComprada, precoTotal);
    }

    // Função para finalizar a compra
    function finalizarCompra() public payable {
        require(msg.sender == comprador, "Apenas o comprador pode finalizar a compra");
        require(msg.value >= precoTotal, "Valor insuficiente");

        payable(ofertas[_encontrarMelhorOferta(quantidadeComprada)].produtor).transfer(precoTotal);
        comprador = address(0);
        quantidadeComprada = 0;
        precoTotal = 0;

        emit CompraEfetuada(msg.sender, quantidadeComprada, precoTotal);
    }

    // Função interna para encontrar a melhor oferta
    function encontrarMelhorOferta(uint _quantidadeDesejada) public view returns (address produtor, uint quantidadeDisponivel, uint precoMinimoPorKwhEmReais, bool ativa) {
        uint melhorIndex = 0;
        uint melhorPreco = type(uint).max;

        for (uint i = 0; i < ofertas.length; i++) {
            if (ofertas[i].ativa && ofertas[i].quantidadeDisponivel >= _quantidadeDesejada && ofertas[i].precoMinimoPorKwhEmReais < melhorPreco) {
                melhorIndex = i;
                melhorPreco = ofertas[i].precoMinimoPorKwhEmReais;
            }
        }

        Oferta storage melhorOferta = ofertas[melhorIndex];
        return (melhorOferta.produtor, melhorOferta.quantidadeDisponivel, melhorOferta.precoMinimoPorKwhEmReais, melhorOferta.ativa);
    }
}