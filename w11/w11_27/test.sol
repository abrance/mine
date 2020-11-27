pragma solidity ^0.4.0


contract DynamicString{

    string name = "xiaoY";
    string _n = "小歪";

    function getLength() view returns(uint)
    {
	// 强转后可以有length属性, 可以看到占用空间情况
	return bytes(name).length;
    }

    function pay() payable
    {
	// payable 
    }

    function get_balance() returns(uint)
    {
	return this.balance;
    }
}