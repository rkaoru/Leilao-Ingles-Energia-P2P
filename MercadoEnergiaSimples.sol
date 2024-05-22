// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract MercadoEnergiaSimples {
    // Define the state variables
    uint256 public constant GAS_LIMIT = 6721975;
    uint256 public constant GAS_PRICE = 20;

    address public owner;
    mapping(address => bool) public participants;
    uint256 public totalSupply;
    uint256 public totalDemand;

    // Define the constructor
    constructor() {
    owner = msg.sender;
}

    // Define the modifier functions
    modifier onlyOwner() {
        require(msg.sender == owner, "Only the contract owner can call this function.");
        _;
    }

    modifier notParticipant() {
        require(!participants[msg.sender], "The sender is already a participant.");
        _;
    }

    // Define the public functions
    function register() public payable notParticipant {
        participants[msg.sender] = true;
    }

    function deregister() public onlyOwner notParticipant {
        delete participants[msg.sender];
    }

    function getParticipant(address _address) public view returns (bool) {
        return participants[_address];
    }

    function getTotalSupply() public view returns (uint256) {
        uint256 supply = 0;
        for (uint256 i = 0; i < addressArray.length; i++) {
            if (participants[addressArray[i]]) {
                supply += 1;
            }
        }
        return supply;
    }

    function getTotalDemand() public view returns (uint256) {
        uint256 demand = 0;
        for (uint256 i = 0; i < orders.length; i++) {
            demand += orders[i].quantity;
        }
        return demand;
    }

    // Define the private functions
    struct Order {
        address buyer;
        uint256 quantity;
        uint256 price;
    }

    Order[] private orders;

    address[] private addressArray;

    function addOrder(address _buyer, uint256 _quantity, uint256 _price) private {
        orders.push(Order({buyer: _buyer, quantity: _quantity, price: _price}));
        addressArray.push(_buyer);
    }

    function executeOrders() private {
        uint256 localTotalSupply = getTotalSupply();
        uint256 localTotalDemand = getTotalDemand();
        uint256 price = 0;
        for (uint256 i = 0; i < orders.length; i++) {
            if (localTotalSupply > orders[i].quantity) {
                localTotalSupply -= orders[i].quantity;
                payable(orders[i].buyer).transfer(orders[i].price * orders[i].quantity);
                price = orders[i].price;
                delete orders[i];
            } else {
                uint256 remainingDemand = localTotalDemand - orders[i].quantity;
                orders[i].quantity = remainingDemand;
                payable(msg.sender).transfer(price * remainingDemand);
                localTotalDemand -= remainingDemand;
                delete orders[i];
                for (uint256 j = i; j < orders.length - 1; j++) {
                    orders[j] = orders[j + 1];
                }
                i--;
            }
        }
        totalSupply = localTotalSupply;
        totalDemand = localTotalDemand;
    }

    // Define the fallback function
    fallback() external payable {
        addOrder(msg.sender,msg.value, gasleft() / GAS_PRICE);
        if (getTotalSupply() + 1 > GAS_LIMIT / GAS_PRICE) {
            executeOrders();
        }
    }

    // Define the receive ether function
    receive() external payable {
        // Do nothing
    }
}