// SPDX-License-Identifier: MIT

pragma solidity ^0.7.0;

// 导包
import "../@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "../@openzeppelin/contracts/math/SafeMath.sol";
import "../@openzeppelin/contracts/utils/Address.sol";
import "../@openzeppelin/contracts/token/ERC20/SafeERC20.sol";

import "../../interfaces/yearn/IProxy.sol";
import "../../interfaces/curve/Mintr.sol";

contract StrategyProxy {
    // 扩展这些类型
    using SafeERC20 for IERC20;
    using Address for address;
    using SafeMath for uint256;

    // 初始化值
    IProxy public constant proxy = IProxy(0xF147b8125d2ef93FB6965Db97D6746952a133934);
    address public constant mintr = address(0xd061D61a4d941c39E5453435B6345Dc261C2fcE0);
    address public constant crv = address(0xD533a949740bb3306d119CC777fa900bA034cd52);
    address public constant gauge = address(0x2F50D538606Fa9EDD2B11E2446BEb18C9D5846bB);
    address public constant y = address(0xFA712EE4788C042e2B7BB55E6cb8ec569C4530c1);

    mapping(address => bool) public strategies;
    address public governance;

    // 构造函数 对 governance 赋值
    constructor() public {
        governance = msg.sender;
    }

    // 声明需要交互对象本人（合约）
    function setGovernance(address _governance) external {
        require(msg.sender == governance, "!governance");
        governance = _governance;
    }

    // 在mapping 里增加 _strategy, true 的映射关系
    function approveStrategy(address _strategy) external {
        require(msg.sender == governance, "!governance");
        strategies[_strategy] = true;
    }

    // 将mapping 中的 _strategy映射置为 false
    function revokeStrategy(address _strategy) external {
        require(msg.sender == governance, "!governance");
        strategies[_strategy] = false;
    }

    // proxy 拥有的代币数量
    function lock() external {
        uint256 amount = IERC20(crv).balanceOf(address(proxy));
        if (amount > 0) proxy.increaseAmount(amount);
    }

    // 在strategies里映射为true的对象，proxy 回调 参数为_gauge, _amount 的vote_for_gauge_weights函数
    function vote(address _gauge, uint256 _amount) public {
        require(strategies[msg.sender], "!strategy");
        proxy.execute(gauge, 0, abi.encodeWithSignature("vote_for_gauge_weights(address,uint256)", _gauge, _amount));
    }

    // 在strategies里映射为true的对象，返还 数量为_amount的代币
    function withdraw(
        address _gauge,
        address _token,
        uint256 _amount
    ) public returns (uint256) {
        require(strategies[msg.sender], "!strategy");
        uint256 _before = IERC20(_token).balanceOf(address(proxy));
        proxy.execute(_gauge, 0, abi.encodeWithSignature("withdraw(uint256)", _amount));     // 计算花费由 proxy 承担
        uint256 _after = IERC20(_token).balanceOf(address(proxy));
        uint256 _net = _after.sub(_before);
        proxy.execute(_token, 0, abi.encodeWithSignature("transfer(address,uint256)", msg.sender, _net));
        return _net;
    }

    // 返回 proxy 账户代币数量
    function balanceOf(address _gauge) public view returns (uint256) {
        return IERC20(_gauge).balanceOf(address(proxy));
    }

    // 调用withdraw，返还_gauge 对象的 账户金额
    function withdrawAll(address _gauge, address _token) external returns (uint256) {
        require(strategies[msg.sender], "!strategy");
        return withdraw(_gauge, _token, balanceOf(_gauge));
    }

    // _gauge 向proxy 转账
    function deposit(address _gauge, address _token) external {
        require(strategies[msg.sender], "!strategy");
        uint256 _balance = IERC20(_token).balanceOf(address(this));
        IERC20(_token).safeTransfer(address(proxy), _balance);
        _balance = IERC20(_token).balanceOf(address(proxy));

        proxy.execute(_token, 0, abi.encodeWithSignature("approve(address,uint256)", _gauge, 0));
        proxy.execute(_token, 0, abi.encodeWithSignature("approve(address,uint256)", _gauge, _balance));
        (bool success, ) = proxy.execute(_gauge, 0, abi.encodeWithSignature("deposit(uint256)", _balance));
        if (!success) assert(false);
    }

    // 给proxy 发放津贴
    function harvest(address _gauge) external {
        require(strategies[msg.sender], "!strategy");
        uint256 _before = IERC20(crv).balanceOf(address(proxy));
        proxy.execute(mintr, 0, abi.encodeWithSignature("mint(address)", _gauge));
        uint256 _after = IERC20(crv).balanceOf(address(proxy));
        uint256 _balance = _after.sub(_before);
        proxy.execute(crv, 0, abi.encodeWithSignature("transfer(address,uint256)", msg.sender, _balance));
    }
}
